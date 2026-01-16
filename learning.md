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
