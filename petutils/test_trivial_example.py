import unittest

from petutils.experiment import Runner
from petutils.trivial_example import get_experiment


class Test(unittest.TestCase):
    def test_sample(self):
        expt = get_experiment()
        sample = expt.sample()
        print(sample)

    def test_summary(self):
        expt = get_experiment()
        runner = Runner(expt)
        runner.run(20)

        runner.print_summary()
