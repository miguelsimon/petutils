"""
Plot petalo sensors, hits and activated sensors.
"""

import argparse
import random
from typing import Dict

import h5py
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
from pandas import DataFrame


def plot_xyz(ax: Axes, pos: DataFrame, c: str, alpha: float):
    """
    Parameters
    ----------

    ax : matplotlib.axes.Axes
        target for plotting
    pos : DataFrame
        a dataframe containing x, y, z positions
    c : str
        color eg. "green"
    alpha : float
        transparency
    """
    ax.scatter(pos["x"], pos["y"], pos["z"], c=c, alpha=alpha)


class Plotter:
    """
    Given an h5 file eg. full_ring_iradius165mm_depth3cm_pitch7mm_new_h5.001.pet.h5
    extract events and plot a random one. Meant to illustrate the use of the
    functions and for testing.
    """

    def __init__(self, filename: str):
        with h5py.File(filename, "r") as f:
            self.positions = DataFrame(f["MC"]["sensor_positions"][:])
            hits = DataFrame(f["MC"]["hits"][:])
            waveforms = DataFrame(f["MC"]["waveforms"][:])

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

        self.event_ids = list(set(self.hits.keys()).intersection(self.waveforms.keys()))

    def plot_random_event(self):
        event_id = random.choice(self.event_ids)
        self.plot(event_id)

    def plot(self, event_id: int):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")
        plot_xyz(ax, self.positions, c="green", alpha=0.1)

        hits = self.hits[event_id]
        waveforms = self.waveforms[event_id]

        plot_xyz(ax, hits, c="red", alpha=1)
        plot_xyz(ax, waveforms, c="blue", alpha=0.5)

        plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("command", choices=["plot_rnd"], help="command to execute")

    parser.add_argument(
        "--hdf5_file",
        required=True,
        help="hdf5 file containing mc data eg. full_ring_iradius165mm_depth3cm_pitch7mm_new_h5.001.pet.h5",
    )

    args = parser.parse_args()

    plotter = Plotter(args.hdf5_file)
    plotter.plot_random_event()
