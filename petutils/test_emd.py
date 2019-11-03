import unittest

import numpy as np

from petutils.emd import emd, sparse_emd


class Test(unittest.TestCase):
    def test_1d_emd(self):
        x = np.array([1.0])
        y = np.array([1.0])
        xy_dist = np.array([[1.0]])

        dist, _ = emd(x, y, xy_dist)

        self.assertTrue(np.allclose(dist, 1))

    def test_2d_emd(self):
        x = np.array([1.0, 0.0])
        y = np.array([0.0, 1.0])
        xy_dist = np.array([[0.0, 1], [1.0, 0]])

        dist, _ = emd(x, y, xy_dist)
        self.assertTrue(np.allclose(dist, 1))

        dist, _ = emd(x, x, xy_dist)
        self.assertTrue(np.allclose(dist, 0))

    def test_sparse_emd(self):
        x = np.array([1.0])
        x_points = np.array([[0.0]])

        y = np.array([1.0])
        y_points = np.array([[1.0]])

        dist, _ = sparse_emd(x, x_points, y, y_points)
        self.assertTrue(np.allclose(dist, 1))

        dist, _ = sparse_emd(x, x_points, y, x_points)
        self.assertTrue(np.allclose(dist, 0))

        dist, _ = sparse_emd(x, x_points, y, np.array([[10.0]]))
        self.assertTrue(np.allclose(dist, 10))
