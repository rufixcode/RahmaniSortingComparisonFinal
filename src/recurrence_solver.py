import numpy as np
from numpy.linalg import solve

# Recurrence: a_n = 3a_{n-1} - 2a_{n-2}
coeffs = [3, -2]  # [c1, c2]
initials = [2, 3]  # a0=2, a1=3

# --- Iterative method ---
def iterative_terms(coeffs, initials, n):
    k = len(coeffs)
    terms = initials[:]
    for i in range(k, n+1):
        next_val = sum(coeffs[j] * terms[i-1-j] for j in range(k))
        terms.append(next_val)
    return terms

# --- Closed-form method ---
def closed_form_terms(coeffs, initials, n):
    k = len(coeffs)
    poly = [1.0] + [-c for c in coeffs]
    roots = np.roots(poly)
    V = np.vander(roots, N=k, increasing=True)
    alphas = solve(V, np.array(initials, dtype=complex))
    seq = []
    for m in range(n+1):
        val = sum(alphas[i] * roots[i]**m for i in range(k))
        if abs(val.imag) < 1e-9:  # discard tiny imaginary parts
            val = val.real
        seq.append(val)
    return seq

# Generate first 15 terms
iter_terms = iterative_terms(coeffs, initials, 15)
print("Iterative first 15 terms:", iter_terms)

closed_terms = closed_form_terms(coeffs, initials, 15)
print("Closed-form first 15 terms:", closed_terms)

# 10th term comparison
print("Iterative a10 =", iter_terms[10])
print("Closed-form a10 =", closed_terms[10])
