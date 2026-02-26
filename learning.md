# Finding All Divisors Using Prime Factorization

**Key fact:** Every positive integer has exactly one prime factorization (*Fundamental Theorem of Arithmetic*).

---

## Step 1: Find the Prime Factorization

Repeatedly divide by the smallest prime that goes in evenly, until you reach 1.

**Example with 60:**

```
60 ÷ 2 = 30  
30 ÷ 2 = 15  
15 ÷ 3 = 5  
5 ÷ 5 = 1  
```

So,  
```
60 = 2² × 3 × 5
```

---

## Step 2: Generate All Divisors

A divisor cannot contain more of any prime than the original number has.  
So each divisor is formed by choosing, for each prime, how many copies to include (from 0 up to the max).

For \(60 = 2^2 \times 3 \times 5\):

- Pick 0, 1, or 2 twos
- Pick 0 or 1 three
- Pick 0 or 1 five

Multiply your choices together to get a divisor.

---

## Counting Divisors

Multiply together (exponent + 1) for each prime factor.

For 60:  
\[
(2+1) \times (1+1) \times (1+1) = 12\ \text{divisors}
\]

---

# Jupyter Notebook Tips

## Auto-reload Modules
When working in a notebook and modifying external `.py` files, use this magic command to auto-reload changes without restarting the kernel:

```python
%load_ext autoreload
%autoreload 2
```

---

# Python Tips

## Finding the Largest Character in a String
You can use `max()` directly on a string to find the character with the highest value (based on ASCII/Unicode value). For strings of digits, this effectively finds the largest digit.

```python
digits = "3295"
largest = max(digits)  # Returns "9" (as a string)
```

---

# Day 5: Recursion & Ranges

## Recursion Pitfalls: Wrapper vs. Helper
When writing a recursive function that requires a "helper" or "worker" step inside a loop (e.g., merging ranges until stable), be careful not to call the **wrapper** function recursively with the same data.

**Incorrect (Infinite Recursion):**
```python
def process_data(data):
    # This just calls itself with the same data -> Infinite Loop
    new_data = process_data(data) 
    # ...
```

**Correct (Iterative Wrapper):**
Call the helper function that performs the actual unit of work.
```python
def process_data(data):
    # Call the HELPER function to make progress
    new_data = helper_function(data) 
    if new_data != data:
        # Recurse or loop with the NEW data
        return process_data(new_data)
    return data
```

## Python `any()` function
The `any()` function is a concise way to check if *at least one* element in an iterable is Truthy. It stops evaluating as soon as it finds a True value (short-circuiting).

```python
# Check if ID is in ANY of the ranges
is_fresh = any(id in r for r in ranges)
```

## One-liner Generator Expressions
You can chain iterators to parse complex data structures efficiently in one line.

```python
# Parses "1-3\n5-7" into ((1, 3), (5, 7))
ranges = tuple(tuple(map(int, line.split('-'))) for line in raw_lines)
```

---

# Learning Notes

## Algorithms & Techniques

### Ray Casting Algorithm (Point-in-Polygon)

**Problem:** Determine if a point `(px, py)` lies inside a complex polygon.

**Technique:** The **Even-Odd Rule** (Ray Casting).
1. Draw a ray from the point in a fixed direction (e.g., to positive infinity along the X-axis).
2. Count how many times the ray intersects the polygon's edges.
3. **Odd** number of intersections $\rightarrow$ Point is **INSIDE**.
4. **Even** number of intersections $\rightarrow$ Point is **OUTSIDE**.

**Implementation Detail (Grid/Vertices):**
When a ray passes exactly through a vertex (corner), standard intersection logic can fail (counting 0 or 2 intersections incorrectly).
*Solution:* Treat vertical edges as **half-open intervals** $[y_{min}, y_{max})$.
- A horizontal ray at $y$ intersects a vertical edge if $y_{min} \le y < y_{max}$.
- This assigns each vertex $y$-coordinate to exactly one edge (the one starting there), ensuring correct counts.

### Maximal Rectangle in Rectilinear Polygon
To find the largest valid rectangle defined by two corners inside a rectilinear polygon (potentially with holes):
1. **Corner Validity:** Check if corners are inside/boundary using Ray Casting.
2. **Interior Validity:** Ensure the rectangle does not cross any polygon boundary lines.
   - If a rectangle is strictly inside, no boundary edge can slice through it.
   - Check if any horizontal polygon segment intersects the rectangle's vertical range strictly inside its X-range.
   - Check if any vertical polygon segment intersects the rectangle's horizontal range strictly inside its Y-range.

---

### Mixed Integer Linear Programming (MILP)

**Problem:** Find non-negative integers $x_1, x_2, \ldots, x_n$ that satisfy linear constraints while minimizing a linear objective.

**When to use:** Optimization problems where:
- You have a linear objective to minimize/maximize (e.g., `sum(x)`)
- Constraints are linear equations/inequalities (e.g., `A @ x == target`)
- Variables must be integers (counts, selections, etc.)

**Python Implementation with scipy:**

