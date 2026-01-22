from dataclasses import dataclass
from pathlib import Path
from itertools import combinations
import re


@dataclass
class Machine:
    """Represents a single factory machine with its configuration."""
    indicator_lights: str  # Pattern like ".##." where . = off, # = on
    schematics: list[tuple[int, ...]]  # Button wiring - each tuple lists light indices to toggle
    joltage_reqs: list[int]  # Joltage requirements (ignored for Part 1)
    schematics_bitmask: list[tuple[int, ...]] = None  # Bitmask version: 0 stays 0, non-zero becomes 1
    
    def __post_init__(self):
        """Compute schematics_bitmask from schematics.
        
        Each schematic is a tuple of indices (e.g., (1, 3) means toggle lights 1 and 3).
        The bitmask is a fixed-length tuple with 1s at those positions.
        Example: schematic (1, 3) with 4 lights → (0, 1, 0, 1)
        """
        n = len(self.indicator_lights)
        self.schematics_bitmask = [
            tuple(1 if i in schematic else 0 for i in range(n))
            for schematic in self.schematics
        ]

    @property
    def num_lights(self) -> int:
        """Number of indicator lights on this machine."""
        return len(self.indicator_lights)

    @property
    def target_state(self) -> list[bool]:
        """Target state as a list of booleans (True = on, False = off)."""
        return [c == '#' for c in self.indicator_lights]

    @property
    def target_bitmask(self) -> int:
        """Target state as a bitmask (bit i = 1 means light i should be on)."""
        result = 0
        for i, c in enumerate(self.indicator_lights):
            if c == '#':
                result |= (1 << i)
        return result


def parse_line(line: str) -> Machine:
    """Parse a single line into a Machine object.
    
    Example line: [.##.] (3) (1,3) (2) (2,3) (0,2) (0,1) {3,5,4,7}
    """
    # Extract indicator lights pattern (inside square brackets)
    lights_match = re.search(r'\[([.#]+)\]', line)
    if not lights_match:
        raise ValueError(f"Could not find indicator lights in line: {line}")
    indicator_lights = lights_match.group(1)

    # Extract all button schematics (inside parentheses)
    schematic_matches = re.findall(r'\(([0-9,]+)\)', line)
    schematics: list[tuple[int, ...]] = []
    for match in schematic_matches:
        indices = tuple(int(x) for x in match.split(','))
        schematics.append(indices)

    # Extract joltage requirements (inside curly braces)
    joltage_match = re.search(r'\{([0-9,]+)\}', line)
    if not joltage_match:
        raise ValueError(f"Could not find joltage requirements in line: {line}")
    joltage_reqs = [int(x) for x in joltage_match.group(1).split(',')]

    return Machine(
        indicator_lights=indicator_lights,
        schematics=schematics,
        joltage_reqs=joltage_reqs
    )


def load_machines(filepath: str | Path) -> list[Machine]:
    """Load all machines from a file.
    
    Args:
        filepath: Path to the input file (e.g., 'example.txt' or 'input.txt')
    
    Returns:
        List of Machine objects parsed from the file
    """
    filepath = Path(filepath)
    machines: list[Machine] = []
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line:  # Skip empty lines
                machines.append(parse_line(line))
    
    return machines


def find_min_presses(machine: Machine) -> int:
    """Find the minimum number of button presses to reach the target state.
    
    Uses subset enumeration: since pressing a button twice cancels out,
    we only need to consider each button being pressed 0 or 1 times.
    Time complexity: O(2^B) where B is the number of buttons.
    
    Returns:
        Minimum number of button presses, or -1 if no solution exists.
    """
    # Target state as a tuple of 0s and 1s
    target = tuple(1 if c == '#' else 0 for c in machine.indicator_lights)
    num_buttons = len(machine.schematics_bitmask)
    
    # Try subsets of increasing size (to find minimum first)
    for num_pressed in range(1, num_buttons + 1):
        for button_indices in combinations(range(num_buttons), num_pressed):
            # Get the bitmasks for selected buttons
            selected = [machine.schematics_bitmask[i] for i in button_indices]
            
            # Sum element-wise and apply mod 2
            # zip(*selected) transposes: columns become rows
            final_state = tuple(sum(col) % 2 for col in zip(*selected))
            
            if final_state == target:
                return num_pressed
    
    return -1  # No solution found


def solve(filepath: str | Path) -> int:
    """Solve Part 1: sum of minimum button presses for all machines."""
    machines = load_machines(filepath)
    total = 0
    for machine in machines:
        min_presses = find_min_presses(machine)
        total += min_presses
    return total






if __name__ == "__main__":
    # Test with example data
    example_path = Path(__file__).parent / "example.txt"
    example_machines = load_machines(example_path)
    
    print("=== Example ===")
    for i, machine in enumerate(example_machines, 1):
        min_presses = find_min_presses(machine)
        print(f"Machine {i}: {machine.indicator_lights} → {min_presses} presses")
    
    example_total = solve(example_path)
    print(f"Example total: {example_total} (expected: 7)\n")
    
    # Solve with real input
    input_path = Path(__file__).parent / "input.txt"
    if input_path.exists():
        print("=== Input ===")
        input_total = solve(input_path)
        print(f"Part 1 Answer: {input_total}")

