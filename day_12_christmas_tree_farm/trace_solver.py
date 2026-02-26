"""Run the bitmask backtracking solver with event recording for visualization."""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from new_part_1 import parse_input, find_unique_orientations

MAX_EVENTS = 50_000


def solve_region_traced(w, h, counts, all_orientations, shapes):
    events = []
    total_cells = sum(counts[s] * len(shapes[s]) for s in range(len(shapes)))
    if total_cells > w * h:
        return False, events

    active = [(s, counts[s]) for s in range(len(counts)) if counts[s] > 0]
    if not active:
        return True, events

    type_data = []
    for s, cnt in active:
        masks, cells_list = [], []
        for orient in all_orientations[s]:
            max_r = max(r for r, _ in orient)
            max_c = max(c for _, c in orient)
            if max_r >= h or max_c >= w:
                continue
            for dr in range(h - max_r):
                for dc in range(w - max_c):
                    mask = 0
                    cells = []
                    for r, c in orient:
                        mask |= 1 << ((r + dr) * w + (c + dc))
                        cells.append([r + dr, c + dc])
                    masks.append(mask)
                    cells_list.append(cells)
        if len(masks) < cnt:
            return False, events
        type_data.append((s, cnt, masks, cells_list))

    type_data.sort(key=lambda x: len(x[2]))

    inst_masks = []
    inst_cells_all = []
    inst_shape_type = []
    group_boundaries = []
    idx = 0
    for s, cnt, masks, cells_list in type_data:
        group_boundaries.append((idx, idx + cnt))
        for _ in range(cnt):
            inst_masks.append(masks)
            inst_cells_all.append(cells_list)
            inst_shape_type.append(s)
        idx += cnt

    n = len(inst_masks)
    mi = [0] * (n + 1)
    grids = [0] * n
    grid = 0
    pos = 0
    capped = False

    while 0 <= pos < n:
        masks = inst_masks[pos]
        found = False
        nmasks = len(masks)
        i = mi[pos]

        while i < nmasks:
            m = masks[i]
            if grid & m == 0:
                new_grid = grid | m

                prune = False
                for gs, ge in group_boundaries:
                    if ge <= pos + 1:
                        continue
                    needed = ge - max(pos + 1, gs)
                    if needed <= 0:
                        continue
                    gmasks = inst_masks[gs]
                    count = 0
                    for gm in gmasks:
                        if new_grid & gm == 0:
                            count += 1
                            if count >= needed:
                                break
                    if count < needed:
                        prune = True
                        break
                if prune:
                    i += 1
                    continue

                grids[pos] = grid
                mi[pos] = i + 1
                grid = new_grid
                same_next = pos + 1 < n and inst_masks[pos + 1] is masks
                mi[pos + 1] = (i + 1) if same_next else 0

                if not capped:
                    events.append({
                        "t": "c",
                        "p": pos,
                        "s": inst_shape_type[pos],
                        "cells": inst_cells_all[pos][i],
                    })
                    if len(events) >= MAX_EVENTS:
                        capped = True

                pos += 1
                found = True
                break
            i += 1

        if not found:
            if not capped:
                events.append({"t": "b", "p": pos})
                if len(events) >= MAX_EVENTS:
                    capped = True
            pos -= 1
            if pos >= 0:
                grid = grids[pos]

    return pos >= n, events


def main():
    script_dir = Path(__file__).resolve().parent
    text = (script_dir / "input.txt").read_text()
    shapes, regions = parse_input(text)
    all_orientations = [find_unique_orientations(s) for s in shapes]

    region_idx = int(sys.argv[1]) if len(sys.argv) > 1 else None

    if region_idx is not None:
        w, h, counts = regions[region_idx]
    else:
        for i, (w, h, counts) in enumerate(regions):
            total = sum(counts[s] * len(shapes[s]) for s in range(len(shapes)))
            if total <= w * h:
                region_idx = i
                break
        if region_idx is None:
            print("No feasible regions found!")
            return
        w, h, counts = regions[region_idx]

    total = sum(counts[s] * len(shapes[s]) for s in range(len(shapes)))
    n_inst = sum(counts)
    print(f"Region #{region_idx}: {w}x{h}, counts={counts}")
    print(f"Total cells: {total}, Grid area: {w*h}, Fill: {total/(w*h)*100:.1f}%")
    print(f"Instances: {n_inst}")
    print("Solving...")

    t0 = time.perf_counter()
    result, events = solve_region_traced(w, h, counts, all_orientations, shapes)
    elapsed = time.perf_counter() - t0

    commits = sum(1 for e in events if e["t"] == "c")
    backtracks = sum(1 for e in events if e["t"] == "b")
    print(f"Result: {'SOLVABLE' if result else 'UNSOLVABLE'}")
    print(f"Time: {elapsed:.2f}s")
    print(f"Events: {len(events)} ({commits} commits, {backtracks} backtracks)")

    # Shape definitions for the visualizer
    shape_defs = []
    for s in shapes:
        max_r = max(r for r, _ in s)
        max_c = max(c for _, c in s)
        grid_vis = [[False] * (max_c + 1) for _ in range(max_r + 1)]
        for r, c in s:
            grid_vis[r][c] = True
        shape_defs.append(grid_vis)

    trace = {
        "w": w, "h": h,
        "counts": counts,
        "shapeDefs": shape_defs,
        "result": result,
        "events": events,
        "nInstances": n_inst,
        "regionIdx": region_idx,
        "elapsed": round(elapsed, 3),
    }

    outpath = script_dir / "trace_data.js"
    with open(outpath, "w") as f:
        f.write("const TRACE = ")
        json.dump(trace, f, separators=(",", ":"))
        f.write(";\n")

    print(f"Trace written to {outpath} ({outpath.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
