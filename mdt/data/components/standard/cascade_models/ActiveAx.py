from mdt.components_config.cascade_models import CascadeConfig

__author__ = 'Robbert Harms'
__date__ = '2017-07-19'
__maintainer__ = 'Robbert Harms'
__email__ = 'robbert.harms@maastrichtuniversity.nl'
__licence__ = 'LGPL v3'


class ActiveAx_ExVivo(CascadeConfig):

    name = 'ActiveAx_ExVivo (Cascade)'
    description = 'Initializes the directions to Ball & Stick.'
    models = ('BallStick_r1 (Cascade)',
              'ActiveAx_ExVivo')
    inits = {'ActiveAx_ExVivo': [('CylinderGPD.theta', 'Stick.theta'),
                                 ('CylinderGPD.phi', 'Stick.phi')]}
