from collections import defaultdict
from typing import Dict, Generic, List, NamedTuple, Sequence, Tuple, TypeVar

import matplotlib.pyplot as plt
import numpy as np
from typing_extensions import Protocol

XT_co = TypeVar("XT_co", covariant=True)
X_co = TypeVar("X_co", covariant=True)
Y_co = TypeVar("Y_co", covariant=True)

XT_contra = TypeVar("XT_contra", contravariant=True)
X_contra = TypeVar("X_contra", contravariant=True)
Y_contra = TypeVar("Y_contra", contravariant=True)


class Simulator(Protocol[XT_co, Y_co]):
    def sample(self) -> Tuple[XT_co, Y_co]:
        """
        Take a sample from the simulation.

        Returns
        -------

        Tuple[XT, Y]
            XT : true cause of observation Y
            Y  : observation

        """
        pass


class Predictor(Protocol[X_co, Y_contra]):
    def predict(self, y: Y_contra) -> X_co:
        """
        Infer the cause X of an observation Y

        Parameters
        ----------

        y : Y
            observation

        Returns
        -------

        X
            inferred cause of observation `y`

        """
        pass


class Loss(Protocol[XT_contra, X_contra]):
    def loss(self, xt: XT_contra, x: X_contra) -> float:
        """
        Loss associated to predicting x given a true value xt

        Parameters
        ----------

        xt: XT
            true value
        x: X
            inferred value

        Returns
        -------

        float
            loss

        """
        pass


XT = TypeVar("XT")
X = TypeVar("X")
Y = TypeVar("Y")


class Sample(NamedTuple, Generic[XT, X, Y]):
    xt: XT
    y: Y
    predictions: Sequence[Tuple[X, float]]


class Experiment(Generic[XT, X, Y]):
    def __init__(
        self,
        sim: Simulator[XT, Y],
        predictors: Sequence[Predictor[X, Y]],
        loss: Loss[XT, X],
    ):
        self.sim = sim
        self.predictors = predictors
        self.loss = loss

    def sample(self) -> Sample:
        xt, y = self.sim.sample()
        predictions: List[Tuple[X, float]] = []
        for predictor in self.predictors:
            x = predictor.predict(y)
            loss = self.loss.loss(xt, x)
            predictions.append((x, loss))
        return Sample(xt, y, predictions)


class Runner(Generic[XT, X, Y]):
    def __init__(self, expt: Experiment[XT, X, Y]):
        self.expt = expt
        self.samples: List[Sample] = []

    def run(self, num: int):
        for _ in range(num):
            sample = self.expt.sample()
            self.samples.append(sample)

    def get_losses_dict(self) -> Dict[str, List[float]]:
        losses_dict: Dict[str, List[float]] = defaultdict(list)
        names = [pred.__class__.__name__ for pred in self.expt.predictors]
        for sample in self.samples:
            for name, (_, loss) in zip(names, sample.predictions):
                losses_dict[name].append(loss)

        return losses_dict

    def print_summary(self):
        losses_dict = self.get_losses_dict()

        for name, losses in sorted(losses_dict.items()):
            print(name, np.mean(losses), np.std(losses))

    def plot_summary(self):
        losses_dict = self.get_losses_dict()
        names = []
        loss_arrays = []

        for name, losses in sorted(losses_dict.items()):
            names.append(name)
            loss_arrays.append(np.array(losses))

        pos = range(len(names))

        fig = plt.figure()
        ax = fig.add_subplot(111)

        ax.violinplot(loss_arrays, pos)

        ax.set_xticks(pos)
        ax.set_xticklabels(names)

        ax.set_ylabel("loss")
        plt.show()
