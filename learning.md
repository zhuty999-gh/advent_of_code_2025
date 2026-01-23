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
