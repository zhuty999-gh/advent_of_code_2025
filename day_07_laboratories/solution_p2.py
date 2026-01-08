def convert_input_to_coordinate_map(input: list[list[str]]) -> dict:
    """
    Converts a 2D list of characters (representing rows and columns)
    into a coordinate-based dictionary mapping (col, row) tuples to the character at that position.
    
    Args:
        input: List of lists of characters, where each inner list is a row.
        
    Returns:
        Dictionary mapping (col, row) coordinates to character values.
        For example, the character at column j and row i will be found at key (j, i).
    """
    out_dict = {}
    for i in range(len(input)):
        cur_row = input[i]
        for j in range(len(cur_row)):
            coordinate = (j, i) # col by row
            #label = cur_row[j] if cur_row[j] != "S" else "|"
            out_dict[coordinate] = cur_row[j]
    return out_dict

class Path:
    def __init__(self, chain, tail) -> None:
        self.chain: list = chain
        self.tail: tuple = tail

    def split(self, cords):
        output = []
        for c in cords:
            c_chain = self.chain + [c]
            c_tail = c
            new_path = Path(c_chain, c_tail)
            output.append(new_path)
        return output

def init_path(cord_map):
    """ """
    for index, (key, values) in enumerate(cord_map.items()):
        if values == "S":
            entrance = Path(chain=[key], tail=key)
            return [entrance]


def cord_tracer(cord, cord_map, path_counts):
    """
    Now uses path_counts (dict: coord -> int) instead of paths_by_tail (dict: coord -> list[Path]).
    Returns (new_cell_value, dict of {destination_coord: count_to_add})
    """
    x, y = cord
    cord_anchor_left = (x - 1, y)
    cord_anchor_right = (x + 1, y)
    cord_down_left = (x - 1, y + 1)
    cord_down_right = (x + 1, y + 1)
    cord_cell_down = (x, y + 1)

    neighbors = {
        "anchor_value": cord_map.get(cord, '.'),
        "anchor_left": cord_map.get(cord_anchor_left, '.'),
        "anchor_right": cord_map.get(cord_anchor_right, '.'),
        "down_left": cord_map.get(cord_down_left, '.'),
        "down_right": cord_map.get(cord_down_right, '.'),
        "cell_down": cord_map.get(cord_cell_down, '.'),
    }

    for key, value in neighbors.items():
        if value == 'S':
            neighbors[key] = '|'

    # O(1) lookup - get count of paths at this coordinate
    count_here = path_counts.get(cord, 0)


    match neighbors:
        case {"anchor_value": "|", "cell_down": "^"}:
            # Split: paths go both left and right
            new_counts = {}
            if count_here > 0:
                new_counts[cord_down_left] = count_here
                new_counts[cord_down_right] = count_here
            return "^", new_counts

        case {"cell_down": "^"}:
            return "^", {}

        case {"anchor_value": "|", "cell_down": "."}:
            # Beam continues downward
            new_counts = {}
            if count_here > 0:
                new_counts[cord_cell_down] = count_here
            return "|", new_counts

        case {"anchor_left": "|", "down_left": "^"}:
            # Beam from left hits diagonal splitter, creates beam here
            # No paths to propagate (those come from the split at anchor_left via case 1)
            return "|", {}

        case {"anchor_right": "|", "down_right": "^"}:
            # Beam from right hits diagonal splitter, creates beam here
            # No paths to propagate (those come from the split at anchor_right via case 1)
            return "|", {}
        
        case _:
            return neighbors["cell_down"], {}


import time

def path_finder(og_state: list[list[str]]):
    cur_map = convert_input_to_coordinate_map(og_state)
    cur_state = og_state # Note: This modifies the original list in place
    needle = 0
    
    # Find starting position
    start_coord = None
    for coord, val in cur_map.items():
        if val == 'S':
            start_coord = coord
            break
    
    # path_counts[coord] = number of paths ending at that coordinate
    path_counts = {start_coord: 1}
    
    while needle < len(og_state) - 1:
        num_paths = sum(path_counts.values())
        print(f"processing needle={needle}, paths={num_paths}")
        cur_row = cur_state[needle]
        cur_row_coordinates = [(x, needle) for x in range(len(cur_row))]
        
        t1 = time.perf_counter()
        results = [cord_tracer(c, cur_map, path_counts) for c in cur_row_coordinates]
        t2 = time.perf_counter()
        
        cur_down_new = [r[0] for r in results]

        # Merge all the count dictionaries from each cell
        new_path_counts = {}
        for r in results:
            for coord, count in r[1].items():
                new_path_counts[coord] = new_path_counts.get(coord, 0) + count
        t3 = time.perf_counter()
        
        path_counts = new_path_counts
        t4 = time.perf_counter()
        
        print(f"  -> cord_tracer: {t2-t1:.3f}s, merge: {t3-t2:.3f}s, assign: {t4-t3:.3f}s")
        
        # Update the state grid with the newly calculated row
        cur_state[needle+1] = cur_down_new
        
        # Efficiently update the coordinate map with the new values for the next row.
        # This is necessary because the processor for the *next* iteration (needle + 1)
        # will need to look up these values in the map.
        next_row_index = needle + 1
        map_updates = {
            (x, next_row_index): val 
            for x, val in enumerate(cur_down_new)
        }
        cur_map.update(map_updates)
        
        needle += 1
        
    # Return total count of all paths
    return sum(path_counts.values())