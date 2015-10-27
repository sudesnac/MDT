#ifndef DMRICM_NODDIIC_H
#define DMRICM_NODDIIC_H

/**
 * Author = Robbert Harms
 * Date = 2/26/14 
 * License = LGPL v3
 * Maintainer = Robbert Harms
 * Email = robbert.harms@maastrichtuniversity.nl
 */

/**
 * Generate the compartment model signal for the Noddi Intra Cellular (Stick with dispersion) model.
 * If Radius is fixed to 0 the model behaves as a stick (with dispersion), if non-fixed the model behaves as a
 * cylinder (with dispersion).
 *
 * It may seem redundant to have both G/Delta/delta and b as arguments. But that is for speed reasons. b is most
 * of the time available anyway, and G/Delta/delta is only needed if R is not fixed (still it must be provided for).
 *
 * @params g from the protocol /scheme
 * @params b from the protocol /scheme
 * @params G from the protocol / scheme
 * @params Delta big delta from the protocol / scheme
 * @params delta small delta from the protocol / scheme
 * @params d parameter
 * @params theta parameter
 * @params phi parameter
 * @params kappa parameter (concentration parameter of the Watson's distribution)
 * @params R the radius of the cylinder
 * @params CLJnpZeros: the bessel root zeros used by the model function
 * @params CLJnpZerosLength: the length of the bessel roots vector CLJnpZeros
 */
model_float cmNoddi_IC(const model_float4 g,
                       const model_float b,
                       const model_float G,
                       const model_float Delta,
                       const model_float delta,
                       const model_float d,
                       const model_float theta,
                       const model_float phi,
                       const model_float kappa,
                       const model_float R,
                       global const model_float* const CLJnpZeros,
                       const int CLJnpZerosLength);
                    
#endif // DMRICM_NODDIIC_H