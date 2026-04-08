from bisect import bisect_left
from datetime import date
from parser import GTFSData

# Indeksy krotek połączeń w grafie
FROM_STOP = 0
TO_STOP = 1
DEPARTURE = 2
ARRIVAL = 3
TRIP_ID = 4
ROUTE_NAME = 5
FROM_NAME = 6
TO_NAME = 7


def build_graph(data: GTFSData, query_date: date) -> dict:
    """Buduje graf połączeń dla danej daty. Zwraca dict: stop_id -> lista połączeń posortowana po czasie odjazdu."""
    departures = {}
    total = 0

    for trip_id, stop_times_list in data.stop_times.items():
        trip = data.trips.get(trip_id)
        if not trip:
            continue
        if not data.is_service_active(trip["service_id"], query_date):
            continue

        route_name = data.get_route_name(trip_id)

        for i in range(len(stop_times_list) - 1):
            curr = stop_times_list[i]
            nxt = stop_times_list[i + 1]

            if curr["pickup_type"] != 0:
                continue

            conn = (
                curr["stop_id"],
                nxt["stop_id"],
                curr["departure"],
                nxt["arrival"],
                trip_id,
                route_name,
                data.get_stop_name(curr["stop_id"]),
                data.get_stop_name(nxt["stop_id"]),
            )

            if curr["stop_id"] not in departures:
                departures[curr["stop_id"]] = []
            departures[curr["stop_id"]].append(conn)
            total += 1

    for stop_id in departures:
        departures[stop_id].sort(key=lambda c: c[DEPARTURE])

    print(f"Graf: {len(departures)} przystankow z odjazdami, {total} polaczen")
    return departures


def get_departures_after(departures: dict, stop_id: str, after_time: int) -> list:
    """Zwraca połączenia z przystanku odjeżdżające od after_time wzwyż (binary search O(log n))."""
    conns = departures.get(stop_id, [])
    if not conns:
        return []

    idx = bisect_left([c[DEPARTURE] for c in conns], after_time)
    return conns[idx:]


def get_sibling_platforms(data: GTFSData, stop_id: str) -> list:
    """Zwraca listę peronów tej samej stacji (włącznie z podanym)."""
    station_id = data.get_station_id(stop_id)
    return data.station_platforms.get(station_id, [stop_id])
