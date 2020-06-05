

import unittest
import numpy as np
from procrustes.base import Procrustes
from procrustes.base_utils import zero_padding, hide_zero_padding_array, translate_array_to_origin, scale_array, is_diagonalizable, frobenius_norm, centroid, eigenvalue_decomposition


class Test(unittest.TestCase):

    def test_zero_padding_rows(self):
        """
        This test verifies that zero_padding_array applied to two arrays with a differing number of rows
        returns the two input arrays, where the array with the least number of rows is zero padded so that
        it matches the number of rows of the other array
        """
        array1 = np.array([[1, 2], [3, 4]])
        array2 = np.array([[5, 6]])
        procrust = Procrustes(array1, array2)
        # match the number of rows of the 2nd array (automatically down when initiating the class)
        assert array1.shape == (2, 2)
        assert array2.shape == (1, 2)
        assert procrust.array_a.shape == (2, 2)
        assert procrust.array_b.shape == (2, 2)
        expected = np.array([[5, 6], [0, 0]])
        assert (abs(procrust.array_a - array1) < 1.e-10).all()
        assert (abs(procrust.array_b - expected) < 1.e-10).all()

        # match the number of rows of the 1st array
        padded_array2, padded_array1 = zero_padding(array2, array1, row=True)
        assert array1.shape == (2, 2)
        assert array2.shape == (1, 2)
        assert padded_array1.shape == (2, 2)
        assert padded_array2.shape == (2, 2)
        assert (abs(padded_array1 - array1) < 1.e-10).all()
        assert (abs(padded_array2 - expected) < 1.e-10).all()

        # match the number of rows of the 1st array
        array3 = np.arange(8).reshape(2, 4)
        array4 = np.arange(8).reshape(4, 2)
        padded_array3, padded_array4 = zero_padding(array3, array4, row=True)
        assert array3.shape == (2, 4)
        assert array4.shape == (4, 2)
        assert padded_array3.shape == (4, 4)
        assert padded_array4.shape == (4, 2)
        assert (abs(array4 - padded_array4) < 1.e-10).all()
        expected = list(range(8))
        expected.extend([0]*8)
        expected = np.array(expected).reshape(4, 4)
        assert (abs(expected - padded_array3) < 1.e-10).all()

        # padding the padded_arrays should not change anything
        padded_array5, padded_array6 = zero_padding(padded_array3, padded_array4, row=True)
        assert padded_array3.shape == (4, 4)
        assert padded_array4.shape == (4, 2)
        assert padded_array5.shape == (4, 4)
        assert padded_array6.shape == (4, 2)
        assert (abs(padded_array5 - padded_array3) < 1.e-10).all()
        assert (abs(padded_array6 - padded_array4) < 1.e-10).all()

    # -----------------------------------------------------------------

    def test_zero_padding_columns(self):
        """
        This test verifies that zero_padding_array applied to two arrays with a differing number of columns
        returns the two input arrays, where the array with the least number of columns is zero padded so that
        it matches the number of rows of the other array.
        """
        array1 = np.array([[4, 7, 2], [1, 3, 5]])
        array2 = np.array([[5], [2]])
        procrust = Procrustes(array1, array2)
        assert array1.shape == (2, 3)
        assert array2.shape == (2, 1)
        assert procrust.array_a.shape == (2, 3)
        assert procrust.array_b.shape == (2, 1)
        expected = np.array([[5, 0, 0], [2, 0, 0]])
        assert (abs(procrust.array_a - array1) < 1.e-10).all()
        assert (abs(procrust.array_b - array2) < 1.e-10).all()

        # match the number of columns of the 1st array
        padded_array2, padded_array1 = zero_padding(array2, array1, column=True)
        assert array1.shape == (2, 3)
        assert array2.shape == (2, 1)
        assert padded_array1.shape == (2, 3)
        assert padded_array2.shape == (2, 3)
        assert (abs(padded_array1 - array1) < 1.e-10).all()
        assert (abs(padded_array2 - expected) < 1.e-10).all()

        # match the number of columns of the 1st array
        array3 = np.arange(8).reshape(8, 1)
        array4 = np.arange(8).reshape(2, 4)
        padded_array3, padded_array4 = zero_padding(array3, array4, row=False, column=True)
        assert array3.shape == (8, 1)
        assert array4.shape == (2, 4)
        assert padded_array3.shape == (8, 4)
        assert padded_array4.shape == (2, 4)
        assert (abs(array4 - padded_array4) < 1.e-10).all()
        expected = list(range(8))
        expected.extend([0]*24)
        expected = np.array(expected).reshape(4, 8).T
        assert (abs(expected - padded_array3) < 1.e-10).all()

        # padding the padded_arrays should not change anything
        padded_array5, padded_array6 = zero_padding(padded_array3, padded_array4, row=False, column=True)
        assert padded_array3.shape == (8, 4)
        assert padded_array4.shape == (2, 4)
        assert padded_array5.shape == (8, 4)
        assert padded_array6.shape == (2, 4)
        assert (abs(padded_array5 - padded_array3) < 1.e-10).all()
        assert (abs(padded_array6 - padded_array4) < 1.e-10).all()

    # ----------------------------------------------

    def test_zero_padding_square(self):
        """
        This test verifies that zero_padding_array applied to two arrays with a differing number of rows
        and/or columns returns the two input arrays are zero-padded in both with both rows an columns so
        as to return two square arrays of equal size.
        """

        # Try two equivalent (but different sized) symmetric arrays
        sym_array1 = np.array([[60,  85,  86], [85, 151, 153], [86, 153, 158]])
        sym_array2 = np.array([[60,  85,  86, 0, 0], [85, 151, 153, 0, 0], [86, 153, 158, 0, 0], [0, 0, 0, 0, 0]])
        assert(sym_array1.shape != sym_array2.shape)
        square_1, square_2 = zero_padding(sym_array1, sym_array2, square=True)
        assert(square_1.shape == square_2.shape)
        assert(square_1.shape[0] == square_1.shape[1])

        # Performing the analysis on equally sized square arrays should return the same input arrays
        sym_part = np.array([[1, 7, 8, 4], [6, 4, 8, 1]])
        sym_array1 = np.dot(sym_part, sym_part.T)
        sym_array2 = sym_array1
        assert(sym_array1.shape == sym_array2.shape)
        square_1, square_2 = zero_padding(sym_array1, sym_array2, row=False, column=False, square=True)
        assert(square_1.shape == square_2.shape)
        assert(square_1.shape[0] == square_1.shape[1])
        assert(abs(sym_array2 - sym_array1) < 1.e-10).all()

    # -------------------------------------------

    def test_hide_zero_padding_array(self):
        """
        This test verifies that applying hide_zero_padding_array to an array padded with
        zeros will return the original (unpadded) array.
        """

        # Define an arbitrary array
        array0 = np.array([[1, 6, 7, 8], [5, 7, 22, 7]])
        # Create (arbitrary) pads to add onto the permuted input array, array_permuted
        m, n = array0.shape
        arb_pad_col = 27
        arb_pad_row = 13
        pad_vertical = np.zeros((m, arb_pad_col))
        pad_horizontal = np.zeros((arb_pad_row, n+arb_pad_col))
        array1 = np.concatenate((array0, pad_vertical), axis=1)
        array1 = np.concatenate((array1, pad_horizontal), axis=0)
        # Assert array has been zero padded
        assert(array0.shape != array1.shape)
        # Confirm that after hide_zero_padding has been applied, the arrays are of equal size and
        # are identical
        hide_array0 = hide_zero_padding_array(array0)
        hide_array1 = hide_zero_padding_array(array1)
        assert(hide_array0.shape == hide_array1.shape)
        assert(abs(hide_array0 - hide_array1) < 1.e-10).all()
        # Define an arbitrary array
        array0 = np.array([[124.25, 625.15, 725.64, 158.51], [536.15, 367.63, 322.62, 257.61],
                           [361.63, 361.63, 672.15, 631.63]])
        # Create (arbitrary) pads to add onto the permuted input array, array_permuted
        m, n = array0.shape
        arb_pad_col = 14
        arb_pad_row = 19
        pad_vertical = np.zeros((m, arb_pad_col))
        pad_horizontal = np.zeros((arb_pad_row, n+arb_pad_col))
        array1 = np.concatenate((array0, pad_vertical), axis=1)
        array1 = np.concatenate((array1, pad_horizontal), axis=0)
        # Assert array has been zero padded
        assert(array0.shape != array1.shape)
        # Confirm that after hide_zero_padding has been applied, the arrays are of equal size and
        # are identical
        hide_array0 = hide_zero_padding_array(array0)
        hide_array1 = hide_zero_padding_array(array1)
        assert(hide_array0.shape == hide_array1.shape)
        assert(abs(hide_array0 - hide_array1) < 1.e-10).all()

    # ----------------------------------------------------------

    def test_translate_array_to_origin(self):
        """
        This test shows the validity of the function translate_array_to_origin
        """

        """
        This test confirms that the centroid of array_a is translated to the origin after the analysis is applied
        (when array_b is none).
        """
        # Define an arbitrary nd array
        array_translated = np.array([[2, 4, 6, 10], [1, 3, 7, 0], [3, 6, 9, 4]])
        # Instantiate Procrustes class with arbitrary second argument
        # Find the means over each dimension
        column_means_translated = np.zeros(4)
        for i in range(4):
            column_means_translated[i] = np.mean(array_translated[:, i])
        # Confirm that these means are not all zero
        assert (abs(column_means_translated) > 1.e-8).all()
        # Compute the origin-centred array
        origin_centred_array, unused = translate_array_to_origin(array_translated)
        # Confirm that the column means of the origin-centred array are all zero
        column_means_centred = np.ones(4)
        for i in range(4):
            column_means_centred[i] = np.mean(origin_centred_array[:, i])
        assert (abs(column_means_centred) < 1.e-10).all()

        """
        This test verifies that translating an already centred array should return the original array.
        """
        centred_sphere = 25.25 * np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1], [-1, 0, 0], [0, -1, 0], [0, 0, -1]])
        predicted, unused = translate_array_to_origin(centred_sphere)
        expected = centred_sphere
        assert(abs(predicted - expected) < 1.e-8).all()

        """
        This test verifies that centering a translated unit sphere should return the original unit sphere
        """
        shift = np.array([[1, 4, 5], [1, 4, 5], [1, 4, 5], [1, 4, 5], [1, 4, 5], [1, 4, 5]])
        translated_sphere = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1], [-1, 0, 0], [0, -1, 0], [0, 0, -1]])\
            + shift
        predicted, unused = translate_array_to_origin(translated_sphere)
        expected = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1], [-1, 0, 0], [0, -1, 0], [0, 0, -1]])
        assert(abs(predicted - expected) < 1.e-8).all()

        """
        If an arbitrary array is centroid translated, the analysis applied to the original array
        and the translated array should give identical results
        """
        # Define an arbitrary array
        array_a = np.array([[1, 5, 7], [8, 4, 6]])
        # Define an arbitrary translation
        translate = np.array([[5, 8, 9], [5, 8, 9]])
        # Define the translated original array
        array_translated = array_a + translate
        # Begin translation analysis
        predicted1, unused = translate_array_to_origin(array_a)
        predicted2, unused = translate_array_to_origin(array_translated)
        assert(abs(predicted1 - predicted2) < 1.e-10).all()

    # -----------------------------------------------------

    def test_scale_array(self):

        """
        This test shows the validity of the function scale_array
        """
        """
        This test shows that when scale_array is applied to an array, the each point of the new array has
        unit norm.
        """
        # Rescale arbitrary array
        array = np.array([[6, 2, 1], [5, 2, 9], [8, 6, 4]])
        # Create (arbitrary second argument) Procrustes instance
        # Confirm Frobenius normaliation has transformed the array to lie on the unit sphere in
        # the R^(mxn) vector space. We must centre the array about the origin before proceeding
        array, unused = translate_array_to_origin(array)
        # Confirm proper centering
        column_means_centred = np.zeros(3)
        for i in range(3):
            column_means_centred[i] = np.mean(array[:, i])
        assert (abs(column_means_centred) < 1.e-10).all()
        # Proceed with Frobenius normalization
        scaled_array, unused = scale_array(array)
        # Confirm array has unit norm
        assert(abs(np.sqrt((scaled_array**2.).sum()) - 1.) < 1.e-10)
        """
        This test verifies that when scale_array is applied to two scaled unit spheres,
        the Frobenius norm of each new sphere is unity.
        """
        # Rescale spheres to unitary scale
        # Define arbitrarily scaled unit spheres
        unit_sphere = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1], [-1, 0, 0], [0, -1, 0], [0, 0, -1]])
        sphere_1 = 230.15 * unit_sphere
        sphere_2 = .06 * unit_sphere
        # Proceed with scaling procedure
        scaled1, unused = scale_array(sphere_1)
        scaled2, unused = scale_array(sphere_2)
        # Confirm each scaled array has unit Frobenius norm
        assert(abs(np.sqrt((scaled1**2.).sum()) - 1.) < 1.e-10)
        assert(abs(np.sqrt((scaled2**2.).sum()) - 1.) < 1.e-10)
        """
        If an arbitrary array is scaled, the scaling analysis should be able to recreate the scaled array from the original
        applied to the original array and the scaled array should give identical results.
        """
        # Define an arbitrary array
        array_a = np.array([[1, 5, 7], [8, 4, 6]])
        # Define an arbitrary scaling factor
        scale = 6.3
        # Define the scaled original array
        array_scaled = scale * array_a
        # Begin scaling analysis
        scaled_a, unused = scale_array(array_a, array_scaled)
        assert(abs(scaled_a - array_scaled) < 1.e-10).all()

        # Testing

        # Define an arbitrary array
        array = np.array([[6., 12., 16., 7.], [4., 16., 17., 33.], [5., 17., 12., 16.]])
        # Define the scaled original array
        array_scale = 123.45 * array
        # Verify the validity of the translate_scale analysis
        # Proceed with analysis, matching array_trans_scale to array
        predicted, unused = scale_array(array_scale, array)
        # array_trans_scale should be identical to array after the above analysis
        expected = array
        assert(abs(predicted - expected) < 1.e-10).all()

    # -------------------------------------------------------------

    def test_translate_scale_array(self):

        """
        This test verifies the validity of translate_scale_array.
        """
        """
        This test shows that performing translate_scale on an array multiple times
        always returns the same solution.
        """
        # Define an arbitrary array
        array = np.array([[5, 3, 2, 5], [7, 5, 4, 3]])
        # Proceed with the translate_scale process.
        predicted1 = translate_array_to_origin(array)[0]
        predicted1 = scale_array(predicted1)[0]
        predicted2 = translate_array_to_origin(predicted1)[0]
        predicted2 = scale_array(predicted2)[0]
        # Perform the process again using the already translated and scaled array as input
        assert(abs(predicted1 - predicted2) < 1.e-10).all()
        """
        This test shows that applying translate scale to an array which is translated
        and scaled is equal to applying translate_scale on the original array
        """
        # Define an arbitrary array
        array = np.array([[1., 4., 6., 7.], [4., 6., 7., 3.], [5., 7., 3., 1.]])
        # Define an arbitrary centroid shift
        shift = np.array([[1., 4., 6., 9.], [1., 4., 6., 9.], [1., 4., 6., 9.]])
        # Define the translated and scaled original array
        array_trans_scale = 14.76 * array + shift
        # Verify the validity of the translate_scale analysis
        # Returns an object with an origin centred centroid unit Frobenius norm
        predicted = translate_array_to_origin(array_trans_scale)[0]
        predicted = scale_array(predicted)[0]
        # Returns the same object, origin centred and unit Frobenius norm
        expected = translate_array_to_origin(array)[0]
        expected = scale_array(expected)[0]
        assert(abs(predicted - expected) < 1.e-10).all()
        """
        This test shows that applying translate scale to an array which is translated
        and scaled returns an array that is equal to the original
        """
        # Define an arbitrary array
        array = np.array([[6., 12., 16., 7.], [4., 16., 17., 33.], [5., 17., 12., 16.]])
        # Define an arbitrary centroid shift
        shift = np.array([[3., 7., 9., 1.], [3., 7., 9., 1.], [3., 7., 9., 1.]])
        # Define the translated and scaled original array
        array_trans_scale = 123.45 * array + shift
        # Verify the validity of the translate_scale analysis
        # Proceed with analysis, matching array_trans_scale to array
        predicted1 = translate_array_to_origin(array_trans_scale)[0]
        predicted1 = scale_array(predicted1)[0]
        predicted2 = translate_array_to_origin(array)[0]
        predicted2 = scale_array(predicted2)[0]
        # array_trans_scale should be identical to array after the above analysis
        assert(abs(predicted1 - predicted2) < 1.e-10).all()

    # ----------------------------------------------------

    def test_singular_value_decomposition(self):
        pass
        """
        This is a numpy function, please refer to their
        documents for their testing procedure
        """

    #------------------------------------------------------

    def test_eigenvalue_decomposition(self):
        """
        This test verifies the validity of the function eigenvalue_decomposition
        """

        """
        This test shows that if eigenvalue decomposition is doable
        (dimension of eigenspace = dimension of array) function should return the appropriate decomposition
        """
        array = np.array([[-1./2, 3./2], [3./2, -1./2]])
        assert(is_diagonalizable(array) is True)
        s_predicted, u_predicted = eigenvalue_decomposition(array)
        s_expected = np.array([1, -2])
        assert(abs(np.dot(u_predicted, u_predicted.T) - np.eye(2)) < 1.e-8).all()
        # The eigenvalue decomposition must return the original array
        predicted = np.dot(u_predicted, np.dot(np.diag(s_predicted), u_predicted.T))
        assert (abs(predicted - array) < 1.e-8).all()
        assert(abs(s_predicted - s_expected) < 1.e-8).all()
        """
        This test shows that the product of u, s, and u.T obtained from eigenvalue_decomposition yields the original
        array again.
        """
        array = np.array([[3, 1], [1, 3]])
        assert(is_diagonalizable(array) is True)
        s_predicted, u_predicted = eigenvalue_decomposition(array)
        s_expected = np.array([4, 2])
        assert(abs(np.dot(u_predicted, u_predicted.T) - np.eye(2)) < 1.e-8).all()
        # The eigenvalue decomposition must return the original array
        predicted = np.dot(u_predicted, np.dot(np.diag(s_predicted), u_predicted.T))
        assert (abs(predicted - array) < 1.e-8).all()
        assert(abs(s_predicted - s_expected) < 1.e-8).all()

    # ------------------------------------------------------

    def test_centroid(self):
        """
        This test shows that centroid is not scale-independent
        """
        """
        This test shows that the centroid of an array after translate_array_to_origin is applied is the origin.
        """
        # Define an arbitrary array
        array = np.array([[6., 12., 16., 7.], [4., 16., 17., 33.], [5., 17., 12., 16.]])
        array_centred, translate = translate_array_to_origin(array)
        assert(abs(centroid(array_centred)) < 1.e-10).all()

        # Define an arbitrary array
        array = np.array([[6325.26, 1232.46, 1356.75, 7351.64], [4351.36, 1246.63, 1247.63, 3243.64]])
        array_centred, translate = translate_array_to_origin(array)
        assert(abs(centroid(array_centred)) < 1.e-10).all()
        """
        Even if the array is zero-padded, the correct translation about the origin is obtained.
        """
        # Define an arbitrary, zero-padded array
        array = np.array([[1.5294e-4, 1.242e-5, 1.624e-3, 7.35e-4], [4.534e-5, 1.652e-5, 1.725e-5, 3.314e-4],
                          [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]])
        array_centred, translate = translate_array_to_origin(array)
        assert(abs(centroid(array_centred)) < 1.e-10).all()

    # ------------------------------------------------------

    def test_frobenius_norm(self):
        """
        This test verifies the validity of the frobenius_norm function
        """
        """
        The Frobenius norm of any array after it has undergone scale_array should be unity.
        """

        # Define an arbitrary, zero-padded array
        array = np.array([[1.5294e-4, 1.242e-5, 1.624e-3, 7.35e-4], [4.534e-5, 1.652e-5, 1.725e-5, 3.314e-4],
                          [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]])

        predicted = translate_array_to_origin(array)[0]
        predicted = scale_array(predicted)[0]
        assert(abs(frobenius_norm(predicted) - 1.) < 1.e-10).all()

        # Define an arbitrary, zero-padded array
        array = np.array([[6325.26, 1232.46, 1356.75, 7351.64, 0, 0], [4351.36, 1246.63, 1247.63, 3243.64, 0, 0],
                          [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]])
        predicted = translate_array_to_origin(array)[0]
        predicted = scale_array(predicted)[0]
        assert(abs(frobenius_norm(predicted) - 1.) < 1.e-10).all()

        # Define an arbitrary
        array = np.array([[6., 12., 16., 7.], [4., 16., 17., 33.], [5., 17., 12., 16.]])
        predicted = translate_array_to_origin(array)[0]
        predicted = scale_array(predicted)[0]
        assert(abs(frobenius_norm(predicted) - 1.) < 1.e-10).all()

    if __name__ == '__main__':
        unittest.main()











