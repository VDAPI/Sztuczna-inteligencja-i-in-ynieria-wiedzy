import heapq
import math
from graph import (
    get_departures_after, get_sibling_platforms,
    FROM_STOP, TO_STOP, DEPARTURE, ARRIVAL, TRIP_ID, ROUTE_NAME, FROM_NAME, TO_NAME,
)
from parser import GTFSData, format_time, format_duration


def zero_heuristic(stop_id):
    """h(n) = 0 — zamienia A* w Dijkstrę."""
    return 0


def make_haversine_heuristic(data: GTFSData, goal_stop_ids: set):
    """Tworzy heurystykę czasową: odległość haversine do celu / maks. prędkość. Admissible."""
    MAX_SPEED_KMH = 160.0
    EARTH_R = 6371.0

    lats, lons = [], []
    for sid in goal_stop_ids:
        stop = data.stops.get(sid)
        if stop:
            lats.append(stop["lat"])
            lons.append(stop["lon"])
    goal_lat = sum(lats) / len(lats) if lats else 0
    goal_lon = sum(lons) / len(lons) if lons else 0

    def heuristic(stop_id):
        stop = data.stops.get(stop_id)
        if not stop:
            return 0
        lat1, lon1 = math.radians(stop["lat"]), math.radians(stop["lon"])
        lat2, lon2 = math.radians(goal_lat), math.radians(goal_lon)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        dist_km = EARTH_R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return int(dist_km / MAX_SPEED_KMH * 3600)

    return heuristic


def make_transfer_heuristic(data: GTFSData, goal_stop_ids: set):
    """Heurystyka przesiadkowa: h=0 jeśli istnieje bezpośredni kurs do celu, h=1 w p.p. Admissible."""
    goal_stations = set()
    for gid in goal_stop_ids:
        goal_stations.add(data.get_station_id(gid))

    # Zbiór przystanków z bezpośrednim kursem do stacji docelowej
    direct_stops = set()
    for trip_id, st_list in data.stop_times.items():
        hits_goal = False
        for st in st_list:
            if data.get_station_id(st["stop_id"]) in goal_stations:
                hits_goal = True
                break
        if hits_goal:
            for st in st_list:
                if data.get_station_id(st["stop_id"]) in goal_stations:
                    break
                direct_stops.add(st["stop_id"])

    def heuristic(stop_id):
        if stop_id in goal_stop_ids:
            return 0
        return 0 if stop_id in direct_stops else 1

    return heuristic


def find_path(data, departures, start_ids, end_ids, start_time, criterion, heuristic):
    goal_stations = set()
    for gid in end_ids:
        goal_stations.add(data.get_station_id(gid))

    # Kolejka: (f_cost, counter, state)
    # state = (stop_id, current_time, g_cost, transfers, last_trip_id, parent_idx, last_conn)
    counter = 0
    pq = []
    states = []
    best = {}

    for sid in start_ids:
        h = heuristic(sid)
        state = (sid, start_time, 0, 0, None, -1, None)
        heapq.heappush(pq, (0 + h, counter, state))
        counter += 1

    nodes_expanded = 0

    while pq:
        f_cost, _, state = heapq.heappop(pq)
        stop_id, cur_time, g_cost, transfers, last_trip, parent_idx, last_conn = state

        if data.get_station_id(stop_id) in goal_stations:
            path = _reconstruct(states, parent_idx, last_conn)
            segments = _build_segments(path)
            stats = {
                "total_time": cur_time - start_time,
                "transfers": transfers,
                "nodes_expanded": nodes_expanded,
                "arrival_time": cur_time,
            }
            return segments, stats

        if criterion == "transfers":
            key = (stop_id, last_trip)
        else:
            key = stop_id

        if key in best and best[key] <= g_cost:
            continue
        best[key] = g_cost
        nodes_expanded += 1

        state_idx = len(states)
        states.append(state)

        # Rozwiń: odjazdy z bieżącego przystanku
        conns = get_departures_after(departures, stop_id, cur_time)
        seen_trip = None
        count = 0

        for conn in conns:
            if conn[DEPARTURE] - cur_time > 4 * 3600:
                break
            if count >= 500:
                break

            if conn[TRIP_ID] == seen_trip:
                continue
            seen_trip = conn[TRIP_ID]
            count += 1

            is_transfer = (last_trip is not None and last_trip != conn[TRIP_ID])
            new_transfers = transfers + (1 if is_transfer else 0)
            new_time = conn[ARRIVAL]

            if criterion == "time":
                new_g = new_time - start_time
            else:
                new_g = new_transfers

            h = heuristic(conn[TO_STOP])
            new_f = new_g + h

            if criterion == "transfers":
                new_key = (conn[TO_STOP], conn[TRIP_ID])
            else:
                new_key = conn[TO_STOP]
            if new_key in best and best[new_key] <= new_g:
                continue

            new_state = (conn[TO_STOP], new_time, new_g, new_transfers,
                         conn[TRIP_ID], state_idx, conn)
            heapq.heappush(pq, (new_f, counter, new_state))
            counter += 1

        # Rozwiń: przejście na inny peron tej samej stacji (koszt 0)
        for platform_id in get_sibling_platforms(data, stop_id):
            if platform_id == stop_id:
                continue

            h = heuristic(platform_id)
            new_f = g_cost + h

            if criterion == "transfers":
                new_key = (platform_id, last_trip)
            else:
                new_key = platform_id
            if new_key in best and best[new_key] <= g_cost:
                continue

            new_state = (platform_id, cur_time, g_cost, transfers,
                         last_trip, state_idx, None)
            heapq.heappush(pq, (new_f, counter, new_state))
            counter += 1

    return None, {"nodes_expanded": nodes_expanded}


