import numpy as np
from typing import Any, cast
from scipy.sparse import diags, eye
from scipy.sparse.linalg import spsolve

def D2_sparse(n: int):
    return diags([1.0, -2.0, 1.0], cast(Any, (0, 1, 2)), shape=(n-2, n))

def hp_filter(y, lam):
    n = len(y)
    
    D2 = D2_sparse(n)
    
    A = eye(n, format="csc") + lam * (D2.T @ D2)
    
    trend = spsolve(A, y)
    
    cycle = y - trend

    return np.array(trend), np.array(cycle)