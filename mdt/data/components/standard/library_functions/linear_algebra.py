from mdt import LibraryFunctionTemplate


class RotateOrthogonalVector(LibraryFunctionTemplate):

    description = '''
        Uses Rodrigues' rotation formula to rotate the given vector v by psi around k.

        This function assumes that the given vectors v and k are orthogonal which allows a speed up/

        Args:
            basis: the unit vector defining the rotation axis (k)
            to_rotate: the vector to rotate by the angle psi (v)
            psi: the rotation angle (psi)

        Returns:
            vector: the rotated vector
    '''
    return_type = 'mot_float_type4'
    parameters = [('mot_float_type4', 'basis'),
                  ('mot_float_type4', 'to_rotate'),
                  ('mot_float_type', 'psi')]
    cl_code = '''
        mot_float_type cos_psi;
        mot_float_type sin_psi = sincos(psi, &cos_psi);

        return to_rotate * cos_psi + (cross(basis, to_rotate) * sin_psi);
    '''


class RotateVector(LibraryFunctionTemplate):

    description = '''
        Uses Rodrigues' rotation formula to rotate the given vector v by psi around k.

        Args:
            basis: the unit vector defining the rotation axis (k)
            to_rotate: the vector to rotate by the angle psi (v)
            psi: the rotation angle (psi)

        Returns:
            vector: the rotated vector
    '''
    return_type = 'mot_float_type4'
    parameters = [('mot_float_type4', 'basis'),
                  ('mot_float_type4', 'to_rotate'),
                  ('mot_float_type', 'psi')]
    cl_code = '''
        mot_float_type cos_psi;
        mot_float_type sin_psi = sincos(psi, &cos_psi);

        return to_rotate * cos_psi
                + (cross(basis, to_rotate) * sin_psi)
                + (basis * dot(basis, to_rotate) * (1 - cos_psi));
    '''


class SphericalToCartesian(LibraryFunctionTemplate):

    description = '''
        """Convert polar coordinates in 3d space to cartesian unit coordinates.

        .. code-block:: python

            x = sin(theta) * cos(phi)
            y = sin(theta) * sin(phi)
            z = cos(theta)

        Args:
            theta: polar angle of the first vector
            phi: azimuth angle of the first vector
    '''
    return_type = 'mot_float_type4'
    parameters = ['theta', 'phi']
    cl_code = '''
        mot_float_type cos_theta;
        mot_float_type sin_theta = sincos(theta, &cos_theta);
        mot_float_type cos_phi;
        mot_float_type sin_phi = sincos(phi, &cos_phi);
        
        return (mot_float_type4)(cos_phi * sin_theta, sin_phi * sin_theta, cos_theta, 0.0);
    '''


class TensorSphericalToCartesian(LibraryFunctionTemplate):

    description = '''
        Generates the D matrix for a Tensor compartment.

        The angles ``theta`` and ``phi`` are used for creating the first vector, ``vec0``.
        Next, ``vec0`` is rotated 90 degrees in the (x, z) plane to form a vector perpendicular to the
        principal direction. This vector is then rotated around ``psi`` to generate the first perpendicular
        orientation, ``vec1``. The third vector is generated by being perpendicular to the other two vectors.

        Args:
            theta: polar angle of the first vector
            phi: azimuth angle of the first vector
            psi: rotation around the first vector, used to generate the perpendicular vectors.
    '''
    dependencies = ['RotateOrthogonalVector', 'SphericalToCartesian']
    parameters = ['theta', 'phi', 'psi',
                  ('mot_float_type4*', 'vec0'),
                  ('mot_float_type4*', 'vec1'),
                  ('mot_float_type4*', 'vec2')]
    cl_code = '''
        *vec0 = SphericalToCartesian(theta, phi);
        *vec1 = RotateOrthogonalVector(*vec0, SphericalToCartesian(theta + M_PI_2_F, phi), psi);
        *vec2 = cross(*vec0, *vec1);
    '''


class CartesianPolarDotProduct(LibraryFunctionTemplate):

    description = '''
        Calculates the dot product between a cartesian and a polar coordinate vector.
        
        Prior to taking the dot product it will convert the polar coordinate vector to cartesian coordinates.
         
        Args:
            v0_x: the x coordinate of the first vector
            v0_y: the y coordinate of the first vector
            v0_z: the z coordinate of the first vector
            v1_theta: the polar angle of the second vector
            v1_phi: the azimuth angle of the second vector
            
        Returns:
            dot product between the two vectors
    '''
    return_type = 'mot_float_type'
    parameters = [('mot_float_type', 'v0_x'),
                  ('mot_float_type', 'v0_y'),
                  ('mot_float_type', 'v0_z'),
                  ('mot_float_type', 'v1_theta'),
                  ('mot_float_type', 'v1_phi')]
    cl_code = '''
        mot_float_type cos_theta;
        mot_float_type sin_theta = sincos(v1_theta, &cos_theta);
        mot_float_type cos_phi;
        mot_float_type sin_phi = sincos(v1_phi, &cos_phi);
        
        return (v0_x * (cos_phi * sin_theta)) + (v0_y * (sin_phi * sin_theta)) + (v0_z * cos_theta);
    '''


class EigenvaluesSymmetric3x3(LibraryFunctionTemplate):
    description = '''
        Calculate the eigenvalues of a symmetric 3x3 matrix. 

        This simple algorithm only works in case of a real and symmetric matrix. 

        This returns the eigenvalues such that eig1 >= eig2 >= eig3, i.e. from large to small.

        References:
            [1]: https://en.wikipedia.org/wiki/Eigenvalue_algorithm#3.C3.973_matrices
            [2]: Smith, Oliver K. (April 1961), "Eigenvalues of a symmetric 3 × 3 matrix.", Communications of the ACM, 
                 4 (4): 168, doi:10.1145/355578.366316

        Args:
            A: the matrix as an array in c/row-major order
            v: the output eigenvalues as a vector of three elements.            
    '''
    parameters = [('mot_float_type*', 'A'),
                  ('mot_float_type*', 'v')]
    cl_code = '''
        double p1 = (A[1] * A[1]) + (A[2] * A[2]) + (A[5] * A[5]);

        if (p1 == 0.0){
            v[0] = A[0];
            v[1] = A[4];
            v[2] = A[8];
            return;
        }
        
        double q = (A[0] + A[4] + A[8]) / 3.0;
        double p = sqrt(((A[0] - q)*(A[0] - q) + (A[4] - q)*(A[4] - q) + (A[8] - q)*(A[8] - q) + 2*p1) / 6.0);

        double r = (
             ((A[0] - q)/p) * ((((A[4] - q)/p) * ((A[8] - q)/p)) - ((A[7]/p) * (A[5]/p))) 
            - (A[1]/p)      * ((A[3]/p) * ((A[8] - q)/p) - (A[6]/p) * (A[5]/p)) 
            + (A[2]/p)      * ((A[3]/p) * (A[7]/p) - (A[6]/p) * ((A[4] - q)/p))
        ) / 2.0;

        double phi;
        if(r <= -1){
            phi = M_PI / 3.0;
        }
        else if(r >= 1){
            phi = 0;
        }
        else{
            phi = acos(r) / 3;
        }

        v[0] = q + 2 * p * cos(phi);
        v[2] = q + 2 * p * cos(phi + (2*M_PI/3.0));
        v[1] = 3 * q - v[0] - v[2];
    '''
