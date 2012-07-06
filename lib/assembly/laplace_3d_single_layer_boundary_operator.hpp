// Copyright (C) 2011-2012 by the BEM++ Authors
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.

#ifndef bempp_laplace_3d_single_layer_boundary_operator_hpp
#define bempp_laplace_3d_single_layer_boundary_operator_hpp

#include "laplace_3d_boundary_operator_base.hpp"
#include "boundary_operator.hpp"

#include "../common/boost_make_shared_fwd.hpp"

namespace Bempp
{

template <typename BasisFunctionType, typename ResultType>
struct Laplace3dSingleLayerBoundaryOperatorImpl;

template <typename BasisFunctionType, typename ResultType>
class Laplace3dSingleLayerBoundaryOperator;

/** \ingroup laplace_3d
 *  \brief Single-layer-potential operator for the Laplace equation in 3D.
 *
 *  \tparam BasisFunctionType
 *    Type used to represent the values of basis functions.
 *  \tparam ResultType
 *    Type used to represent entries in the discrete form of the operator.
 *
 *  Both template parameters can take the following values: \c float, \c
 *  double, <tt>std::complex<float></tt> and <tt>std::complex<double></tt>.
 *  Both types must have the same precision: for instance, mixing \c float with
 *  <tt>std::complex<double></tt> is not allowed. The parameter \p ResultType
 *  is by default set to \p BasisFunctionType. You should override that only if
 *  you set \p BasisFunctionType to a real type, but you want the entries of
 *  the operator's weak form to be stored as complex numbers.
 *
 *  \see laplace_3d */
template <typename BasisFunctionType_, typename ResultType_ = BasisFunctionType_>
class Laplace3dSingleLayerBoundaryOperator :
        public Laplace3dBoundaryOperatorBase<
        Laplace3dSingleLayerBoundaryOperatorImpl<BasisFunctionType_, ResultType_>,
        BasisFunctionType_,
        ResultType_>
{
    typedef Laplace3dBoundaryOperatorBase<
    Laplace3dSingleLayerBoundaryOperatorImpl<BasisFunctionType_, ResultType_>,
    BasisFunctionType_,
    ResultType_>
    Base;
public:
    typedef typename Base::BasisFunctionType BasisFunctionType;
    typedef typename Base::KernelType KernelType;
    typedef typename Base::ResultType ResultType;
    typedef typename Base::CoordinateType CoordinateType;
    typedef typename Base::CollectionOfBasisTransformations
    CollectionOfBasisTransformations;
    typedef typename Base::CollectionOfKernels CollectionOfKernels;
    typedef typename Base::TestKernelTrialIntegral TestKernelTrialIntegral;

    Laplace3dSingleLayerBoundaryOperator(
            const shared_ptr<const Space<BasisFunctionType> >& domain,
            const shared_ptr<const Space<BasisFunctionType> >& range,
            const shared_ptr<const Space<BasisFunctionType> >& dualToRange,
            const std::string& label);
};

template <typename BasisFunctionType, typename ResultType>
BoundaryOperator<BasisFunctionType, ResultType>
laplace3dSingleLayerBoundaryOperator(
        const shared_ptr<const Context<BasisFunctionType, ResultType> >& context,
        const shared_ptr<const Space<BasisFunctionType> >& domain,
        const shared_ptr<const Space<BasisFunctionType> >& range,
        const shared_ptr<const Space<BasisFunctionType> >& dualToRange,
        const std::string& label = "");

} // namespace Bempp

#endif
