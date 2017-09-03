"""Definitions of the free parameters.

The free parameters are meant to be used for parameters that one wants to optimize. They can be fixed to a certain
value to disable them from being optimized in a given situation, but they remain classified as 'optimizable' parameters.

Please choose the parameter type for a model and parameter carefully since the type signifies how the parameter and
its data are handled during model construction.
"""

import numpy as np
from mdt.component_templates.parameters import FreeParameterTemplate
from mot.model_building.parameter_functions.priors import UniformWithinBoundsPrior
from mot.model_building.parameter_functions.proposals import GaussianProposal, CircularGaussianProposal
from mot.model_building.parameter_functions.sample_statistics import CircularGaussianPIFit, TruncatedGaussianFitModulus
from mot.model_building.parameter_functions.transformations import ClampTransform, AbsModPiTransform, \
    SinSqrClampTransform, CosSqrClampTransform


__author__ = 'Robbert Harms'
__date__ = "2015-12-12"
__maintainer__ = "Robbert Harms"
__email__ = "robbert.harms@maastrichtuniversity.nl"


class s0(FreeParameterTemplate):

    init_value = 1e4
    lower_bound = 1e-5
    upper_bound = 1e10
    parameter_transform = ClampTransform()
    sampling_proposal = GaussianProposal(std=10.0)


class T1(FreeParameterTemplate):

    init_value = 0.02
    lower_bound = 1e-5
    upper_bound = 4.0
    parameter_transform = ClampTransform()
    sampling_proposal = GaussianProposal(0.0001)


class T2(FreeParameterTemplate):

    init_value = 0.01
    lower_bound = 1e-5
    upper_bound = 2.0
    parameter_transform = ClampTransform()
    sampling_proposal = GaussianProposal(0.0001)


class T2_star(FreeParameterTemplate):

    init_value = 0.01
    lower_bound = 0.0
    upper_bound = 1.0
    parameter_transform = ClampTransform()
    sampling_proposal = GaussianProposal(0.0001)


class E1(FreeParameterTemplate):
    """This parameter is defined *only* for linear decay T1 fitting in GRE data *with* TR constant.

    This parameter is also defined in the SSFP equation. However, in SSFP this parameter is from the protocol (!)
        E1 = exp( -TR / T1 ).
    After estimation of this parameter, T1 can be recovered by applying the next equation:
        -TR / log( E1 ).
    """

    init_value = 0.37
    lower_bound = 0.0
    upper_bound = 1.0
    parameter_transform = ClampTransform()
    sampling_proposal = GaussianProposal(0.0001)


class R1(FreeParameterTemplate):
    """R1 = 1/T1, for linear T1Dec or other models. """

    init_value = 2
    lower_bound = 0.25
    upper_bound = 100.0
    parameter_transform = ClampTransform()
    sampling_proposal = GaussianProposal(0.0001)


class R2(FreeParameterTemplate):
    """R2 = 1/T2, for linear T2Dec or other models."""

    init_value = 5
    lower_bound = 0.5
    upper_bound = 500.0
    parameter_transform = ClampTransform()
    sampling_proposal = GaussianProposal(0.0001)


class R2s(FreeParameterTemplate):
    """R2s = 1/T2s, for lineaR T2sDec or other models."""

    init_value = 10
    lower_bound = 1
    upper_bound = 50.0
    parameter_transform = ClampTransform()
    sampling_proposal = GaussianProposal(0.0001)


class theta(FreeParameterTemplate):
    """The inclination/polar angle."""
    init_value = np.pi / 2.0
    lower_bound = 0
    upper_bound = np.pi
    parameter_transform = AbsModPiTransform()
    sampling_proposal = CircularGaussianProposal(np.pi, 0.1)
    sampling_prior = UniformWithinBoundsPrior()
    sampling_statistics = CircularGaussianPIFit()


class phi(FreeParameterTemplate):
    """The azimuth angle.

    We limit this parameter between [0, pi] making us only use (together with theta between [0, pi]) only the right
    hemisphere. This is possible since diffusion is symmetric and works fine during optimization.

    However, during sampling the results can clip to pi since the standard formula for transforming spherical
    coordinates to cartesian coordinates defines phi to be in the range [0, 2*pi]. This is both a problem and a
    blessing. The problem is that the samples will not wrap nicely around pi, the blessing is that we prevent a
    bimodal distribution in phi. Not wrapping around pi is not much of a problem though, as the sampler can easily
    sample only half of a gaussian if the optimal parameter is around pi. A point estimate can then be obtained using
    a truncated gaussian.
    """
    init_value = np.pi / 2.0
    lower_bound = 0
    upper_bound = np.pi
    parameter_transform = AbsModPiTransform()
    sampling_proposal = GaussianProposal(0.1)
    sampling_prior = UniformWithinBoundsPrior()
    sampling_statistics = TruncatedGaussianFitModulus(0, np.pi, np.pi)


