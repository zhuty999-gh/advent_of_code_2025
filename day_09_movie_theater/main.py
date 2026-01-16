from collections import namedtuple
from itertools import combinations
from types import SimpleNamespace
import numpy as np

Tile = namedtuple('Tile', ['x', 'y'])

# ---- Fast "red-or-green" membership for Part II (no materializing interior tiles) ----

def _build_boundary_index(loop_red_tiles):
    """
    Build an index of the polygon boundary described by the input order.

    The prompt states adjacent tiles in the list are connected by a straight
    horizontal/vertical line of green tiles, and the list wraps.

    Returns:
      - horiz_by_y: y -> list[(x1, x2)] inclusive
      - vert_by_x:  x -> list[(y1, y2)] inclusive
      - vert_edges: list[(x, y_low, y_high)] with half-open y in [y_low, y_high)
                   for ray-casting point-in-polygon tests
      - all_segments: list of all segments (type, fixed_coord, start, end)
                      type='H' -> (y, x1, x2), type='V' -> (x, y1, y2)
    """
    horiz_by_y = {}
    vert_by_x = {}
    vert_edges = []
    all_segments = []

    if not loop_red_tiles:
        return horiz_by_y, vert_by_x, vert_edges, all_segments

    n = len(loop_red_tiles)
    for i in range(n):
        a = loop_red_tiles[i]
        b = loop_red_tiles[(i + 1) % n]

        if a.y == b.y:
            y = a.y
            x1, x2 = (a.x, b.x) if a.x <= b.x else (b.x, a.x)
            horiz_by_y.setdefault(y, []).append((x1, x2))
            all_segments.append(('H', y, x1, x2))
        elif a.x == b.x:
            x = a.x
            y1, y2 = (a.y, b.y) if a.y <= b.y else (b.y, a.y)
            vert_by_x.setdefault(x, []).append((y1, y2))
            all_segments.append(('V', x, y1, y2))
            # Half-open interval avoids double-counting vertices in ray casting
            if y1 != y2:
                vert_edges.append((x, y1, y2))
        else:
            raise ValueError(f"Non-axis-aligned consecutive points: {a} -> {b}")

    return horiz_by_y, vert_by_x, vert_edges, all_segments


def _tile_on_boundary(tile, horiz_by_y, vert_by_x):
    # Horizontal segments at this y
    for x1, x2 in horiz_by_y.get(tile.y, []):
        if x1 <= tile.x <= x2:
            return True
    # Vertical segments at this x
    for y1, y2 in vert_by_x.get(tile.x, []):
        if y1 <= tile.y <= y2:
            return True
    return False


def _tile_inside_polygon(tile, vert_edges):
    """
    Ray-casting to +x direction using vertical edges only.

    We count crossings where:
      - edge.x > tile.x
      - tile.y in [y_low, y_high)   (half-open to avoid vertex double counts)
    """
    y = tile.y
    x = tile.x
    crossings = 0
    for edge_x, y_low, y_high in vert_edges:
        if edge_x > x and y_low <= y < y_high:
            crossings += 1
    return (crossings % 2) == 1


def _rectangle_intersects_boundary(rect_corners, all_segments):
    """
    Check if the interior of the rectangle defined by rect_corners
    is cut by any boundary segment of the polygon.
    
    rect_corners = (min_x, max_x, min_y, max_y)
    """
    r_min_x, r_max_x, r_min_y, r_max_y = rect_corners

    for seg_type, fixed, start, end in all_segments:
        if seg_type == 'H':
            # Horizontal segment at y=fixed, from x=start to x=end
            # Intersects if:
            # 1. The segment's Y is strictly inside the rect's Y range
            # 2. The segment's X range overlaps strictly with rect's X range
            if r_min_y < fixed < r_max_y:
                # Check x overlap (strictly inside)
                overlap_min = max(r_min_x, start)
                overlap_max = min(r_max_x, end)
                if overlap_min < overlap_max:
                    return True
        else: # seg_type == 'V'
            # Vertical segment at x=fixed, from y=start to y=end
            # Intersects if:
            # 1. The segment's X is strictly inside the rect's X range
            # 2. The segment's Y range overlaps strictly with rect's Y range
            if r_min_x < fixed < r_max_x:
                # Check y overlap (strictly inside)
                overlap_min = max(r_min_y, start)
                overlap_max = min(r_max_y, end)
                if overlap_min < overlap_max:
                    return True
    return False


def _make_red_or_green_checker(loop_red_tiles):
    """
    Returns:
      1. check_tile(tile) -> bool (is it red or green?)
      2. check_rect(corners) -> bool (does it intersect boundary?)
    """
    red_set = set(loop_red_tiles)
    horiz_by_y, vert_by_x, vert_edges, all_segments = _build_boundary_index(loop_red_tiles)

    def is_red_or_green(tile):
        if tile in red_set:
            return True
        if _tile_on_boundary(tile, horiz_by_y, vert_by_x):
            return True
        return _tile_inside_polygon(tile, vert_edges)

    def is_rect_valid_internally(tom, jerry):
        # Define rectangle bounds
        min_x, max_x = min(tom.x, jerry.x), max(tom.x, jerry.x)
        min_y, max_y = min(tom.y, jerry.y), max(tom.y, jerry.y)
        
        # If the rectangle is flat (width or height 0), it can't contain holes
        if min_x == max_x or min_y == max_y:
            return True
            
        rect_corners = (min_x, max_x, min_y, max_y)
        # It's invalid if a boundary cuts through it
        if _rectangle_intersects_boundary(rect_corners, all_segments):
            return False
        return True

    return is_red_or_green, is_rect_valid_internally

