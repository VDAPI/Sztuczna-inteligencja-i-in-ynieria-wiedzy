from bisect import bisect_left
from datetime import date
from parser import GTFSData

FROM_STOP = 0
TO_STOP = 1
DEPARTURE = 2
ARRIVAL = 3
TRIP_ID = 4
ROUTE_NAME = 5
FROM_NAME = 6
TO_NAME = 7


def build_graph(data: GTFSData, query_date: date) -> dict:
    """
    Zbuduj graf dla konkretnej daty.
    
    Zwraca dict: stop_id -> lista połączeń posortowana po czasie odjazdu.
    Każde połączenie to tuple:
        (from_stop_id, to_stop_id, departure_sec, arrival_sec, 
         trip_id, route_name, from_stop_name, to_stop_name)
    """
    departures = {}  # stop_id -> [connection, ...]
    total = 0

    for trip_id, stop_times_list in data.stop_times.items():
        # Sprawdź czy ten kurs jest aktywny w danym dniu
        trip = data.trips.get(trip_id)
        if not trip:
            continue
        if not data.is_service_active(trip["service_id"], query_date):
            continue

        route_name = data.get_route_name(trip_id)

        # Twórz połączenia między kolejnymi przystankami
        for i in range(len(stop_times_list) - 1):
            curr = stop_times_list[i]
            nxt = stop_times_list[i + 1]

            # Pomijamy jeśli nie można wsiąść (pickup_type != 0)
            if curr["pickup_type"] != 0:
                continue

            conn = (
                curr["stop_id"],            # FROM_STOP
                nxt["stop_id"],             # TO_STOP
                curr["departure"],          # DEPARTURE
                nxt["arrival"],             # ARRIVAL
                trip_id,                    # TRIP_ID
                route_name,                 # ROUTE_NAME
                data.get_stop_name(curr["stop_id"]),  # FROM_NAME
                data.get_stop_name(nxt["stop_id"]),    # TO_NAME
            )

            if curr["stop_id"] not in departures:
                departures[curr["stop_id"]] = []
            departures[curr["stop_id"]].append(conn)
            total += 1

    # Posortuj odjazdy z każdego przystanku po czasie odjazdu
    for stop_id in departures:
        departures[stop_id].sort(key=lambda c: c[DEPARTURE])

    print(f"Graf: {len(departures)} przystankow z odjazdami, {total} polaczen")
    return departures


def get_departures_after(departures: dict, stop_id: str, after_time: int) -> list:
    """
    Znajdź połączenia z przystanku odjeżdżające o after_time lub później.
    Używa binary search (bisect) - O(log n) zamiast O(n).
    """
    conns = departures.get(stop_id, [])
    if not conns:
        return []

    # Binary search: znajdź indeks pierwszego odjazdu >= after_time
    # Tworzymy listę samych czasów odjazdu do bisect
    idx = bisect_left([c[DEPARTURE] for c in conns], after_time)
    return conns[idx:]


def get_sibling_platforms(data: GTFSData, stop_id: str) -> list:
    """Zwróć listę peronów tej samej stacji (włącznie z podanym)."""
    station_id = data.get_station_id(stop_id)
    return data.station_platforms.get(station_id, [stop_id])
