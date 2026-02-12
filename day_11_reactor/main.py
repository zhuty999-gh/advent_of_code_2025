from dataclasses import dataclass, field
from pathlib import Path

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent


@dataclass
class Device:
    """A device with its name and list of attached output devices."""
    name: str
    attached: list[str] = field(default_factory=list)


def import_devices(filename: str = "input.txt") -> dict[str, Device]:
    """
    Import devices from a file into a dictionary of Device dataclasses.
    
    Each line in the file has format: "device_name: output1 output2 output3"
    
    Args:
        filename: The input file to read (example.txt or input.txt)
        
    Returns:
        A dictionary mapping device names to their Device dataclass instances.
    """
    devices: dict[str, Device] = {}
    filepath = SCRIPT_DIR / filename
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            # Parse "name: output1 output2 output3"
            name, outputs_str = line.split(': ')
            outputs = outputs_str.split()
            
            devices[name] = Device(name=name, attached=outputs)
    
    return devices


def build_adjacency_graph(devices: dict[str, Device]) -> dict[str, list[str]]:
    """
    Build an adjacency list representation of the device graph.
    
    Args:
        devices: Dictionary of Device objects from import_devices()
        
    Returns:
        Dictionary mapping device names to list of output device names.
    """
    return {name: device.attached for name, device in devices.items()}


def find_all_paths(graph: dict[str, list[str]], start: str, end: str) -> list[list[str]]:
    """
    Find all paths from start to end using DFS.
    
    Args:
        graph: Adjacency list representation of the device graph
        start: Starting device name (e.g., "you")
        end: Ending device name (e.g., "out")
        
    Returns:
        List of all paths, where each path is a list of device names.
    """
    all_paths = []
    visited = {start}
    
    def dfs(current: str, path: list[str]):
        if current == end:
            all_paths.append(path.copy())
            return
        
        if current not in graph:
            return
        
        for neighbor in graph[current]:
            if neighbor not in visited:
                visited.add(neighbor)
                path.append(neighbor)
                dfs(neighbor, path)
                path.pop()
                visited.discard(neighbor)
    
    dfs(start, [start])
    return all_paths


def topological_sort(graph: dict[str, list[str]], start: str) -> list[str]:
    """
    Return a topological ordering of all nodes reachable from start.
    Assumes the reachable subgraph is a DAG.
    """
    visited = set()
    order = []

    def dfs(node: str):
        if node in visited:
            return
        visited.add(node)
        for neighbor in graph.get(node, []):
            dfs(neighbor)
        order.append(node)

    dfs(start)
    order.reverse()
    return order


def count_paths_with_required(
    graph: dict[str, list[str]], start: str, end: str, required: set[str]
) -> int:
    """
    Count all paths from start to end that visit every node in 'required'.
    
    Uses topological sort + DP instead of enumerating all paths.
    
    State: (node, frozenset of which required nodes have been seen so far)
    dp[node][seen] = number of paths from start to node where 'seen' is the
                     subset of required nodes visited along the way.
    """
    from collections import defaultdict

    order = topological_sort(graph, start)

    # dp[node] is a dict: frozenset -> count
    # meaning: number of paths from start to node having seen exactly that subset of required
    dp: dict[str, dict[frozenset, int]] = defaultdict(lambda: defaultdict(int))

    # Base case: we're at start, having seen whichever required nodes start itself is
    init_seen = frozenset({start} & required)
    dp[start][init_seen] = 1

    for node in order:
        if not dp[node]:
            continue
        for seen, cnt in dp[node].items():
            for neighbor in graph.get(node, []):
                # What subset of required have we seen after visiting neighbor?
                new_seen = seen | (frozenset({neighbor}) if neighbor in required else frozenset())
                dp[neighbor][new_seen] += cnt

    # Sum up all paths reaching 'end' that have seen ALL required nodes
    full_required = frozenset(required)
    return dp[end].get(full_required, 0)


def main():
    # Import devices from file
    devices = import_devices("input.txt")
    
    # Build the adjacency graph
    graph = build_adjacency_graph(devices)
    
    # Find all paths from "you" to "out"
    paths = find_all_paths(graph, "you", "out")
    
    print(f"Found {len(paths)} paths from 'you' to 'out':\n")
    
    for path in paths:
        print(" -> ".join(path))
    
    print(f"\nAnswer I: {len(paths)}")

    # Part II: Count paths from svr to out that visit both dac and fft
    count_dac_fft = count_paths_with_required(graph, "svr", "out", {"dac", "fft"})

    print(f"\nAnswer II: {count_dac_fft}")


if __name__ == "__main__":
    main()

