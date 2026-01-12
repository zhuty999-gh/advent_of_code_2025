from collections import namedtuple
from gettext import find
from itertools import combinations

Tile = namedtuple('Tile', ['x', 'y'])


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