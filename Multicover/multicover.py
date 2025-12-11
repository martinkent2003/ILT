import csv
import math
import time
from pathlib import Path
from typing import Dict, List, Set, Tuple

R_DEFAULT = 5
M_LIMIT = 500  # set to an integer to get first M materials

CSV_PATH = Path("materials.csv")

N5_KANJI_STR = ("人一日大年出本中子見国上分生行二間時気十女三前入小後長下学月何来話山高今書五名金男外四先川東聞語九食八水天木六万白七円電父北車母半百土西読千校右南左友火毎雨休午")
U: Set[str] = set(N5_KANJI_STR)

def load_materials(csv_path: Path, m_limit=math.inf) -> Tuple[List[str], List[int], List[Set[str]]]:
    # Returns: (names, costs, sets)
    names: List[str] = []
    costs: List[int] = []
    sets_: List[Set[str]] = []

    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if len(names) >= (m_limit if math.isfinite(m_limit) else 10**12):
                break
            name = row["Name"].strip()
            try:
                cost = int(row["Cost"])
            except Exception:
                cost = 1
            if cost <= 0:
                cost = 1

            kanji_str = (row.get("Kanji") or "").strip()
            kset = {ch for ch in kanji_str if ch in U}
            if not kset:
                continue

            names.append(name)
            costs.append(cost)
            sets_.append(kset)

    return names, costs, sets_

def compute_availability(S: List[Set[str]]) -> Dict[str, int]:
    # avail[u] = number of materials that contain u
    avail = {u: 0 for u in U}
    for s in S:
        for u in s:
            avail[u] += 1
    return avail

def greedy_weighted_multicover(
    names: List[str],
    costs: List[int],
    sets_: List[Set[str]],
    r_default: int,
) -> Tuple[List[int], Dict[str, int], Dict[str, int], Dict[str, int]]:
    # Returns: C_indices, need, avail, coverage
    m = len(sets_)
    
    avail = compute_availability(sets_)
    need = {u: min(r_default, avail[u]) for u in U}

    if all(need[u] == 0 for u in U):
        return [], need, avail, {u: 0 for u in U}

    remaining = set(range(m))
    C_indices: List[int] = []
    cov = {u: 0 for u in U}  # number of chosen materials that cover u

    # Greedy loop
    while True:
        if all(need[u] == 0 for u in U):
            break

        best = None
        best_score = 0.0

        for i in list(remaining):
            gain = 0
            # Count how many distinct still-needed kanji this material covers
            for u in sets_[i]:
                if need[u] > 0:
                    gain += 1
            if gain <= 0:
                continue
            score = gain / costs[i]
            if score > best_score:
                best_score = score
                best = i

        if best is None:
            break

        # Select best
        C_indices.append(best)
        remaining.remove(best)

        # Apply one exposure for each kanji this material covers
        for u in sets_[best]:
            if need[u] > 0:
                need[u] -= 1
            cov[u] += 1

    return C_indices, need, avail, cov

def main():
    if not CSV_PATH.exists():
        print(f"Error: {CSV_PATH} not found.")
        return

    names, costs, sets_ = load_materials(CSV_PATH, m_limit=M_LIMIT)
    if not names:
        print("No materials loaded (after filtering).")
        return

    print(f"Loaded {len(names)} materials from {CSV_PATH}.")

    # Run greedy with timer
    t0 = time.perf_counter()
    C_indices, need, avail, cov = greedy_weighted_multicover(names, costs, sets_, R_DEFAULT)
    t1 = time.perf_counter()
    print(f"\nRuntime: {(t1 - t0):.6f} seconds")

    total_cost = sum(costs[i] for i in C_indices)
    print(f"\nSelected {len(C_indices)} materials; Total cost = {total_cost}")
    print("Selected material names:")
    for i in C_indices:
        print(f"  - {names[i]} (cost={costs[i]})")

    print("\nKanji with availability < r(u) in the pool")
    scarce = [(u, avail[u]) for u in sorted(U) if avail[u] < R_DEFAULT]
    if scarce:
        print(f"  Total kanji with requirements not met: {len(scarce)}")
        for u, a in scarce:
            print(f"  {u}: avail={a} < r={R_DEFAULT}")
    else:
        print("  None. Every kanji appears at least r(u) times in the pool.")

if __name__ == "__main__":
    main()
