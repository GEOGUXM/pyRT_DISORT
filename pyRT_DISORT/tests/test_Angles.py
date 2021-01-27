from pyRT_DISORT.observation import Angles
from unittest import TestCase
import numpy as np
import numpy.testing as npt


class TestAngles(TestCase):
    def setUp(self) -> None:
        self.angles = Angles


class TestIncidence(TestAngles):
    def test_float_incidence_angles_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            Angles(1, np.ndarray([1]), np.ndarray([1]))

    def test_2d_incidence_angles_raises_type_error(self) -> None:
        with self.assertRaises(ValueError):
            a = np.ones((10, 5))
            Angles(a, np.ndarray([1]), np.ndarray([1]))

    def test_incidence_angles_outside_0_to_180_raises_value_error(self) -> None:
        dummy_angles = np.array([1])
        Angles(np.array([0]), dummy_angles, dummy_angles)
        Angles(np.array([180]), dummy_angles, dummy_angles)
        with self.assertRaises(ValueError):
            test_angle = np.array([np.nextafter(0, -1)])
            Angles(test_angle, dummy_angles, dummy_angles)
        with self.assertRaises(ValueError):
            test_angle = np.array([np.nextafter(181, 181)])
            Angles(test_angle, dummy_angles, dummy_angles)

    def test_oddly_shaped_incidence_angles_raises_value_error(self) -> None:
        dummy_angles = np.array([20, 30])
        with self.assertRaises(ValueError):
            Angles(np.array([20]), dummy_angles, dummy_angles)

    def test_emission_angles_is_read_only(self) -> None:
        with self.assertRaises(AttributeError):
            test_angles = np.array([20])
            a = Angles(test_angles, test_angles, test_angles)
            a.incidence = test_angles


class TestEmission(TestAngles):
    def test_float_emission_angles_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            Angles(np.ndarray([1]), 1, np.ndarray([1]))

    def test_2d_emission_angles_raises_type_error(self) -> None:
        with self.assertRaises(ValueError):
            a = np.ones((10, 5))
            Angles(np.ndarray([1]), a, np.ndarray([1]))

    def test_emission_angles_outside_0_to_90_raises_value_error(self) -> None:
        dummy_angles = np.array([1])
        Angles(dummy_angles, np.array([0]), dummy_angles)
        Angles(dummy_angles, np.array([90]), dummy_angles)
        with self.assertRaises(ValueError):
            test_angle = np.array([np.nextafter(0, -1)])
            Angles(dummy_angles, test_angle, dummy_angles)
        with self.assertRaises(ValueError):
            test_angle = np.array([np.nextafter(90, 91)])
            Angles(dummy_angles, test_angle, dummy_angles)

    def test_oddly_shaped_emission_angles_raises_value_error(self) -> None:
        dummy_angles = np.array([20, 30])
        with self.assertRaises(ValueError):
            Angles(dummy_angles, np.array([20]), dummy_angles)

    def test_emission_angles_is_read_only(self) -> None:
        with self.assertRaises(AttributeError):
            test_angles = np.array([20])
            a = Angles(test_angles, test_angles, test_angles)
            a.emission = test_angles


class TestPhase(TestAngles):
    def test_float_phase_angles_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            Angles(np.ndarray([1]), np.ndarray([1]), 1)

    def test_2d_phase_angles_raises_type_error(self) -> None:
        with self.assertRaises(ValueError):
            a = np.ones((10, 5))
            Angles(np.ndarray([1]), np.ndarray([1]), a)

    def test_phase_angles_outside_0_to_90_raises_value_error(self) -> None:
        dummy_angles = np.array([1])
        Angles(dummy_angles, dummy_angles, np.array([0]))
        Angles(dummy_angles, dummy_angles, np.array([180]))
        with self.assertRaises(ValueError):
            test_angle = np.array([np.nextafter(0, -1)])
            Angles(dummy_angles, dummy_angles, test_angle)
        with self.assertRaises(ValueError):
            test_angle = np.array([np.nextafter(180, 181)])
            Angles(dummy_angles, dummy_angles, test_angle)

    def test_oddly_shaped_phase_angles_raises_value_error(self) -> None:
        dummy_angles = np.array([20, 30])
        with self.assertRaises(ValueError):
            Angles(dummy_angles, dummy_angles, np.array([20]))

    def test_phase_angles_is_read_only(self) -> None:
        with npt.assert_raises(AttributeError):
            test_angles = np.array([20])
            a = Angles(test_angles, test_angles, test_angles)
            a.phase = test_angles


