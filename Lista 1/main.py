import sys
import os
import time
from datetime import date

from parser import GTFSData, parse_time, format_time, format_duration
from graph import build_graph
from pathfinder import (
    find_path, print_result,
    zero_heuristic, make_haversine_heuristic, make_transfer_heuristic,
)
from tsp import TSPSolver


DEFAULT_DATE = "2026-03-10"


def find_gtfs_dir():
    """Szuka katalogu z danymi GTFS w kilku typowych lokalizacjach."""
    candidates = [
        "data/google_transit",
        "google_transit",
        "../data/google_transit",
        "../Lista_1/data/google_transit",
    ]
    for c in candidates:
        if os.path.exists(os.path.join(c, "stops.txt")):
            return c
    print("Nie znaleziono katalogu z danymi GTFS!", file=sys.stderr)
    print("Oczekiwany: data/google_transit/ z plikami stops.txt, routes.txt, ...", file=sys.stderr)
    sys.exit(1)


def run_pathfinding(args):
    """Zadanie 1: wyszukiwanie trasy A -> B (Dijkstra / A*)."""
    start_name = args[0]
    end_name = args[1]
    criterion = "transfers" if args[2].lower() == "p" else "time"
    start_time = parse_time(args[3])
    date_str = args[4] if len(args) > 4 else DEFAULT_DATE
    algo = args[5] if len(args) > 5 else "astar"
    query_date = date.fromisoformat(date_str)

    gtfs_dir = find_gtfs_dir()
    print(f"Ladowanie GTFS z: {gtfs_dir}", file=sys.stderr)
    data = GTFSData(gtfs_dir)

    departures = build_graph(data, query_date)

    start_ids = data.get_stop_ids_for_name(start_name)
    end_ids = data.get_stop_ids_for_name(end_name)

    if not start_ids:
        print(f"Nie znaleziono przystanku: {start_name}", file=sys.stderr)
        return
    if not end_ids:
        print(f"Nie znaleziono przystanku: {end_name}", file=sys.stderr)
        return

    print(f"Start: {start_name} ({len(start_ids)} peronow)", file=sys.stderr)
    print(f"Cel: {end_name} ({len(end_ids)} peronow)", file=sys.stderr)
    print(f"Kryterium: {'czas' if criterion == 'time' else 'przesiadki'}", file=sys.stderr)
    print(f"Algorytm: {algo}", file=sys.stderr)

    if algo == "dijkstra":
        heuristic = zero_heuristic
    elif criterion == "time":
        heuristic = make_haversine_heuristic(data, end_ids)
    else:
        heuristic = make_transfer_heuristic(data, end_ids)

    t0 = time.time()
    segments, stats = find_path(data, departures, start_ids, end_ids,
                                start_time, criterion, heuristic)
    elapsed = int((time.time() - t0) * 1000)
    stats["elapsed_ms"] = elapsed

    if segments is None:
        print("Nie znaleziono polaczenia!", file=sys.stderr)
        return

    print_result(segments, stats, start_time, criterion)


def run_tsp(args):
    """Zadanie 2: problem komiwojażera (Tabu Search)."""
    start_name = args[1]
    stop_names = [s.strip() for s in args[2].split(";")]
    criterion = "transfers" if args[3].lower() == "p" else "time"
    start_time = parse_time(args[4])
    date_str = args[5] if len(args) > 5 else DEFAULT_DATE
    variant = args[6] if len(args) > 6 else "aspiration"
    query_date = date.fromisoformat(date_str)

    gtfs_dir = find_gtfs_dir()
    print(f"Ladowanie GTFS z: {gtfs_dir}", file=sys.stderr)
    data = GTFSData(gtfs_dir)
    departures = build_graph(data, query_date)

    print(f"TSP: start={start_name}, przystanki={stop_names}", file=sys.stderr)
    print(f"Kryterium: {'czas' if criterion == 'time' else 'przesiadki'}", file=sys.stderr)
    print(f"Wariant: {variant}", file=sys.stderr)

    solver = TSPSolver(data, departures, criterion, start_time)
    step_limit = max(100, len(stop_names) * 50)

    t0 = time.time()
    if variant == "basic":
        best_perm, best_cost = solver.solve_basic(start_name, stop_names, step_limit)
    elif variant == "variable":
        best_perm, best_cost = solver.solve_variable(start_name, stop_names, step_limit)
    elif variant == "sampling":
        best_perm, best_cost = solver.solve_sampling(start_name, stop_names, step_limit)
    else:
        best_perm, best_cost = solver.solve_aspiration(start_name, stop_names, step_limit)
    elapsed = int((time.time() - t0) * 1000)

    route = " -> ".join([start_name] + best_perm + [start_name])
    print(f"--- Wynik TSP ---", file=sys.stderr)
    print(f"Kolejnosc: {route}", file=sys.stderr)
    if criterion == "time":
        print(f"Calkowity czas: {format_duration(best_cost)} ({best_cost} sek.)", file=sys.stderr)
    else:
        print(f"Liczba przesiadek: {best_cost}", file=sys.stderr)
    print(f"Czas obliczen: {elapsed} ms", file=sys.stderr)

    segments = solver.build_full_path(start_name, best_perm)
    for i, seg in enumerate(segments):
        print(f"{seg['from']} | {seg['to']} | {seg['route']} | "
              f"{format_time(seg['departure'])} | {format_time(seg['arrival'])}")
        if i < len(segments) - 1:
            next_seg = segments[i + 1]
            wait = next_seg["departure"] - seg["arrival"]
            if wait > 0:
                print(f"  --- Przesiadka ({format_duration(wait)} oczekiwania) ---")


def print_usage():
    """Wypisuje instrukcję użycia programu."""
    print("Uzycie (Zadanie 1):", file=sys.stderr)
    print('  python main.py <start> <cel> <t|p> <HH:MM:SS> [RRRR-MM-DD] [dijkstra|astar]', file=sys.stderr)
    print('  Przyklad: python main.py "Wroclaw Glowny" "Jelenia Gora" t 08:00:00', file=sys.stderr)
    print(file=sys.stderr)
    print("Uzycie (Zadanie 2 - TSP):", file=sys.stderr)
    print('  python main.py --tsp <start> <stop1;stop2;...> <t|p> <HH:MM:SS> [RRRR-MM-DD] [wariant]', file=sys.stderr)
    print('  Przyklad: python main.py --tsp "Wroclaw Glowny" "Legnica;Jelenia Gora" t 06:00:00', file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print_usage()
        sys.exit(1)

    args = sys.argv[1:]

    if args[0] == "--tsp":
        run_tsp(args)
    else:
        run_pathfinding(args)