class psi(FreeParameterTemplate):
    """The rotation angle for use in cylindrical models.

    This parameter can be used to rotate a vector around another vector, as is for example done in the Tensor model.
    """
    init_value = np.pi / 2.0
    lower_bound = 0
    upper_bound = np.pi
    parameter_transform = AbsModPiTransform()
    sampling_proposal = CircularGaussianProposal(np.pi, 0.5)
    sampling_prior = UniformWithinBoundsPrior()
    sampling_statistics = CircularGaussianPIFit()


class d(FreeParameterTemplate):

    init_value = 1.7e-9
    lower_bound = 1e-11
    upper_bound = 1.0e-8
    parameter_transform = SinSqrClampTransform()
    sampling_proposal = GaussianProposal(1e-10)


class dperp0(FreeParameterTemplate):

    init_value = 1.7e-10
    lower_bound = 0
    upper_bound = 1.0e-8
    parameter_transform = SinSqrClampTransform()
    sampling_proposal = GaussianProposal(5e-10)


class dperp1(FreeParameterTemplate):

    init_value = 1.7e-11
    lower_bound = 0
    upper_bound = 1.0e-8
    parameter_transform = SinSqrClampTransform()
    sampling_proposal = GaussianProposal(5e-10)


class R(FreeParameterTemplate):

    init_value = 1.0e-6
    lower_bound = 1e-7
    upper_bound = 20e-6
    parameter_transform = CosSqrClampTransform()
    sampling_proposal = GaussianProposal(1e-7)


class kappa(FreeParameterTemplate):

    init_value = 1
    lower_bound = 1e-5
    upper_bound = 2 * np.pi
    parameter_transform = CosSqrClampTransform()
    sampling_proposal = GaussianProposal(0.01)


# for use in the GDRCylinder model
class gamma_shape(FreeParameterTemplate):

    init_value = 1
    lower_bound = 0.1e-3
    upper_bound = 20
    parameter_transform = CosSqrClampTransform()
    sampling_proposal = GaussianProposal(1.0e-2)


# for use in the GDRCylinder model
class gamma_scale(FreeParameterTemplate):

    init_value = 1e-6
    lower_bound = 0.1e-9
    upper_bound = 20e-6
    parameter_transform = CosSqrClampTransform()
    sampling_proposal = GaussianProposal(1e-9)


# for use in ExpT1DecSTEAM model. It is assumed for ex-vivo values. For in-vivo use d instead.
class d_exvivo(FreeParameterTemplate):

    init_value = 5.0e-10
    lower_bound = 0.0
    upper_bound = 1.0e-8
    parameter_transform = SinSqrClampTransform()
    sampling_proposal = GaussianProposal(1e-11)


class time_dependent_characteristic_coefficient(FreeParameterTemplate):
    """The time dependent characteristic as used in the TimeDependentZeppelin model. Values are in m^2."""
    init_value = 1e-6
    lower_bound = 1e-7
    upper_bound = 1e-5
    parameter_transform = CosSqrClampTransform()
    sampling_proposal = GaussianProposal(1e-7)


class d_bulk(FreeParameterTemplate):

    init_value = 0.e-9
    lower_bound = 0
    upper_bound = 1.0e-8
    parameter_transform = SinSqrClampTransform()
    sampling_proposal = GaussianProposal(1e-10)


# the following parameters are part of the non-parametric Tensor
# (Tensor in which a upper triangular D matrix is optimized directly)
class Tensor_D_00(FreeParameterTemplate):

    init_value = 0.3e-9
    lower_bound = 0
    upper_bound = 5e-9
    parameter_transform = SinSqrClampTransform()
    sampling_proposal = GaussianProposal(1e-10)


class Tensor_D_11(FreeParameterTemplate):

    init_value = 0.3e-9
    lower_bound = 0
    upper_bound = 5e-9
    parameter_transform = SinSqrClampTransform()
    sampling_proposal = GaussianProposal(1e-10)


class Tensor_D_22(FreeParameterTemplate):

    init_value = 1.2e-9
    lower_bound = 0
    upper_bound = 5e-9
    parameter_transform = SinSqrClampTransform()
    sampling_proposal = GaussianProposal(1e-10)


class Tensor_D_01(FreeParameterTemplate):

    init_value = 0
    lower_bound = -1e-9
    upper_bound = 1e-9
    parameter_transform = SinSqrClampTransform()
    sampling_proposal = GaussianProposal(1e-10)


class Tensor_D_02(FreeParameterTemplate):

    init_value = 0
    lower_bound = -1e-9
    upper_bound = 1e-9
    parameter_transform = SinSqrClampTransform()
    sampling_proposal = GaussianProposal(1e-10)


class Tensor_D_12(FreeParameterTemplate):

    init_value = 0
    lower_bound = -1e-9
    upper_bound = 1e-9
    parameter_transform = SinSqrClampTransform()
    sampling_proposal = GaussianProposal(1e-10)


class Efficiency(FreeParameterTemplate):

    init_value = 0.95
    lower_bound = 0
    upper_bound = 1
    parameter_transform = SinSqrClampTransform()
    sampling_proposal = GaussianProposal(0.001)
