__author__ = 'Jonny'

from procrustes.base import Procrustes
from procrustes.procrustes_orthogonal import OrthogonalProcrustes
import numpy as np
from itertools import product


class TwoSidedOrthogonalSingleTransformationProcrustes(Procrustes):

    """
    This method deals with the two-sided orthogonal Procrustes problem
    limited to a single transformation

    We require symmetric input arrays to perform this analysis
    """

    """
    map_a_to_b is set to True by default. For the two-sided single transformation procrustes analyses, this is crucial
    for accuracy. When set to False, the input arrays both undergo centroid translation to the origin and
    Frobenius normalization, prior to further analysis. Something about this transformation skews the accuracy
    of the results.
    """

    def __init__(self, array_a, array_b, translate=False, scale=False, preserve_symmetry=True, hide_padding=True,
                 translate_symmetrically=False):
        self.hide_padding = hide_padding
        self.translate = translate
        self.scale = scale
        self.preserve_symmetry = preserve_symmetry
        self.translate_symmetrically = translate_symmetrically
        Procrustes.__init__(self, array_a, array_b, translate=self.translate, scale=self.scale,
            preserve_symmetry=self.preserve_symmetry, hide_padding=self.hide_padding, translate_symmetrically=self.translate_symmetrically)

        if (abs(self.array_a - self.array_a.T) > 1.e-10).all() or (abs(self.array_b - self.array_b.T) > 1.e-10).all():
            raise ValueError('Arrays array_a and array_b must both be symmetric for this analysis.')

    def calculate(self, return_u_approx=False, return_u_best=True, tol=1.e-12):

        """
        Calculates the single optimum two-sided orthogonal transformation matrix in the
        double-sided procrustes problem

        Parameters
        ----------
        array_a : ndarray
            A 2D array representing the array to be transformed (as close as possible to array_b)

        array_b : ndarray
            A 2D array representing the reference array

        Returns
        ----------
        u_umeyama_approx, array_transformed, error
        u_umeyama_approx = the optimum orthogonal transformation array satisfying the double
             sided procrustes problem. Array represents the closest orthogonal array to
             u_umeyama given by the orthogonal procrustes problem
        array_transformed = the transformed input array after transformation by u_umeyama_approx
        error = the error as described by the double-sided procrustes problem
        """

        array_a = self.array_a
        array_b = self.array_b
        if self.is_diagonalizable(array_a) is False or self.is_diagonalizable(array_b) is False:
            return_u_approx = False

        error_approx = None
        u_approx = None
        u_best = None
        error_best = None
        array_transformed_approx = None
        array_transformed_best = None
        if return_u_approx:
            # Calculate the eigenvalue decomposition of array_a and array_b
            sigma_a, u_a = self.eigenvalue_decomposition(array_a)
            sigma_a0, u_a0 = self.eigenvalue_decomposition(array_b)
            # Compute u_umeyama
            u_umeyama = np.multiply(abs(u_a), abs(u_a0).T)
            # Compute u_umeyama_approx using orthogonal procrustes analysis
            n, m = u_umeyama.shape
            ortho = OrthogonalProcrustes(np.eye(n), u_umeyama, translate=self.translate, scale=self.scale,
                                         hide_padding=self.hide_padding)
            u_approx, array_transformed_ortho, error_ortho, translate_and_or_scale = ortho.calculate()
            u_approx[abs(u_approx) < 1.e-8] = 0
            # Calculate the error
            error_approx = self.double_sided_procrustes_error(array_a, array_b, u_approx, u_approx)
            # Calculate the transformed input array
            array_transformed_approx = np.dot(array_a, u_approx)

        if return_u_best:
            # svd of each array
            u_a, sigma_a, v_trans_a = self.singular_value_decomposition(array_a)
            u_a0, sigma_a0, v_trans_a0 = self.singular_value_decomposition(array_b)
            n = sigma_a.shape[0]
            # Compute all 2^n combinations of diagonal n x n matrices where diagonal elements are from the set {-1,1}
            diag_vec_list = list(product((-1., 1.), repeat=n))
            error_best = 1.e5  # Arbitrarily initialize best error
            u_best = u_a
            """
            Iterate until all possible combinations have been checked, and choose trial with the least error.
            If any iteration produces error less than the tolerance, stop the loop and choose this trial.
            """
            for i in range(2**n):
                # Compute the trial's optimum transformation array
                u_trial = np.dot(np.dot(u_a, np.diag(diag_vec_list[i])), u_a0.T)
                # And the trial's corresponding error
                error = self.double_sided_procrustes_error(array_a, array_b, u_trial, u_trial)
                if error < tol:
                    u_best = u_trial
                    error_best = error
                    break
                if error < error_best:
                    u_best = u_trial
                    error_best = error
                else:
                    continue
            array_transformed_best = np.dot(np.dot(u_best.T, array_a), u_best)

        if return_u_approx and return_u_best:
            if error_approx >= error_best:
                u_best = u_best
                error_best = error_best
            else:
                u_best = u_approx
                error_best = error_approx
            # map array_a to array_b
            self.map_a_b(u_best.T, u_best, preserve_symmetry=True, translate_symmetrically=self.translate_symmetrically)
            # print " You've selected both the Umeyaman and exact transformations."
            # print "Output order: u_approx, u_best, array_transformation_approx_exact,"
            # print "array_transformation_exact, error_approx, error_best, translate_and_or_scaling:"
            return u_approx, u_best, array_transformed_approx, array_transformed_best, error_approx, \
                error_best, self.transformation

        elif return_u_approx:
            # map array_a to array_b
            self.map_a_b(u_approx.T, u_approx, preserve_symmetry=True, translate_symmetrically=self.translate_symmetrically)
            # print "You've selected the Umeyaman approximation."
            # print 'The input 2D arrays are {0} and {1}.\n'.format(array_a.shape, array_b.shape)
            return u_approx, u_best, array_transformed_approx, array_transformed_best, error_approx, \
                error_best, self.transformation  # u_approx, array_transformed_approx, error_approx, self.translate_scale

        elif return_u_best:
            # map array_a to array_b
            self.map_a_b(u_best.T, u_best, preserve_symmetry=True, translate_symmetrically=self.translate_symmetrically)
            # print "You've selected the best transformation. "
            # print 'The input 2D arrays are {0} and {1}.\n'.format(array_a.shape, array_b.shape)
            return u_approx, u_best, array_transformed_approx, array_transformed_best, error_approx, \
                error_best, self.transformation  # u_best, array_transformed_best, error_best, self.translate_scale

        else:
            raise ValueError(" Cannot complete analysis. You must select at least one transformation.")
