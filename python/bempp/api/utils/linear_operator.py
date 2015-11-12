# coding=utf-8
"""
This module provides a full implementation of the Scipy 0.16 LinearOperator
class structure for older Scipy version. If the Scipy version is at least 0.16
then the corresponding Scipy classes are directly imported.

The class definitions below are part of Scipy 0.16 and protected by the
following license.

Copyright © 2001, 2002 Enthought, Inc.
All rights reserved.

Copyright © 2003-2013 SciPy Developers.
All rights reserved.
Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
Neither the name of Enthought nor the names of the SciPy Developers may be used to endorse or promote products derived from this software without specific prior written permission.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
from __future__ import division, print_function, absolute_import

import scipy

if scipy.version.full_version < "0.16.0":


    import numpy as np

    from scipy.sparse import isspmatrix
    from scipy.sparse.sputils import isshape, isintlike
    from scipy.sparse.linalg import LinearOperator as ScipyLinearOperator

    class LinearOperator(ScipyLinearOperator):
        """Common interface for performing matrix vector products
        This class reimplements the Scipy 0.16 LinearOperator interface
        for older Scipy versions. It itself inherits from the original
        Scipy LinearOperator so that these objects can be handed over
        everywhere where LinearOperator objects are needed.

        """
        def __new__(cls, *args, **kwargs):
            if cls is LinearOperator:
                # Operate as _CustomLinearOperator factory.
                return _CustomLinearOperator(*args, **kwargs)
            else:
                obj = super(LinearOperator, cls).__new__(cls)

                if (type(obj)._matvec == LinearOperator._matvec
                        and type(obj)._matmat == LinearOperator._matmat):
                    raise TypeError("LinearOperator subclass should implement"
                                    " at least one of _matvec and _matmat.")

                obj.__init__(*args, **kwargs)
                return obj

        def __init__(self, dtype, shape):
            """Initialize this LinearOperator.
            To be called by subclasses. ``dtype`` may be None; ``shape`` should
            be convertible to a length-2 tuple.
            """
            if dtype is not None:
                dtype = np.dtype(dtype)

            shape = tuple(shape)
            if not isshape(shape):
                raise ValueError("invalid shape %r (must be 2-d)" % shape)

            self.dtype = dtype
            self.shape = shape

        def _init_dtype(self):
            """Called from subclasses at the end of the __init__ routine.
            """
            if self.dtype is None:
                v = np.zeros(self.shape[-1])
                self.dtype = np.asarray(self.matvec(v)).dtype

        def _matmat(self, X):
            """Default matrix-matrix multiplication handler.
            Falls back on the user-defined _matvec method, so defining that will
            define matrix multiplication (though in a very suboptimal way).
            """

            return np.hstack([self.matvec(col.reshape(-1,1)) for col in X.T])

        def _matvec(self, x):
            """Default matrix-vector multiplication handler.
            If self is a linear operator of shape (M, N), then this method will
            be called on a shape (N,) or (N, 1) ndarray, and should return a
            shape (M,) or (M, 1) ndarray.
            This default implementation falls back on _matmat, so defining that
            will define matrix-vector multiplication as well.
            """
            return self.matmat(x.reshape(-1, 1))

        def matvec(self, x):
            """Matrix-vector multiplication.
            Performs the operation y=A*x where A is an MxN linear
            operator and x is a column vector or 1-d array.
            Parameters
            ----------
            x : {matrix, ndarray}
                An array with shape (N,) or (N,1).
            Returns
            -------
            y : {matrix, ndarray}
                A matrix or ndarray with shape (M,) or (M,1) depending
                on the type and shape of the x argument.
            Notes
            -----
            This matvec wraps the user-specified matvec routine or overridden
            _matvec method to ensure that y has the correct shape and type.
            """

            x = np.asanyarray(x)

            M,N = self.shape

            if x.shape != (N,) and x.shape != (N,1):
                raise ValueError('dimension mismatch')

            y = self._matvec(x)

            if isinstance(x, np.matrix):
                y = np.asmatrix(y)
            else:
                y = np.asarray(y)

            if x.ndim == 1:
                y = y.reshape(M)
            elif x.ndim == 2:
                y = y.reshape(M,1)
            else:
                raise ValueError('invalid shape returned by user-defined matvec()')

            return y

        def rmatvec(self, x):
            """Adjoint matrix-vector multiplication.
            Performs the operation y = A^H * x where A is an MxN linear
            operator and x is a column vector or 1-d array.
            Parameters
            ----------
            x : {matrix, ndarray}
                An array with shape (M,) or (M,1).
            Returns
            -------
            y : {matrix, ndarray}
                A matrix or ndarray with shape (N,) or (N,1) depending
                on the type and shape of the x argument.
            Notes
            -----
            This rmatvec wraps the user-specified rmatvec routine or overridden
            _rmatvec method to ensure that y has the correct shape and type.
            """

            x = np.asanyarray(x)

            M,N = self.shape

            if x.shape != (M,) and x.shape != (M,1):
                raise ValueError('dimension mismatch')

            y = self._rmatvec(x)

            if isinstance(x, np.matrix):
                y = np.asmatrix(y)
            else:
                y = np.asarray(y)

            if x.ndim == 1:
                y = y.reshape(N)
            elif x.ndim == 2:
                y = y.reshape(N,1)
            else:
                raise ValueError('invalid shape returned by user-defined rmatvec()')

            return y

        def _rmatvec(self, x):
            """Default implementation of _rmatvec; defers to adjoint."""
            if type(self)._adjoint == LinearOperator._adjoint:
                # _adjoint not overridden, prevent infinite recursion
                raise NotImplementedError
            else:
                return self.H.matvec(x)

        def matmat(self, X):
            """Matrix-matrix multiplication.
            Performs the operation y=A*X where A is an MxN linear
            operator and X dense N*K matrix or ndarray.
            Parameters
            ----------
            X : {matrix, ndarray}
                An array with shape (N,K).
            Returns
            -------
            Y : {matrix, ndarray}
                A matrix or ndarray with shape (M,K) depending on
                the type of the X argument.
            Notes
            -----
            This matmat wraps any user-specified matmat routine or overridden
            _matmat method to ensure that y has the correct type.
            """

            X = np.asanyarray(X)

            if X.ndim != 2:
                raise ValueError('expected 2-d ndarray or matrix, not %d-d'
                                 % X.ndim)

            M,N = self.shape

            if X.shape[0] != N:
                raise ValueError('dimension mismatch: %r, %r'
                                 % (self.shape, X.shape))

            Y = self._matmat(X)

            if isinstance(Y, np.matrix):
                Y = np.asmatrix(Y)

            return Y

        def __call__(self, x):
            return self*x

        def __mul__(self, x):
            return self.dot(x)

        def dot(self, x):
            """Matrix-matrix or matrix-vector multiplication.
            Parameters
            ----------
            x : array_like
                1-d or 2-d array, representing a vector or matrix.
            Returns
            -------
            Ax : array
                1-d or 2-d array (depending on the shape of x) that represents
                the result of applying this linear operator on x.
            """
            if isinstance(x, LinearOperator):
                return _ProductLinearOperator(self, x)
            elif np.isscalar(x):
                return _ScaledLinearOperator(self, x)
            else:
                x = np.asarray(x)

                if x.ndim == 1 or x.ndim == 2 and x.shape[1] == 1:
                    return self.matvec(x)
                elif x.ndim == 2:
                    return self.matmat(x)
                else:
                    raise ValueError('expected 1-d or 2-d array or matrix, got %r'
                                     % x)

        def __rmul__(self, x):
            if np.isscalar(x):
                return _ScaledLinearOperator(self, x)
            else:
                return NotImplemented

        def __pow__(self, p):
            if np.isscalar(p):
                return _PowerLinearOperator(self, p)
            else:
                return NotImplemented

        def __add__(self, x):
            if isinstance(x, LinearOperator):
                return _SumLinearOperator(self, x)
            else:
                return NotImplemented

        def __neg__(self):
            return _ScaledLinearOperator(self, -1)

        def __sub__(self, x):
            return self.__add__(-x)

        def __repr__(self):
            M,N = self.shape
            if self.dtype is None:
                dt = 'unspecified dtype'
            else:
                dt = 'dtype=' + str(self.dtype)

            return '<%dx%d %s with %s>' % (M, N, self.__class__.__name__, dt)

        def adjoint(self):
            """Hermitian adjoint.
            Returns the Hermitian adjoint of self, aka the Hermitian
            conjugate or Hermitian transpose. For a complex matrix, the
            Hermitian adjoint is equal to the conjugate transpose.
            Can be abbreviated self.H instead of self.adjoint().
            Returns
            -------
            A_H : LinearOperator
                Hermitian adjoint of self.
            """
            return self._adjoint()

        H = property(adjoint)

        def transpose(self):
            """Transpose this linear operator.
            Returns a LinearOperator that represents the transpose of this one.
            Can be abbreviated self.T instead of self.transpose().
            """
            return self._transpose()

        T = property(transpose)

        def _adjoint(self):
            """Default implementation of _adjoint; defers to rmatvec."""
            shape = (self.shape[1], self.shape[0])
            return _CustomLinearOperator(shape, matvec=self.rmatvec,
                                         rmatvec=self.matvec,
                                         dtype=self.dtype)


    class _CustomLinearOperator(LinearOperator):
        """Linear operator defined in terms of user-specified operations."""

        def __init__(self, shape, matvec, rmatvec=None, matmat=None, dtype=None):
            super(_CustomLinearOperator, self).__init__(dtype, shape)

            self.args = ()

            self.__matvec_impl = matvec
            self.__rmatvec_impl = rmatvec
            self.__matmat_impl = matmat

            self._init_dtype()

        def _matmat(self, X):
            if self.__matmat_impl is not None:
                return self.__matmat_impl(X)
            else:
                return super(_CustomLinearOperator, self)._matmat(X)

        def _matvec(self, x):
            return self.__matvec_impl(x)

        def _rmatvec(self, x):
            func = self.__rmatvec_impl
            if func is None:
                raise NotImplemented("rmatvec is not defined")
            return self.__rmatvec_impl(x)

        def _adjoint(self):
            return _CustomLinearOperator(shape=(self.shape[1], self.shape[0]),
                                         matvec=self.__rmatvec_impl,
                                         rmatvec=self.__matvec_impl,
                                         dtype=self.dtype)


    def _get_dtype(operators, dtypes=[]):
        for obj in operators:
            if obj is not None and hasattr(obj, 'dtype'):
                dtypes.append(obj.dtype)
        return np.find_common_type(dtypes, [])


    class _SumLinearOperator(LinearOperator):
        def __init__(self, A, B):
            if not isinstance(A, LinearOperator) or \
                    not isinstance(B, LinearOperator):
                raise ValueError('both operands have to be a LinearOperator')
            if A.shape != B.shape:
                raise ValueError('cannot add %r and %r: shape mismatch'
                                 % (A, B))
            self.args = (A, B)
            super(_SumLinearOperator, self).__init__(_get_dtype([A, B]), A.shape)

        def _matvec(self, x):
            return self.args[0].matvec(x) + self.args[1].matvec(x)

        def _rmatvec(self, x):
            return self.args[0].rmatvec(x) + self.args[1].rmatvec(x)

        def _matmat(self, x):
            return self.args[0].matmat(x) + self.args[1].matmat(x)

        def _adjoint(self):
            A, B = self.args
            return A.H + B.H


    class _ProductLinearOperator(LinearOperator):
        def __init__(self, A, B):
            if not isinstance(A, LinearOperator) or \
                    not isinstance(B, LinearOperator):
                raise ValueError('both operands have to be a LinearOperator')
            if A.shape[1] != B.shape[0]:
                raise ValueError('cannot multiply %r and %r: shape mismatch'
                                 % (A, B))
            super(_ProductLinearOperator, self).__init__(_get_dtype([A, B]),
                                                         (A.shape[0], B.shape[1]))
            self.args = (A, B)

        def _matvec(self, x):
            return self.args[0].matvec(self.args[1].matvec(x))

        def _rmatvec(self, x):
            return self.args[1].rmatvec(self.args[0].rmatvec(x))

        def _matmat(self, x):
            return self.args[0].matmat(self.args[1].matmat(x))

        def _adjoint(self):
            A, B = self.args
            return B.H * A.H


    class _ScaledLinearOperator(LinearOperator):
        def __init__(self, A, alpha):
            if not isinstance(A, LinearOperator):
                raise ValueError('LinearOperator expected as A')
            if not np.isscalar(alpha):
                raise ValueError('scalar expected as alpha')
            dtype = _get_dtype([A], [type(alpha)])
            super(_ScaledLinearOperator, self).__init__(dtype, A.shape)
            self.args = (A, alpha)

        def _matvec(self, x):
            return self.args[1] * self.args[0].matvec(x)

        def _rmatvec(self, x):
            return np.conj(self.args[1]) * self.args[0].rmatvec(x)

        def _matmat(self, x):
            return self.args[1] * self.args[0].matmat(x)

        def _adjoint(self):
            A, alpha = self.args
            return A.H * alpha


    class _PowerLinearOperator(LinearOperator):
        def __init__(self, A, p):
            if not isinstance(A, LinearOperator):
                raise ValueError('LinearOperator expected as A')
            if A.shape[0] != A.shape[1]:
                raise ValueError('square LinearOperator expected, got %r' % A)
            if not isintlike(p):
                raise ValueError('integer expected as p')

            super(_PowerLinearOperator, self).__init__(_get_dtype([A]), A.shape)
            self.args = (A, p)

        def _power(self, fun, x):
            res = np.array(x, copy=True)
            for i in range(self.args[1]):
                res = fun(res)
            return res

        def _matvec(self, x):
            return self._power(self.args[0].matvec, x)

        def _rmatvec(self, x):
            return self._power(self.args[0].rmatvec, x)

        def _matmat(self, x):
            return self._power(self.args[0].matmat, x)

        def _adjoint(self):
            A, p = self.args
            return A.H ** p


    class MatrixLinearOperator(LinearOperator):
        def __init__(self, A):
            super(MatrixLinearOperator, self).__init__(A.dtype, A.shape)
            self.A = A
            self.__adj = None
            self.args = (A,)

        def _matmat(self, X):
            return self.A.dot(X)

        def _adjoint(self):
            if self.__adj is None:
                self.__adj = _AdjointMatrixOperator(self)
            return self.__adj


    class _AdjointMatrixOperator(MatrixLinearOperator):
        def __init__(self, adjoint):
            self.A = adjoint.A.T.conj()
            self.__adjoint = adjoint
            self.args = (adjoint,)
            self.shape = adjoint.shape[1], adjoint.shape[0]

        @property
        def dtype(self):
            return self.__adjoint.dtype

        def _adjoint(self):
            return self.__adjoint


    class IdentityOperator(LinearOperator):
        def __init__(self, shape, dtype=None):
            super(IdentityOperator, self).__init__(dtype, shape)

        def _matvec(self, x):
            return x

        def _rmatvec(self, x):
            return x

        def _matmat(self, x):
            return x

        def _adjoint(self):
            return self


    def aslinearoperator(A):
        """Return A as a LinearOperator.
        'A' may be any of the following types:
         - ndarray
         - matrix
         - sparse matrix (e.g. csr_matrix, lil_matrix, etc.)
         - LinearOperator
         - An object with .shape and .matvec attributes
        See the LinearOperator documentation for additional information.
        Examples
        --------
        >>> from scipy import matrix
        >>> M = matrix( [[1,2,3],[4,5,6]], dtype='int32' )
        >>> aslinearoperator( M )
        <2x3 LinearOperator with dtype=int32>
        """
        if isinstance(A, LinearOperator):
            return A

        elif isinstance(A, np.ndarray) or isinstance(A, np.matrix):
            if A.ndim > 2:
                raise ValueError('array must have ndim <= 2')
            A = np.atleast_2d(np.asarray(A))
            return MatrixLinearOperator(A)

        elif isspmatrix(A):
            return MatrixLinearOperator(A)

        else:
            if hasattr(A, 'shape') and hasattr(A, 'matvec'):
                rmatvec = None
                dtype = None

                if hasattr(A, 'rmatvec'):
                    rmatvec = A.rmatvec
                if hasattr(A, 'dtype'):
                    dtype = A.dtype
                return LinearOperator(A.shape, A.matvec,
                                      rmatvec=rmatvec, dtype=dtype)

            else:
                raise TypeError('type not understood')
else:

    from scipy.sparse.linalg.interface import LinearOperator
    from scipy.sparse.linalg.interface import MatrixLinearOperator
    from scipy.sparse.linalg.interface import _SumLinearOperator
    from scipy.sparse.linalg.interface import _ProductLinearOperator
    from scipy.sparse.linalg.interface import _ScaledLinearOperator

        
                


            



