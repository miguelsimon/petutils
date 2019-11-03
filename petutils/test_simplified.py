import unittest

import numpy as np
from pandas import DataFrame

from petutils.simplified import (
    XT,
    BarycenterPredictor,
    EMDLoss,
    RndMarginalPredictor,
    Simulator,
    X,
    Y,
)

positions = DataFrame({"sensor_id": [0], "x": [10.0], "y": [10.0], "z": [10.0]})

hits = DataFrame({"event_id": [0], "x": [1.0], "y": [1.0], "z": [1.0], "energy": [1.0]})

waveforms = DataFrame({"sensor_id": [0], "event_id": [0], "charge": [20.0]})

ext_waveforms = waveforms.join(positions.set_index("sensor_id"), on="sensor_id")


class Test(unittest.TestCase):
    def test_constructors(self):
        print(XT(hits))
        print(Y(ext_waveforms))
        print(RndMarginalPredictor(hits))

    def test_simulator(self):
        sim = Simulator(positions, hits, waveforms)
        xt, y = sim.sample()
        print(xt, y)

    def test_emd_loss(self):
        loss = EMDLoss()

        xt = XT(hits)
        x_eq = X(np.array([1.0, 1.0, 1.0]))

        self.assertAlmostEqual(loss.loss(xt, x_eq), 0)

        x_neq = X(np.array([1.0, 1, 0.0]))
        self.assertAlmostEqual(loss.loss(xt, x_neq), 1)

    def test_rnd_marginal_predictor(self):
        pred = RndMarginalPredictor(hits)
        y = Y(ext_waveforms)
        x = pred.predict(y)
        print(x)

    def test_barycenter_predictor(self):
        pred = BarycenterPredictor()
        y = Y(ext_waveforms)
        x = pred.predict(y)

        self.assertTrue(np.allclose(x.xyz, [10, 10, 10]))
