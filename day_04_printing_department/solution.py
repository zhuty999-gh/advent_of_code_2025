import os

def read_input():
    # Construct the path relative to this script file
    file_path = os.path.join(os.path.dirname(__file__), 'input.txt')
    with open(file_path, 'r') as f:
        # Read each line, strip whitespace, and convert to a list of characters
        return [list(line.strip()) for line in f]

grid = read_input()



