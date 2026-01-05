import os
import string
import math

def read_input(filename='input.txt'):
    # Construct the path relative to this script file
    file_path = os.path.join(os.path.dirname(__file__), filename)
    with open(file_path, 'r') as f:
        lines = f.readlines()

    # The last line contains the operations
    operations_line = lines[-1].strip()
    operations = operations_line.split()

    # The previous lines are the grid
    grid_lines = lines[:-1]
    raw_rows = []
    for line in grid_lines:
        if line.strip(): # Skip empty lines if any
            raw_rows.append([int(x) for x in line.split()])

    # Transpose the rows into columns so they match the operations (one column per operation)
    # zip(*raw_rows) takes the i-th element from each row and groups them together
    grid_columns = [list(col) for col in zip(*raw_rows)] 

    return grid_columns, operations


def find_homework_answer(homework):
    """
    Given a 'homework' tuple or list where:
        - homework[0] is a list of lists of integers (each representing a row of numbers)
        - homework[1] is a list of arithmetic operator strings of the same length (e.g., ["*", "+", "*", "+"])
    For each row and its corresponding operator:
        - If the operator is '+', sum the numbers in the row.
        - If the operator is '*', multiply the numbers in the row.
    Returns the sum of all row results.
    """
    arithmetic_operators: list[str] = homework[1]
    results = []

    for i in range(len(arithmetic_operators)):
        ao: str = arithmetic_operators[i]
        numbers: list[int] = homework[0][i]
        match ao:
            case "+":
                results.append(sum(numbers))
            case "*":
                results.append(math.prod(numbers))
    
    answer = sum(results)
    return answer


        