def _reconstruct(states, parent_idx, last_conn):
    """Odtwarza listę połączeń od startu do celu przechodząc po parent_idx."""
    path = []
    if last_conn is not None:
        path.append(last_conn)

    idx = parent_idx
    while idx >= 0:
        state = states[idx]
        conn = state[6]
        if conn is not None:
            path.append(conn)
        idx = state[5]

    path.reverse()
    return path


def _build_segments(path):
    """Łączy kolejne połączenia na tym samym tripie w jeden segment (np. 15 przystanków -> 1 segment)."""
    if not path:
        return []

    segments = []
    cur_trip = path[0][TRIP_ID]
    seg_from = path[0][FROM_NAME]
    seg_dep = path[0][DEPARTURE]
    seg_to = path[0][TO_NAME]
    seg_arr = path[0][ARRIVAL]
    seg_route = path[0][ROUTE_NAME]

    for i in range(1, len(path)):
        conn = path[i]
        if conn[TRIP_ID] == cur_trip:
            seg_to = conn[TO_NAME]
            seg_arr = conn[ARRIVAL]
        else:
            segments.append({
                "from": seg_from, "to": seg_to, "route": seg_route,
                "departure": seg_dep, "arrival": seg_arr,
            })
            cur_trip = conn[TRIP_ID]
            seg_from = conn[FROM_NAME]
            seg_dep = conn[DEPARTURE]
            seg_to = conn[TO_NAME]
            seg_arr = conn[ARRIVAL]
            seg_route = conn[ROUTE_NAME]

    segments.append({
        "from": seg_from, "to": seg_to, "route": seg_route,
        "departure": seg_dep, "arrival": seg_arr,
    })

    return segments


def print_result(segments, stats, start_time, criterion):
    """Wypisuje wynik: stdout = trasa, stderr = podsumowanie."""
    import sys

    for i, seg in enumerate(segments):
        print(f"{seg['from']} | {seg['to']} | {seg['route']} | "
              f"{format_time(seg['departure'])} | {format_time(seg['arrival'])}")

        if i < len(segments) - 1:
            next_seg = segments[i + 1]
            wait = next_seg["departure"] - seg["arrival"]
            if wait > 0:
                print(f"  --- Przesiadka ({format_duration(wait)} oczekiwania) ---")

    print("--- Wynik ---", file=sys.stderr)
    if criterion == "time":
        print(f"Kryterium: czas przejazdu", file=sys.stderr)
        print(f"Calkowity czas: {format_duration(stats['total_time'])} ({stats['total_time']} sek.)", file=sys.stderr)
    else:
        print(f"Kryterium: liczba przesiadek", file=sys.stderr)
        print(f"Calkowity czas: {format_duration(stats['total_time'])}", file=sys.stderr)
    print(f"Przesiadki: {stats['transfers']}", file=sys.stderr)
    print(f"Czas obliczen: {stats.get('elapsed_ms', '?')} ms", file=sys.stderr)
    print(f"Wezly rozwiniete: {stats['nodes_expanded']}", file=sys.stderr)