class TestMu0(TestAngles):
    def test_mu0_passes_test_cases(self):
        dummy_angles = np.array([20])

        a = Angles(np.array([0]), dummy_angles, dummy_angles)
        npt.assert_equal(1, a.mu0)

        a = Angles(np.array([45]), dummy_angles, dummy_angles)
        npt.assert_equal(np.sqrt(2) / 2, a.mu0)

        a = Angles(np.array([60]), dummy_angles, dummy_angles)
        npt.assert_almost_equal(0.5, a.mu0)

        a = Angles(np.array([90]), dummy_angles, dummy_angles)
        npt.assert_almost_equal(0, a.mu0)

    def test_mu0_is_read_only(self):
        dummy_angles = np.array([20])
        a = Angles(dummy_angles, dummy_angles, dummy_angles)
        with npt.assert_raises(AttributeError):
            a.mu0 = dummy_angles

    def test_mu0_is_same_shape_as_incidence_angles(self):
        dummy_angles = np.array([20])
        a = Angles(dummy_angles, dummy_angles, dummy_angles)
        npt.assert_equal(a.incidence.shape, a.mu0.shape)


class TestMu(TestAngles):
    def test_mu_passes_test_cases(self):
        dummy_angles = np.array([20])

        a = Angles(dummy_angles, np.array([0]), dummy_angles)
        npt.assert_equal(1, a.mu)

        a = Angles(dummy_angles, np.array([45]), dummy_angles)
        npt.assert_equal(np.sqrt(2) / 2, a.mu)

        a = Angles(dummy_angles, np.array([60]), dummy_angles)
        npt.assert_almost_equal(0.5, a.mu)

        a = Angles(dummy_angles, np.array([90]), dummy_angles)
        npt.assert_almost_equal(0, a.mu)

    def test_mu_is_read_only(self):
        dummy_angles = np.array([20])
        a = Angles(dummy_angles, dummy_angles, dummy_angles)
        with npt.assert_raises(AttributeError):
            a.mu = dummy_angles

    def test_mu0_is_same_shape_as_emission_angles(self):
        dummy_angles = np.array([20])
        a = Angles(dummy_angles, dummy_angles, dummy_angles)
        npt.assert_equal(a.emission.shape, a.mu.shape)


class TestPhi0(TestAngles):
    def test_phi0_is_always_0(self):
        dummy_angles = np.array([20])
        a = Angles(dummy_angles, dummy_angles, dummy_angles)
        self.assertTrue(np.all(a.phi0 == 0))

    def test_phi0_is_read_only(self):
        dummy_angles = np.array([20])
        a = Angles(dummy_angles, dummy_angles, dummy_angles)
        with npt.assert_raises(AttributeError):
            a.phi0 = dummy_angles

    def test_phi0_is_same_shape_as_phase_angles(self):
        dummy_angles = np.array([20])
        a = Angles(dummy_angles, dummy_angles, dummy_angles)
        npt.assert_equal(a.phase.shape, a.phi0.shape)


class TestPhi(TestAngles):
    def test_phi_matches_disort_multi_computations(self):
        a = Angles(np.array([0]), np.array([0]), np.array([0]))
        npt.assert_almost_equal(np.array([0]), a.phi, decimal=5)

        a = Angles(np.array([10]), np.array([10]), np.array([10]))
        npt.assert_almost_equal(np.array([119.747139]), a.phi, decimal=4)

        a = Angles(np.array([70]), np.array([70]), np.array([70]))
        npt.assert_almost_equal(np.array([104.764977]), a.phi, decimal=4)

    def test_phi_is_read_only(self):
        dummy_angles = np.array([20])
        a = Angles(dummy_angles, dummy_angles, dummy_angles)
        with npt.assert_raises(AttributeError):
            a.phi = dummy_angles

    def test_phi_is_same_shape_as_phase_angles(self):
        dummy_angles = np.array([20])
        a = Angles(dummy_angles, dummy_angles, dummy_angles)
        npt.assert_equal(a.phase.shape, a.phi.shape)