```python
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds

def solve_milp(A, target):
    """
    Minimize sum(x) subject to A.T @ x == target, x >= 0, x integers.
    
    A: (num_vars, num_constraints) matrix
    target: (num_constraints,) vector
    """
    num_vars = A.shape[0]
    
    c = np.ones(num_vars)                    # Objective: minimize sum(x)
    constraints = LinearConstraint(A.T, lb=target, ub=target)  # A.T @ x == target
    bounds = Bounds(lb=0, ub=np.inf)         # x >= 0
    integrality = np.ones(num_vars, dtype=int)  # All vars are integers
    
    result = milp(c, constraints=constraints, bounds=bounds, integrality=integrality)
    return int(round(result.fun)) if result.success else -1
```

**Why MILP is fast:**
1. **LP Relaxation:** First solves the continuous version (allowing fractional values), which is polynomial time.
2. **Convex Polytope:** Constraints define a convex shape; optimal is always at a vertex.
3. **Simplex Algorithm:** Only walks vertices (corners), not all interior points.
4. **Branch and Bound:** Uses LP bounds to prune the integer search tree intelligently.

**Complexity comparison:**

| Approach | Complexity | Example (6 buttons, 12 presses) |
|----------|------------|--------------------------------|
| Brute force sequences | O(B^n) | 6^12 = 2.2 billion |
| MILP | ~Polynomial | < 1 millisecond |

**Key insight:** When you see a problem asking to "minimize X subject to constraints," think Linear Programming!

---

### Shape Packing via Bitmask Backtracking (2D Bin Packing / Exact Cover)

**Problem:** Given rectangular grids and a list of shapes (with quantities), determine if all shapes can be placed on the grid without overlapping. Shapes can be rotated and flipped. The grid doesn't need to be fully covered. This is a 2D bin packing / exact cover problem — NP-complete, LeetCode Hard territory.

#### Key Terminology

- **Shape type**: One of 6 fixed patterns (e.g., a 3×3 U-shape).
- **Orientation**: A rotation/flip of a shape type. Up to 8 unique orientations per shape (4 rotations × 2 flips = dihedral group D4). Some collapse due to symmetry.
- **Placement**: A specific orientation at a specific (row, col) on the grid. One shape type on a 48×46 grid might have ~16,000 placements.
- **Instance**: A single copy of a shape type that must be placed. "65 copies of shape 0" = 65 instances.

The hierarchy: 6 shape types → each has 2–8 orientations → each orientation has many grid positions → thousands of placements per type.

#### Approach 1: Algorithm X with Dancing Links (DLX)

**Exact Cover Formulation:**

Build a boolean matrix where:

- **Rows** = every possible placement (instance × orientation × position)
- **Primary columns** = one per piece instance (or one per shape type with multiplicity). Must be covered exactly once (or exactly N times with multiplicity).
- **Secondary columns** = one per grid cell. Can be covered at most once (no overlap), but don't have to be covered.

Algorithm X searches for a subset of rows that covers all primary columns exactly the required number of times and no secondary column more than once.

**Dancing Links Data Structure:**

A sparse representation of the boolean matrix using doubly-linked list nodes. Each node has left/right/up/down pointers. Only 1s in the matrix get nodes.

- **Cover** a column: unlink it and all conflicting rows. Nodes "dance out."
- **Uncover** a column: relink everything. Nodes "dance back in." O(1) per pointer — the magic of DLX.
- **MRV heuristic**: Always branch on the column with the fewest remaining rows.

**Multiplicity Variant:** Instead of one primary column per instance, use one column per shape type with a `remaining` counter. Decrement on each placement; remove from header list when it hits 0.

#### Approach 2: Bitmask Backtracking (what the code actually uses)

**Core Idea:** Represent the entire grid as a single integer. Each bit = one cell. A 48×46 grid = a 2208-bit integer.

Each placement is precomputed as a bitmask. Collision detection becomes a single bitwise AND:

```python
grid & placement_mask == 0   # no conflict, safe to place
grid | placement_mask         # place the piece
```

**Symmetry Breaking:** Identical instances of the same shape share the same placement list. Enforce ascending placement index order among same-type instances. This prevents exploring N! equivalent permutations (e.g., 65! ≈ 10^90 for 65 copies of shape 0).

**Forward Checking:** After each placement, scan remaining shape types. Count how many placements still fit (`grid & mask == 0`). If the count < copies still needed → impossible → backtrack immediately. Weak but cheap — catches obvious dead ends without expensive recursive search.

**Why It's Fast Enough:**

1. **Cell count check**: Most regions fail instantly (total cells needed > grid area).
2. **Forward checking**: Catches dead ends within a few placements.
3. **Symmetry breaking**: Eliminates astronomical redundancy from identical pieces.
4. **Bitmask speed**: Collision detection is a single CPU-level integer operation.
5. **Most constrained first**: Shape types sorted by fewest placements.

#### DLX vs Bitmask Comparison

| Aspect | DLX | Bitmask |
|--------|-----|---------|
| Data structure | Doubly-linked list nodes | Python integers |
| Collision check | Pointer traversal | Single `&` operation |
| Dead end detection | MRV (column sizes) | Forward checking (rescan) |
| State update | Cover/uncover columns | `\|=` to place, restore int to undo |
| Python performance | Slow (object/pointer overhead) | Fast (C-level integer ops) |

Both are the same fundamental algorithm: backtracking search with pruning. They differ in data structure and heuristics, not in strategy.

**Complexity:** Worst case exponential (P^N for P placements and N instances). In practice, the optimizations make it tractable — most regions either fail trivially or solve quickly.
