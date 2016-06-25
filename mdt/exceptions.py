__author__ = 'Robbert Harms'
__date__ = "2016-06-25"
__maintainer__ = "Robbert Harms"
__email__ = "robbert.harms@maastrichtuniversity.nl"


class ProtocolIOError(Exception):
    """Custom exception class for protocol input output errors.

    This can be raised if a protocol is inconsistent or incomplete. It should not be raised for general IO errors,
    use the IO exception for that.
    """


class InsufficientProtocolError(Exception):
    """Indicates that the protocol constains insufficient information for fitting a specific model.

    This can be raised if a model misses a column it needs in the protocol, or if there are not enough shells, or...
    """


class NoiseStdEstimationNotPossible(Exception):
    """An exception that can be raised by any ComplexNoiseStdEstimator.

    This indicates that the noise std can not be estimated by the estimation routine.
    """
