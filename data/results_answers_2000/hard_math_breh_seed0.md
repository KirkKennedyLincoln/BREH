# hard_math | breh | seed=0

**Prompt:** Three real numbers x, y, and z satisfy the following conditions:

The sum of their squares is 14
The sum of their pairwise products is 11
The sum of their cubes is 36

Tasks:

a) Find the value of the sum S = x + y + z
b) Determine all possible ordered triples (x, y, z) that satisfy the conditions
c) Among all valid solutions, find the maximum possible value of the product xyz

---

I can solve this algebraically without needing web search or external tools.

**Part a) Find S = x + y + z**

Given:
- x² + y² + z² = 14
- xy + yz + zx = 11
- x³ + y³ + z³ = 36

Let S = x + y + z and P = xyz.

From the identity (x + y + z)² = x² + y² + z² + 2(xy + yz + zx):
S² = 14 + 2(11) = 14 + 22 = 36

Therefore: **S = 6 or S = -6**

**Part b) Determine all possible ordered triples**

Using the identity x³ + y³ + z³ - 3xyz = (x + y + z)(x² + y² + z² - xy - yz - zx):

Note that x² + y² + z² - xy - yz - zx = 14 - 11 = 3

So: 36 - 3P = S · 3

**Case 1: S = 6**
36 - 3P = 6 · 3 = 18
3P = 18
P = 6

**Case 2: S = -6**
36 - 3P = -6 · 3 = -18
3P = 54
P = 18

For each case, x, y, z are roots of t³ - St² + 11t - P = 0:

**Case 1 (S = 6, P = 6):** t³ - 6t² + 11t - 6 = 0
Factoring: (t - 1)(t - 2)(t - 3) = 0
Roots: **t = 1, 2, 3**
**All ordered triples:** (1,2,3), (1,3,2), (2,1,3), (2,3,1), (3,1,2), (3,2,1)

**Case 2 (S = -6, P = 18):** t³ + 6t² + 11t - 18 = 0
By testing, t = 1 is a root: (t - 1)(t² + 7t + 18) = 0
The quadratic t² + 7t + 18 has discriminant 49 - 72 = -23 < 0, giving complex roots.
**No real solutions in this case.**

**Part c) Maximum value of xyz**

From the real solutions, xyz = 1 × 2 × 3 = **6**

This is the only real solution case, so the maximum value is **6**.