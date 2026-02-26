import sys
from pathlib import Path

sys.setrecursionlimit(5000)


def parse_input(text: str):
    """Parse input text into shape definitions and region specifications."""
    shapes = []
    regions = []
    blocks = text.strip().split("\n\n")
    for block in blocks:
        lines = block.strip().split("\n")
        first_line = lines[0].strip()
        if first_line.endswith(":") and "x" not in first_line:
            cells = []
            for r, line in enumerate(lines[1:]):
                for c, ch in enumerate(line):
                    if ch == "#":
                        cells.append((r, c))
            shapes.append(cells)
        else:
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                colon_idx = line.index(":")
                dim_part = line[:colon_idx].strip()
                counts_part = line[colon_idx + 1 :].strip()
                w, h = map(int, dim_part.split("x"))
                counts = list(map(int, counts_part.split()))
                regions.append((w, h, counts))
    return shapes, regions


def find_unique_orientations(
    shape: list[tuple[int, int]],
) -> list[list[tuple[int, int]]]:
    """Find the unique orientations of a shape.

    Args:
        shape: List of tuples representing the filled coordinates.

    Returns:
        List of unique orientations, each as a list of coordinate
        tuples. At most 8 (4 rotations x 2 reflections).
    """
    orientations = set()
    for flip in (False, True):
        for rot in range(4):
            cells = []
            for r, c in shape:
                rr, cc = r, c
                if flip:
                    cc = -cc
                for _ in range(rot):
                    rr, cc = cc, -rr
                cells.append((rr, cc))
            min_r = min(r for r, _ in cells)
            min_c = min(c for _, c in cells)
            normalized = frozenset((r - min_r, c - min_c) for r, c in cells)
            orientations.add(normalized)
    return [sorted(o) for o in orientations]


def compute_absolute_coordinates(
    standard_shape: list[tuple[int, int]],
    top_left_coordinates: tuple[int, int],
) -> list[tuple[int, int]]:
    """Compute the absolute coordinates of a standard shape given a new top-left position.

    Args:
        standard_shape: List of coordinate tuples representing the spatial
            relationships of the shape (i.e. as if the top-left corner is at (0, 0)).
        top_left_coordinates: The coordinates of the new top-left corner.

    Returns:
        List of coordinate tuples representing the transformed shape's
        absolute coordinates.
    """
    dr, dc = top_left_coordinates
    return [(r + dr, c + dc) for r, c in standard_shape]


def solve_region(
    w: int,
    h: int,
    counts: list[int],
    all_orientations: list[list[list[tuple[int, int]]]],
    shapes: list[list[tuple[int, int]]],
) -> bool:
    """Determine whether a region can fit all required shapes.

    Uses bitmask backtracking with symmetry breaking and forward checking.
    The grid state is a Python int bitmask; conflict detection is a single
    C-level integer AND, making it much faster than linked-list DLX in
    pure Python.
    """
    total_cells = sum(counts[s] * len(shapes[s]) for s in range(len(shapes)))
    if total_cells > w * h:
        return False

    active = [(s, counts[s]) for s in range(len(counts)) if counts[s] > 0]
    if not active:
        return True

    # Pre-compute placement bitmasks per shape type
    type_masks: list[tuple[int, int, list[int]]] = []
    for s, cnt in active:
        masks: list[int] = []
        for orient in all_orientations[s]:
            max_r = max(r for r, _ in orient)
            max_c = max(c for _, c in orient)
            if max_r >= h or max_c >= w:
                continue
            for dr in range(h - max_r):
                for dc in range(w - max_c):
                    mask = 0
                    for r, c in orient:
                        mask |= 1 << ((r + dr) * w + (c + dc))
                    masks.append(mask)
        if len(masks) < cnt:
            return False
        type_masks.append((s, cnt, masks))

    # Sort by placements-per-copy ratio (most constrained first)
    type_masks.sort(key=lambda x: len(x[2]))

    # Build flat instance list; instances of same type are consecutive
    # Each entry: the shared masks list for that type
    inst_masks: list[list[int]] = []
    # group_ends[i] = index past the last instance of group i
    group_boundaries: list[tuple[int, int]] = []
    idx = 0
    for _, cnt, masks in type_masks:
        group_boundaries.append((idx, idx + cnt))
        for _ in range(cnt):
            inst_masks.append(masks)
        idx += cnt

    n = len(inst_masks)

    # --- Iterative backtracking with symmetry breaking ---
    mi = [0] * (n + 1)  # current mask index at each position
    grids = [0] * n  # saved grid state for backtracking
    grid = 0
    pos = 0

    while 0 <= pos < n:
        masks = inst_masks[pos]
        found = False
        nmasks = len(masks)

        i = mi[pos]
        while i < nmasks:
            m = masks[i]
            if grid & m == 0:
                new_grid = grid | m

                # Forward check: verify each remaining group has enough
                # valid placements. Short-circuit as soon as enough are found.
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

                # Commit placement
                grids[pos] = grid
                mi[pos] = i + 1  # on backtrack, resume from next mask
                grid = new_grid
                # Symmetry breaking: next instance of same type starts after i
                same_next = pos + 1 < n and inst_masks[pos + 1] is masks
                mi[pos + 1] = (i + 1) if same_next else 0
                pos += 1
                found = True
                break
            i += 1

        if not found:
            pos -= 1
            if pos >= 0:
                grid = grids[pos]

    return pos >= n


def main():
    script_dir = Path(__file__).resolve().parent
    filename = sys.argv[1] if len(sys.argv) > 1 else str(script_dir / "input.txt")
    text = Path(filename).read_text()
    shapes, regions = parse_input(text)
    all_orientations = [find_unique_orientations(s) for s in shapes]

    count = 0
    for w, h, counts in regions:
        if solve_region(w, h, counts, all_orientations, shapes):
            count += 1
    print(count)


if __name__ == "__main__":
    main()
