def read_input(file_path: str) -> list[list[str]]:
    """Reads the input file and returns it as a list of lists of characters."""
    with open(file_path, 'r') as f:
        return [list(line.strip()) for line in f]


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
            out_dict[coordinate] = cur_row[j]
    return out_dict



def coordinate_processor(coordinate: tuple[int, int], coordinate_map: dict) -> (str, int):
    """
    Determines the resulting symbol (tachyon beam or splitter) for the cell directly below the input coordinate.

    Args:
        coordinate: A tuple (x, y) representing the (column, row) to check.
        coordinate_map: A dictionary mapping (col, row) coordinates to their character values
                        (e.g., '.', '^', '|', 'S', etc).

    Returns:
        A tuple containing:
        1. The appropriate symbol for the cell directly below the given coordinate for the next step of propagation.
           - '^' if a splitter is directly below.
           - '|' if a vertical beam should propagate through due to the presence of previous beams or splitters.
           - Otherwise, passes through the cell_below value (continues propagation or empty space).
        2. An integer indicating if a split happened:
           - 1 if a split happened (or a beam was generated/propagated).
           - 0 otherwise.
    
    The function inspects:
        - The cell itself ('anchor_value'),
        - Direct left/right cells at the current row ('anchor_left', 'anchor_right'),
        - Diagonally down-left/right cells ('down_left', 'down_right'),
        - The direct cell below ('cell_down').
    It uses these to determine the evolution of beam and splitter propagation according to the puzzle rules.
    """
    x, y = coordinate

    # Get the current and adjacent cell values needed for propagation rules
    neighbors = {
        "anchor_value": coordinate_map.get(coordinate, '.'),
        "anchor_left": coordinate_map.get((x - 1, y), '.'),
        "anchor_right": coordinate_map.get((x + 1, y), '.'),
        "down_left": coordinate_map.get((x - 1, y + 1), '.'),
        "down_right": coordinate_map.get((x + 1, y + 1), '.'),
        "cell_down": coordinate_map.get((x, y + 1), '.'),
    }

    # Normalize 'S' (start) to '|' (beam) for all neighbors
    for key, value in neighbors.items():
        if value == 'S':
            neighbors[key] = '|'

    # Check propagation cases according to puzzle physics
    match neighbors:
        # This is the only case in which we add the split counts by 1
        case {"anchor_value": "|", "cell_down": "^"}:
            return "^", 1

        # Directly below is a splitter; propagate splitter upward.
        case {"cell_down": "^"}:
            return "^", 0
        # Beam comes from left and hits a splitter from below left; propagate upward beam.
        case {"anchor_left": "|", "down_left": "^"}:
            return "|", 0
        # Beam comes from right and hits a splitter from below right; propagate upward beam.
        case {"anchor_right": "|", "down_right": "^"}:
            return "|", 0
        # Directly above is a vertical beam, and below is empty; propagate the beam downward.
        case {"anchor_value": "|", "cell_down": "."}:
            return "|", 0
        # Otherwise, pass through whatever is directly below.
        case _:
            return neighbors["cell_down"], 0
    

def count_splits(og_state: list[list[str]]) -> int: 
    """
    Simulates the tachyon beam propagation row by row and counts the total number of splits.
    
    This function:
    1. Creates an initial coordinate map from the input grid.
    2. Iterates through the grid row by row (from top to bottom).
    3. For each row, it calculates the state of the row directly below it based on the current row's values.
    4. Updates the coordinate map with the newly calculated values for the next row.
    5. Counts how many splits occurred during this propagation step.
    
    Args:
        og_state: The initial 2D grid of the tachyon manifold.
        
    Returns:
        The total number of times the beam was split during propagation.
    """
    cur_map = convert_input_to_coordinate_map(og_state)
    cur_state = og_state # Note: This modifies the original list in place
    needle = 0
    total_splits = 0
    
    # Iterate through rows. We stop at len - 1 because we process 'needle' (current row) 
    # to determine the state of 'needle + 1' (next row).
    # We need to process up to the second-to-last row to update the very last row.
    while needle < len(og_state) - 1:
        cur_row = cur_state[needle]
        cur_row_coordinates = [(x, needle) for x in range(len(cur_row))]
        
        # Get both the new characters and split counts in one pass
        # coordinate_processor returns (new_char, split_count)
        results = [coordinate_processor(c, cur_map) for c in cur_row_coordinates]
        
        # Unpack results:
        # cur_down_new: The list of characters for the next row (needle + 1)
        # row_split_count: Sum of splits generated by the current row's propagation
        cur_down_new = [r[0] for r in results]
        row_split_count = sum(r[1] for r in results)
        total_splits += row_split_count
        
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
        
    return total_splits
        