def import_tiles(filename):
    """Import tile coordinates from file into a list of namedtuples."""
    tiles = []
    with open(filename, 'r') as f:
        for line in f:
            x, y = line.strip().split(',')
            tiles.append(Tile(int(x), int(y)))
    return tiles


def find_square_with_diagonals(tom, jerry):
    """ Given two tiles forming the diagonals of a square, find the area of the square. """
    abs_x_diff = abs(tom.x - jerry.x) + 1
    abs_y_diff = abs(tom.y - jerry.y) + 1
    square_area = abs_x_diff * abs_y_diff
    return square_area


def find_largest_square_with_diagonals(tiles):
    """ Given a list of tiles, find the largest square that could be formed using two tiles as diagonals. """
    square_areas = []
    for tom, jerry in combinations(tiles, 2):
        square_areas.append(find_square_with_diagonals(tom, jerry))
    return max(square_areas)


def _find_neighbors(anchor, tiles):
    """ Given an anchor tile, find it's closest neighbors in the four directions. """
    tiles_right = sorted([t for t in tiles if t.y == anchor.y and t.x > anchor.x], key=lambda t: t.x)
    tiles_left = sorted([t for t in tiles if t.y == anchor.y and t.x < anchor.x], key=lambda t: t.x )
    tiles_above = sorted([t for t in tiles if t.x == anchor.x and t.y < anchor.y], key=lambda t: t.y)
    tiles_under = sorted([t for t in tiles if t.x == anchor.x and t.y > anchor.y], key=lambda t: t.y)

    return SimpleNamespace(
        t_right=tiles_right[0] if tiles_right else None,
        t_left=tiles_left[-1] if tiles_left else None,
        t_above=tiles_above[-1] if tiles_above else None,
        t_under=tiles_under[0] if tiles_under else None,
    )


def _fill_tiles_inbetween(anchor, neighbors):
    """ Given an anchor and its neighbors, fill the tiles inbetween to be green. """
    left = neighbors.t_left if neighbors.t_left else anchor
    right = neighbors.t_right if neighbors.t_right else anchor
    new_greens_horizontal = [Tile(x, anchor.y) for x in range(left.x+1, right.x)] if left or right else []

    peak = neighbors.t_above if neighbors.t_above else anchor
    trough = neighbors.t_under if neighbors.t_under else anchor
    new_greens_vertical = [Tile(anchor.x, y) for y in range(peak.y+1, trough.y)] if peak or trough else []

    new_greens = list(set(new_greens_horizontal + new_greens_vertical) - {anchor})
    return new_greens


def find_green_tiles(red_tiles):
    green_tiles = []

    for tt in red_tiles:
        neighbors = _find_neighbors(anchor=tt, tiles=red_tiles)
        new_greens = _fill_tiles_inbetween(anchor=tt, neighbors=neighbors)
        green_tiles += new_greens


    # Group boundary tiles by row for O(n) instead of O(rows * tiles)
    boundary_tiles = green_tiles + red_tiles
    rows_dict = {}
    for t in boundary_tiles:
        if t.y not in rows_dict:
            rows_dict[t.y] = []
        rows_dict[t.y].append(t.x)
    
    for row, x_coords in rows_dict.items():
        leftest = min(x_coords)
        rightest = max(x_coords)
        new_greens = [Tile(x, row) for x in range(leftest+1, rightest)] 
        green_tiles += new_greens
    
    return list(set(green_tiles))

def _find_corners(tom, jerry):
    """ Find the other two corners of tom and jerry. """
    corner_A = Tile(tom.x, jerry.y)
    corner_B = Tile(jerry.x, tom.y)
    return corner_A, corner_B


def find_largest_square_with_diagonals_II(tiles):
    """ Given a list of tiles, find the largest square that could be formed using two tiles as diagonals. 
        Satisfying the requirements for part II.
    """
    # IMPORTANT: Don't call find_green_tiles(tiles) for large inputs; it can be enormous.
    is_red_or_green, is_rect_valid_internally = _make_red_or_green_checker(tiles)

    square_areas = []

    for tom, jerry in combinations(tiles, 2):
        corner_A, corner_B = _find_corners(tom, jerry)
        
        # 1. Check if the computed corners are valid tiles (Red or Green)
        corners_valid = is_red_or_green(corner_A) and is_red_or_green(corner_B)
        
        # 2. Check if the rectangle intersects any boundary (meaning it crosses a hole)
        #    Only need to check this if corners are valid.
        if corners_valid:
            if is_rect_valid_internally(tom, jerry):
                square_areas.append(find_square_with_diagonals(tom, jerry))
    
    return max(square_areas) if square_areas else 0

def visualize_tiles(red_tiles, green_tiles=None):
    """Visualize the grid with red tiles (#), green tiles (X), and empty tiles (.)"""
    if green_tiles is None:
        green_tiles = []
    
    # Find grid bounds
    all_tiles = red_tiles + green_tiles
    max_x = max(t.x for t in all_tiles) + 2
    max_y = max(t.y for t in all_tiles) + 2
    
    # Convert to sets for fast lookup
    red_set = set(red_tiles)
    green_set = set(green_tiles)
    
    # Build and print grid
    for y in range(max_y):
        row = ""
        for x in range(max_x):
            tile = Tile(x, y)
            if tile in red_set:
                row += "#"
            elif tile in green_set:
                row += "X"
            else:
                row += "."
        print(row)
