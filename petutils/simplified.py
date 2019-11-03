"""
To test drive the approach, we'll implement a simplified version of the problem
where we ignore the time dimension and restrict our density predictions to a single point.
"""


import random
from typing import Dict, Tuple

import matplotlib.pyplot as plt
import numpy as np
import scipy.spatial
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
from numpy import ndarray
from pandas import DataFrame


class XT:
    """
    Causes are hit energy distributions integrated over time. We can represent
    them by taking the hits DataFrame and ignoring everything except x, y, z
    and energy.
    """

    def __init__(self, df: DataFrame):
        self.df = df
        for col in "x y z energy".split():
            assert col in df


class X:
    """
    This simplified model emits a single point estimate for where the event
    occurred.
    """

    def __init__(self, xyz: ndarray):
        self.xyz = xyz


class Y:
    """
    Observations are counts integrated over time, we can represent them by
    taking the waveforms DataFrame and ignoring everything except sensor_id,
    charge columns (as they all fall in the 0 time bin)

    We also denormalize x, y, z coords of sensors to this to make stuff more convenient
    """

    def __init__(self, df: DataFrame):
        self.df = df
        for col in "sensor_id charge x y z".split():
            assert col in df


class Simulator:
    def __init__(self, positions: DataFrame, hits: DataFrame, waveforms: DataFrame):
        self.positions = positions

        self.hits: Dict[int, DataFrame] = {}
        for event_id, df in hits.groupby("event_id"):
            self.hits[event_id] = df

        # make x, y, z coordinates easy to access for counts
        ext_waveforms = waveforms.join(
            self.positions.set_index("sensor_id"), on="sensor_id"
        )

        self.waveforms: Dict[int, DataFrame] = {}
        for event_id, df in ext_waveforms.groupby("event_id"):
            self.waveforms[event_id] = df

        self.event_ids = sorted(
            set(self.hits.keys()).intersection(self.waveforms.keys())
        )

        # current index into event_ids
        self.cur = 0

    def sample(self) -> Tuple[XT, Y]:
        event_id = self.event_ids[self.cur]

        xt = XT(self.hits[event_id])
        y = Y(self.waveforms[event_id])

        self.cur += 1
        return xt, y


class EMDLoss:
    def loss(self, xt: XT, x: X) -> float:
        """
        Earth mover's distance between the real energy distribution and the
        predicted energy distribution, which is simply all probability mass
        at the predicted point.

        Special casing the calculation instead of using the generalized emd.py
        code because that fails in some cases, either because my implementation
        is buggy or because I hit a scipy.optimize.linprog bug.
        """

        xt_energy = np.array(xt.df["energy"])
        xt_density = xt_energy / np.sum(xt_energy)

        xt_points = np.array(xt.df[["x", "y", "z"]])

        x_points = np.array([x.xyz])

        xy_dist = scipy.spatial.distance_matrix(xt_points, x_points, 2)
        xy_dist = xy_dist.transpose()[0]

        emd = np.sum(xy_dist * xt_density)

        return emd


class DumbPredictor:
    def predict(self, _y: Y) -> X:
        return X(np.array([0.0, 0.0, 0.0]))


class RndMarginalPredictor:
    """
    Samples random points from the energy deposition marginal distribution not
    conditioned on Y in any way
    """

    def __init__(self, hits: DataFrame):
        self.positions = np.array(hits[["x", "y", "x"]])

    def predict(self, _y: Y) -> X:
        return X(random.choice(self.positions))


class BarycenterPredictor:
    """
    Calculate the weighted mean point. Crude because:
    * doesn't take end effects at the cylinder edges into account
    * constrained to predicting a single point
    """

    def predict(self, y: Y) -> X:
        charge = np.array(y.df["charge"])
        density = charge / np.sum(charge)

        points = np.array(y.df[["x", "y", "z"]])

        x = np.sum(points[:, 0] * density)
        y = np.sum(points[:, 1] * density)
        z = np.sum(points[:, 2] * density)

        return X(np.array([x, y, z]))


class Plotter:
    def __init__(self, positions: DataFrame):
        self.positions = positions

    def plot_sample(self, xt: XT, x: X, y: Y):
        """
        Visualize:
            hits (red dots)
            detectors (blue dots)
            activated detectors(green dots)
            prediction (black pyramid)

        Parameters
        ----------

        xt : XT
            hits
        x : X
            prediction
        y : Y
            sensor data
        """

        fig = plt.figure()

        ax = fig.add_subplot(111, projection="3d")

        pos = self.positions

        # draw sensors
        ax.scatter(pos["x"], pos["y"], pos["z"], c="blue", alpha=0.1)

        # draw hits
        ax.scatter(xt.df["x"], xt.df["y"], xt.df["z"], c="red", alpha=1.0)

        # draw counts
        ax.scatter(y.df["x"], y.df["y"], y.df["z"], c="green", alpha=0.5)

        # draw prediction
        ax.scatter([x.xyz[0]], [x.xyz[1]], [x.xyz[2]], c="black", alpha=1.0, marker="^")
