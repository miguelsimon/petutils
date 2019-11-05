from typing import NamedTuple

import numpy as np
import scipy.optimize
import scipy.spatial
from numpy import ndarray


class LinProg(NamedTuple):
    """
    Follows convention in https://docs.scipy.org/doc/scipy-1.1.0/reference/generated/scipy.optimize.linprog.html#scipy.optimize.linprog
    """

    c: ndarray
    A_ub: ndarray
    b_ub: ndarray
    A_eq: ndarray
    b_eq: ndarray

    def solve_scipy(self):
        return scipy.optimize.linprog(
            c=self.c,
            A_eq=self.A_eq,
            b_eq=self.b_eq,
            A_ub=self.A_ub,
            b_ub=self.b_ub,
            bounds=None,
        )


def emd(x, y, xy_dist):
    """
    Calculates earth movers' distance between two densities x and y

    Parameters
    ----------

    x : ndarray
        1 - dimensional array of weights
    y : ndarray
        1 - dimensional array of weights
    xy_dist : ndarray
        2 - dimensional array containing distances between x and y density coordinates

    Returns
    -------

    float
        earth movers' distance
    ndarray
        moves required to move x onto y

    This implementation doesn't exploit the sparsity in the A_eq matrix.

    """

    linprog = to_linprog(x, y, xy_dist)
    res = linprog.solve_scipy()
    assert res["success"]
    return res["fun"], res["x"].reshape(xy_dist.shape)


def to_linprog(x, y, xy_dist) -> LinProg:
    """

    Parameters
    ----------

    x : ndarray
        1 - dimensional array of weights
    y : ndarray
        1 - dimensional array of weights
    xy_dist : ndarray
        2 - dimensional array containing distances between x and y density coordinates

    Returns
    -------

    LinProg

    This was sometimes flaking out when called with single-precision matrices
    because of numerical instability in the scipy _presolve step when eliminating
    redundant constraints, so ensure sufficient precision

    TODO: use sparse A_eq, A_ub matrices

    """

    # constant used in scipy.optimize._remove_redundancy
    tol = 1e-8

    assert np.abs(x.sum() - y.sum()) < tol, "x and y must be close to avoid instability"
    assert xy_dist.shape[0] == x.shape[0]
    assert xy_dist.shape[1] == y.shape[0]

    x_dim = x.shape[0]
    y_dim = y.shape[0]

    c = xy_dist.flatten()

    A_eq = []
    b_eq = []

    for i in range(x_dim):
        constraint = np.zeros(xy_dist.shape)
        constraint[i] = 1.0
        A_eq.append(constraint.flatten())
        b_eq.append(x[i])

    for i in range(y_dim):
        constraint = np.zeros(xy_dist.shape)
        constraint[:, i] = 1.0
        A_eq.append(constraint.flatten())
        b_eq.append(y[i])

    A_ub = np.diag(-np.ones(x_dim * y_dim))
    b_ub = np.zeros(x_dim * y_dim)

    return LinProg(c=c, A_ub=A_ub, b_ub=b_ub, A_eq=np.array(A_eq), b_eq=np.array(b_eq))


def sparse_emd(x, x_points, y, y_points, p=2):
    """
    Calculates earth movers' distance between two densities x and y.

    Parameters
    ----------

    x : ndarray
        1 - dimensional array of weights
    x_points : ndarray
        (x.shape[0], n) - shaped array of points
    y : ndarray
        1 - dimensional array of weights
    y_points : ndarray
        (y.shape[0], n) - shaped array of points
    p : int
        minkowski p-norm

    Returns
    -------

    float
        earth movers' distance
    ndarray
        moves required to move x onto y

    """

    xy_dist = scipy.spatial.distance_matrix(x_points, y_points, p)

    return emd(x, y, xy_dist)
