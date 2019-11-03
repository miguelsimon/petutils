from typing import List, Tuple

import numpy as np
from numpy import ndarray

from petutils.experiment import Experiment, Predictor

X_MIN, X_MAX = 0.0, 1.0
STD = 0.1


class X:
    """
    A point
    """

    def __init__(self, x: float):
        self.x = x


# XT and X are the same in this case
XT = X


class Y:
    """
    An observation is a series of points
    """

    def __init__(self, xs: ndarray):
        self.xs = xs


class Simulator:
    """
    An observation is generated by sampling from a gaussian centered on the
    X point and adding a noise point sampled from a uniform distribution
    """

    def sample(self) -> Tuple[XT, Y]:
        xt = X(np.random.uniform(X_MIN, X_MAX))

        noise_x = np.random.uniform(X_MIN, X_MAX)

        xs = np.append(np.random.normal(xt.x, STD, 10), noise_x)

        y = Y(xs)
        return xt, y


class Loss:
    def loss(self, xt: XT, x: X) -> float:
        return np.abs(xt.x - x.x)


class DumbPredictor:
    """
    The nullary predictor always returns 0
    """

    def predict(self, y: Y) -> X:
        return X(0)


class MeanPredictor:
    """
    The mean predictor calculates the means of the observations
    """

    def predict(self, y: Y) -> X:
        return X(y.xs.mean())


def get_experiment():
    sim = Simulator()
    loss = Loss()
    predictors: List[Predictor] = [DumbPredictor(), MeanPredictor()]

    return Experiment(sim, predictors, loss)