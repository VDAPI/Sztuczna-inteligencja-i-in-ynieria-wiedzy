import csv
import os
from datetime import datetime, date


def parse_time(hms: str) -> int:
    h, m, s = hms.strip().split(":")
    return int(h) * 3600 + int(m) * 60 + int(s)


def format_time(seconds: int) -> str:
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def format_duration(seconds: int) -> str:
    h = seconds // 3600
    m = (seconds % 3600) // 60
    if h > 0:
        return f"{h}h {m}min"
    return f"{m}min"


def normalize_name(name: str) -> str:
    replacements = {
        "ą": "a", "ć": "c", "ę": "e", "ł": "l", "ń": "n",
        "ó": "o", "ś": "s", "ź": "z", "ż": "z",
    }
    result = name.lower().strip()
    for pl, ascii_char in replacements.items():
        result = result.replace(pl, ascii_char)
    return result


def read_csv(filepath: str) -> list[dict]:
    rows = []
    with open(filepath, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cleaned = {k.strip(): v.strip() for k, v in row.items()}
            rows.append(cleaned)
    return rows


class GTFSData:
    def __init__(self, gtfs_dir: str):
        self.gtfs_dir = gtfs_dir
        self.stops = {}
        self.routes = {}
        self.trips = {}
        self.stop_times = {}
        self.calendars = {}
        self.cal_exceptions = {}
        self.station_platforms = {} 
        self.name_to_stop_ids = {}  

        self._load_all()
        self._build_lookups()

    def _load_all(self):
        self._load_stops()
        self._load_routes()
        self._load_trips()
        self._load_stop_times()
        self._load_calendars()
        self._load_calendar_dates()

        total_st = sum(len(v) for v in self.stop_times.values())
        print(f"Zaladowano: {len(self.stops)} przystankow, {len(self.routes)} tras, "
              f"{len(self.trips)} kursow, {total_st} stop_times", flush=True)

    def _load_stops(self):
        for row in read_csv(os.path.join(self.gtfs_dir, "stops.txt")):
            sid = row["stop_id"]
            lt = int(row["location_type"]) if row["location_type"] else 0
            self.stops[sid] = {
                "stop_id": sid,
                "stop_name": row["stop_name"],
                "lat": float(row["stop_lat"]),
                "lon": float(row["stop_lon"]),
                "location_type": lt,
                "parent_station": row.get("parent_station", ""),
                "platform_code": row.get("platform_code", ""),
            }

    def _load_routes(self):
        for row in read_csv(os.path.join(self.gtfs_dir, "routes.txt")):
            rid = row["route_id"]
            short = row.get("route_short_name", "")
            long = row.get("route_long_name", "")
            self.routes[rid] = {
                "route_id": rid,
                "short_name": short,
                "long_name": long,
                "display_name": short if short else long,
            }

    def _load_trips(self):
        for row in read_csv(os.path.join(self.gtfs_dir, "trips.txt")):
            tid = row["trip_id"]
            self.trips[tid] = {
                "trip_id": tid,
                "route_id": row["route_id"],
                "service_id": row["service_id"],
                "headsign": row.get("trip_headsign", ""),
            }

    def _load_stop_times(self):
        for row in read_csv(os.path.join(self.gtfs_dir, "stop_times.txt")):
            tid = row["trip_id"]
            pt = int(row["pickup_type"]) if row["pickup_type"] else 0
            entry = {
                "trip_id": tid,
                "arrival": parse_time(row["arrival_time"]),
                "departure": parse_time(row["departure_time"]),
                "stop_id": row["stop_id"],
                "sequence": int(row["stop_sequence"]),
                "pickup_type": pt,
            }
            if tid not in self.stop_times:
                self.stop_times[tid] = []
            self.stop_times[tid].append(entry)

        for tid in self.stop_times:
            self.stop_times[tid].sort(key=lambda x: x["sequence"])

    def _load_calendars(self):
        day_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for row in read_csv(os.path.join(self.gtfs_dir, "calendar.txt")):
            sid = row["service_id"]
            days = [row[d] == "1" for d in day_names]
            self.calendars[sid] = {
                "service_id": sid,
                "days": days,  # [pon, wt, sr, czw, pt, sob, niedz]
                "start_date": row["start_date"],
                "end_date": row["end_date"],
            }

    def _load_calendar_dates(self):
        for row in read_csv(os.path.join(self.gtfs_dir, "calendar_dates.txt")):
            sid = row["service_id"]
            if sid not in self.cal_exceptions:
                self.cal_exceptions[sid] = []
            self.cal_exceptions[sid].append({
                "date": row["date"],
                "exception_type": int(row["exception_type"]),
            })

    def _build_lookups(self):
        for stop in self.stops.values():
            station_id = self.get_station_id(stop["stop_id"])
            if station_id not in self.station_platforms:
                self.station_platforms[station_id] = []
            self.station_platforms[station_id].append(stop["stop_id"])

        for stop in self.stops.values():
            norm = normalize_name(stop["stop_name"])
            if norm not in self.name_to_stop_ids:
                self.name_to_stop_ids[norm] = set()
            self.name_to_stop_ids[norm].add(stop["stop_id"])

    def get_station_id(self, stop_id: str) -> str:
        """Zwróć ID stacji nadrzędnej (lub własne ID jeśli to stacja)."""
        stop = self.stops.get(stop_id)
        if not stop:
            return stop_id
        parent = stop["parent_station"]
        return parent if parent else stop_id

    def is_service_active(self, service_id: str, query_date: date) -> bool:
        """
        Sprawdź czy dany service jest aktywny w danym dniu.
        
        1. Sprawdź calendar.txt (tygodniowy wzorzec)
        2. Nadpisz wyjątkami z calendar_dates.txt
        """
        active = False

        # Krok 1: calendar.txt
        cal = self.calendars.get(service_id)
        if cal:
            start = datetime.strptime(cal["start_date"], "%Y%m%d").date()
            end = datetime.strptime(cal["end_date"], "%Y%m%d").date()
            if start <= query_date <= end:
                # weekday(): 0=poniedziałek, 6=niedziela
                active = cal["days"][query_date.weekday()]

        # Krok 2: wyjątki nadpisują
        exceptions = self.cal_exceptions.get(service_id, [])
        date_str = query_date.strftime("%Y%m%d")
        for ex in exceptions:
            if ex["date"] == date_str:
                active = (ex["exception_type"] == 1)  # 1=dodany, 2=usunięty

        return active

    def get_stop_ids_for_name(self, name: str) -> set:
        """Znajdź stop_id-ki pasujące do nazwy przystanku."""
        norm = normalize_name(name)

        # Dokładne dopasowanie
        if norm in self.name_to_stop_ids:
            return self.name_to_stop_ids[norm]

        # Częściowe dopasowanie
        for key, ids in self.name_to_stop_ids.items():
            if norm in key or key in norm:
                return ids

        return set()

    def get_route_name(self, trip_id: str) -> str:
        """Zwróć nazwę linii dla danego tripu (np. "D6")."""
        trip = self.trips.get(trip_id)
        if not trip:
            return "?"
        route = self.routes.get(trip["route_id"])
        if not route:
            return "?"
        return route["display_name"]

    def get_stop_name(self, stop_id: str) -> str:
        """Zwróć nazwę przystanku."""
        stop = self.stops.get(stop_id)
        return stop["stop_name"] if stop else stop_id
