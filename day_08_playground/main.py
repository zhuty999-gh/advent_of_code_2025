from typing import NamedTuple
import math
from itertools import combinations


class Point3D(NamedTuple):
    x: int
    y: int
    z: int


def load_input(filepath: str) -> list[Point3D]:
    with open(filepath) as f:
        return [Point3D(*map(int, line.split(","))) for line in f]


def calc_dist_3D(boy: Point3D, girl: Point3D) -> float:
    dist = math.sqrt((boy.x - girl.x) ** 2 + (boy.y - girl.y) ** 2 + (boy.z - girl.z) ** 2)
    return dist


def gen_distance_table(inp):
    return {(p1, p2): calc_dist_3D(p1, p2) for p1, p2 in combinations(inp, 2)}


def connect_circuits(inp, stop=0):
    dist_map = gen_distance_table(inp)
    circ_yellowBook = {}
    circ_ids = {}
    circ_id = 0
    effective_connections = 1


    for (p1, p2), dist in sorted(dist_map.items(), key=lambda x: x[1])[:stop]:
        

        cur_circuits = {
            "p1_circ": circ_yellowBook.get(p1, 0),
            "p2_circ": circ_yellowBook.get(p2, 0)
        }

        p1_cid = cur_circuits["p1_circ"]
        p2_cid = cur_circuits["p2_circ"]

        match cur_circuits:
            case {"p1_circ": 0, "p2_circ": 0}: # Found a new circuit
                circ_id += 1
                circ_ids[circ_id] = [p1, p2]
                circ_yellowBook[p1] = circ_id
                circ_yellowBook[p2] = circ_id

            case {"p1_circ": c1, "p2_circ": 0} if c1 != 0:
                circ_yellowBook[p2] = p1_cid
                circ_ids[p1_cid].append(p2)

            case {"p1_circ": 0, "p2_circ": c2} if c2 != 0:
                circ_yellowBook[p1] = p2_cid
                circ_ids[p2_cid].append(p1)

            case {"p1_circ": c1, "p2_circ": c2} if c1 != 0 and c2 != 0:
                if c1 == c2: # do nothing if c1 and c2 already the same circuit
                    pass
                else: # else always merge c1 onto c2
                    circ_yellowBook.update({x: p2_cid for x in circ_ids[p1_cid]})
                    circ_ids[p2_cid].extend(circ_ids[p1_cid])
                    del circ_ids[p1_cid]        

    return circ_yellowBook, circ_ids       

def find_circLenProdSum(circuits: dict, n=3) -> int:
    Z = sorted((len(c) for c in circuits.values()), reverse=True)[:n]
    return math.prod(Z)


