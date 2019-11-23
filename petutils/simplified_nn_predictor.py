from typing import Mapping

import numpy as np
from numpy import ndarray

from petutils.simplified import XT, Y


def xt_to_point_estimate(xt: XT) -> ndarray:
    """
    Transforms a density to an approximate point estimate density

    Parameters
    ----------

    xt : XT
        density

    Returns
    -------

    ndarray
        x, y, z coordinates of the point density estimate

    """

    energy = np.array(xt.df["energy"])
    density = energy / np.sum(energy)
    points = np.array(xt.df[["x", "y", "z"]])

    x = np.sum(points[:, 0] * density)
    y = np.sum(points[:, 1] * density)
    z = np.sum(points[:, 2] * density)

    return np.array([x, y, z])


def y_to_dense(idx: Mapping[int, int], y: Y) -> ndarray:
    """
    Transform a sparse sensor response to a dense array

    Parameters
    ----------

    idx : Mapping[int, int]
        maps sensor ids to sensor indices in the dense array
    y : Y
        sensor counts

    Returns
    -------

    ndarray
        dense array of sensor counts

    """
    ids = y.df["sensor_id"]
    charge = y.df["charge"]

    indices = [idx[id] for id in ids]

    res = np.zeros(len(idx))

    np.add.at(res, indices, charge)

    return res
