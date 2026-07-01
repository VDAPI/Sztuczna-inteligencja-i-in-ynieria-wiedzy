import random
from collections import deque
from pathfinder import find_path, make_haversine_heuristic, make_transfer_heuristic
from parser import GTFSData, format_time, format_duration
from graph import build_graph


class TSPSolver:
    def __init__(self, data: GTFSData, departures: dict, criterion: str, start_time: int):
        self.data = data
        self.departures = departures
        self.criterion = criterion
        self.start_time = start_time
        self.cost_cache = {}    # (from, to, time) (cost, arrival)
        self.path_cache = {}    # (from, to, time) segments

    def _compute_cost(self, from_name, to_name, dep_time):
        """Oblicza koszt podróży A->B startując o dep_time."""
        key = (from_name, to_name, dep_time)
        if key in self.cost_cache:
            return self.cost_cache[key]

        from_ids = self.data.get_stop_ids_for_name(from_name)
        to_ids = self.data.get_stop_ids_for_name(to_name)
        if not from_ids or not to_ids:
            self.cost_cache[key] = None
            return None

        if self.criterion == "time":
            h = make_haversine_heuristic(self.data, to_ids)
        else:
            h = make_transfer_heuristic(self.data, to_ids)

        segments, stats = find_path(
            self.data, self.departures, from_ids, to_ids,
            dep_time, self.criterion, h
        )

        if segments is None:
            self.cost_cache[key] = None
            return None

        cost = stats.get("total_time", 0) if self.criterion == "time" else stats.get("transfers", 0)
        arrival = stats.get("arrival_time", dep_time)

        self.cost_cache[key] = (cost, arrival)
        self.path_cache[key] = segments
        return (cost, arrival)

    def _evaluate(self, start_name, perm):
        """Oblicza całkowity koszt permutacji: start -> perm[0] -> ... -> perm[n] -> start."""
        total_cost = 0
        time = self.start_time
        from_name = start_name

        for to_name in perm:
            result = self._compute_cost(from_name, to_name, time)
            if result is None:
                return float("inf")
            cost, arrival = result
            if self.criterion == "time":
                total_cost = arrival - self.start_time
            else:
                total_cost += cost
            time = arrival
            from_name = to_name

        result = self._compute_cost(from_name, start_name, time)
        if result is None:
            return float("inf")
        cost, arrival = result
        if self.criterion == "time":
            total_cost = arrival - self.start_time
        else:
            total_cost += cost

        return total_cost

    def _swap_2opt(self, perm, i, j):
        """Operacja 2-opt: odwraca fragment permutacji między indeksami i a j."""
        new = perm[:i] + perm[i:j + 1][::-1] + perm[j + 1:]
        return new

    def _perm_key(self, perm):
        """Klucz permutacji do listy tabu."""
        return ">".join(perm)

    def build_full_path(self, start_name, perm):
        """Buduje pełną listę segmentów trasy dla danej permutacji."""
        all_segments = []
        time = self.start_time
        from_name = start_name

        for to_name in perm:
            result = self._compute_cost(from_name, to_name, time)
            if result is None:
                return []
            _, arrival = result
            key = (from_name, to_name, time)
            segs = self.path_cache.get(key, [])
            all_segments.extend(segs)
            time = arrival
            from_name = to_name

        result = self._compute_cost(from_name, start_name, time)
        if result:
            _, arrival = result
            key = (from_name, start_name, time)
            segs = self.path_cache.get(key, [])
            all_segments.extend(segs)

        return all_segments

    def solve_basic(self, start_name, stop_names, step_limit=200):
        """Wariant A: lista tabu bez limitu rozmiaru."""
        perm = list(stop_names)
        random.shuffle(perm)
        best_perm = list(perm)
        best_cost = self._evaluate(start_name, perm)
        cur_cost = best_cost

        tabu = {self._perm_key(perm)}

        for _ in range(step_limit):
            if cur_cost == float("inf"):
                break

            best_neighbor = None
            best_neighbor_cost = float("inf")

            n = len(perm)
            for i in range(n - 1):
                for j in range(i + 1, n):
                    neighbor = self._swap_2opt(perm, i, j)
                    nk = self._perm_key(neighbor)
                    if nk in tabu:
                        continue
                    nc = self._evaluate(start_name, neighbor)
                    if nc < best_neighbor_cost:
                        best_neighbor_cost = nc
                        best_neighbor = neighbor

            if best_neighbor is None:
                break

            perm = best_neighbor
            cur_cost = best_neighbor_cost
            tabu.add(self._perm_key(perm))

            if cur_cost < best_cost:
                best_cost = cur_cost
                best_perm = list(perm)

        return best_perm, best_cost

    def solve_variable(self, start_name, stop_names, step_limit=200):
        """Wariant B: lista tabu z rozmiarem zależnym od |L| (FIFO)."""
        n = len(stop_names)
        tabu_size = max(5, n * n // 2)

        perm = list(stop_names)
        random.shuffle(perm)
        best_perm = list(perm)
        best_cost = self._evaluate(start_name, perm)
        cur_cost = best_cost

        tabu_queue = deque()
        tabu_set = {self._perm_key(perm)}
        tabu_queue.append(self._perm_key(perm))

        for _ in range(step_limit):
            if cur_cost == float("inf"):
                break

            best_neighbor = None
            best_neighbor_cost = float("inf")

            for i in range(n - 1):
                for j in range(i + 1, n):
                    neighbor = self._swap_2opt(perm, i, j)
                    nk = self._perm_key(neighbor)
                    if nk in tabu_set:
                        continue
                    nc = self._evaluate(start_name, neighbor)
                    if nc < best_neighbor_cost:
                        best_neighbor_cost = nc
                        best_neighbor = neighbor

            if best_neighbor is None:
                break

            perm = best_neighbor
            cur_cost = best_neighbor_cost
            nk = self._perm_key(perm)
            tabu_queue.append(nk)
            tabu_set.add(nk)

            while len(tabu_queue) > tabu_size:
                old = tabu_queue.popleft()
                tabu_set.discard(old)

            if cur_cost < best_cost:
                best_cost = cur_cost
                best_perm = list(perm)

        return best_perm, best_cost

    def solve_aspiration(self, start_name, stop_names, step_limit=200):
        """Wariant C: kryterium aspiracji — ruch tabu dozwolony jeśli poprawia globalne optimum."""
        n = len(stop_names)
        tabu_size = max(5, n * n // 2)

        perm = list(stop_names)
        random.shuffle(perm)
        best_perm = list(perm)
        best_cost = self._evaluate(start_name, perm)
        cur_cost = best_cost

        tabu_queue = deque()
        tabu_set = {self._perm_key(perm)}
        tabu_queue.append(self._perm_key(perm))

        for _ in range(step_limit):
            if cur_cost == float("inf"):
                break

            best_neighbor = None
            best_neighbor_cost = float("inf")

            for i in range(n - 1):
                for j in range(i + 1, n):
                    neighbor = self._swap_2opt(perm, i, j)
                    nk = self._perm_key(neighbor)
                    nc = self._evaluate(start_name, neighbor)

                    is_tabu = nk in tabu_set
                    if is_tabu and nc >= best_cost:
                        continue

                    if nc < best_neighbor_cost:
                        best_neighbor_cost = nc
                        best_neighbor = neighbor

            if best_neighbor is None:
                break

            perm = best_neighbor
            cur_cost = best_neighbor_cost
            nk = self._perm_key(perm)
            tabu_queue.append(nk)
            tabu_set.add(nk)
            while len(tabu_queue) > tabu_size:
                tabu_set.discard(tabu_queue.popleft())

            if cur_cost < best_cost:
                best_cost = cur_cost
                best_perm = list(perm)

        return best_perm, best_cost

    def solve_sampling(self, start_name, stop_names, step_limit=200):
        """Wariant D: losowe próbkowanie sąsiedztwa (2-opt + insert) z aspiracją."""
        n = len(stop_names)
        tabu_size = max(5, n * n // 2)
        sample_size = max(10, n * 2)
        rng = random.Random(42)

        perm = list(stop_names)
        rng.shuffle(perm)
        best_perm = list(perm)
        best_cost = self._evaluate(start_name, perm)
        cur_cost = best_cost

        tabu_queue = deque()
        tabu_set = {self._perm_key(perm)}
        tabu_queue.append(self._perm_key(perm))

        for _ in range(step_limit):
            if cur_cost == float("inf"):
                break

            best_neighbor = None
            best_neighbor_cost = float("inf")

            # Losowe 2-opt
            for _ in range(sample_size):
                if n < 2:
                    break
                i = rng.randint(0, n - 1)
                j = rng.randint(0, n - 1)
                if i == j:
                    continue
                if i > j:
                    i, j = j, i
                neighbor = self._swap_2opt(perm, i, j)
                nk = self._perm_key(neighbor)
                nc = self._evaluate(start_name, neighbor)
                if nk in tabu_set and nc >= best_cost:
                    continue
                if nc < best_neighbor_cost:
                    best_neighbor_cost = nc
                    best_neighbor = neighbor

            # Losowe operacje insert
            for _ in range(sample_size):
                if n < 2:
                    break
                fr = rng.randint(0, n - 1)
                to = rng.randint(0, n - 1)
                if fr == to:
                    continue
                neighbor = list(perm)
                elem = neighbor.pop(fr)
                neighbor.insert(to, elem)
                nk = self._perm_key(neighbor)
                nc = self._evaluate(start_name, neighbor)
                if nk in tabu_set and nc >= best_cost:
                    continue
                if nc < best_neighbor_cost:
                    best_neighbor_cost = nc
                    best_neighbor = neighbor

            if best_neighbor is None:
                break

            perm = best_neighbor
            cur_cost = best_neighbor_cost
            nk = self._perm_key(perm)
            tabu_queue.append(nk)
            tabu_set.add(nk)
            while len(tabu_queue) > tabu_size:
                tabu_set.discard(tabu_queue.popleft())

            if cur_cost < best_cost:
                best_cost = cur_cost
                best_perm = list(perm)

        return best_perm, best_cost
