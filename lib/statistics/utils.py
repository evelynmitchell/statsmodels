import numpy as N
import numpy.linalg as L
import scipy

def inv(X):
    """
    Return the reciprocal of an array, setting all entries less than or
    equal to 0 to 0. Therefore, it presumes that X should be positive in
    general.
    """
    x = N.maximum(N.array(X).astype(N.Float), 0)
    return N.greater(x, 0.) / (x + N.less_equal(x, 0.))

def inv0(X):
    """
    Return the reciprocal of an array, setting all entries equal to 0
    as 0. It does not assume that X should be positive in
    general.
    """
    test = N.equal(N.array(X), 0)
    return N.where(test, 0, 1. / X)

def clean0(matrix):
    """
    Erase columns of zeros: saves some time in pseudoinverse.
    """

    colsum = N.add.reduce(matrix**2, 0)

    val = [matrix[:,i] for i in N.nonzero(colsum)]
    return N.array(N.transpose(val))

def norm(X, p=2, axis=0):
    """
    Return the l^p norm of X, for 0 < p < infty.
    """
    return N.pow(N.add.reduce(X**p,axis=axis),1.0/p)


def rank(X, cond=1.0e-06):
    """
    Return the rank of a matrix X based on its generalized inverse,
    not the SVD.
    """
    pX = L.pinv(X)
    V, D, U = L.svd(N.transpose(X))
    return int(N.add.reduce(N.greater(D / D[0], cond).astype(N.Int)))

def fullrank(X, r=None):
    """
    Return a matrix whose column span is the same as X.

    If the rank of X is known it can be specified as r -- no check
    is made to ensure that this really is the rank of X.

    """

    if r is None:
        r = rank(X)

    V, D, U = L.svd(X)
    order = N.argsort(D)
    order = order[::-1]
    value = []
    for i in range(r):
        value.append(V[:,order[i]])
    return N.array(N.transpose(value)).astype(N.Float)

class StepFunction:
    '''A basic step function: values at the ends are handled in the simplest way possible: everything to the left of x[0] is set to ival; everything to the right of x[-1] is set to y[-1].

    >>>
    >>> from numpy import *
    >>>
    >>> x = arange(20)
    >>> y = arange(20)
    >>>
    >>> f = StepFunction(x, y)
    >>>
    >>> print f(3.2)
    3
    >>> print f([[3.2,4.5],[24,-3.1]])
    [[ 3  4]
     [19  0]]
    >>>

    '''

    def __init__(self, x, y, ival=0., sorted=False):

        _x = N.asarray(x)
        _y = N.asarray(y)

        if _x.shape != _y.shape:
            raise ValueError, 'in StepFunction: x and y do not have the same shape'
        if len(_x.shape) != 1:
            raise ValueError, 'in StepFunction: x and y must be 1-dimensional'

        self.x = N.hstack([[-N.inf], _x])
        self.y = N.hstack([[ival], _y])

        if not sorted:
            asort = N.argsort(self.x)
            self.x = N.take(self.x, asort)
            self.y = N.take(self.y, asort)
        self.n = self.x.shape[0]

    def __call__(self, time):

        tind = scipy.searchsorted(self.x, time) - 1
        _shape = tind.shape
        return self.y[tind]


def ECDF(values):
    """
    Return the ECDF of an array as a step function.
    """
    x = N.array(values, copy=True)
    x.sort()
    x.shape = N.product(x.shape)
    n = x.shape[0]
    y = (N.arange(n) + 1.) / n
    return StepFunction(x, y)

def monotone_fn_inverter(fn, x, vectorized=True, **keywords):
    """
    Given a monotone function x (no checking is done to verify montonocity)
    and a set of x values, return an linearly
    interpolated approximation to its inverse from its values on x.
    """

    if vectorized:
        y = fn(x, **keywords)
    else:
        y = []
        for _x in x:
            y.append(fn(_x, **keywords))
        y = N.array(y)
    return LinearInterpolant(y, x, sorted=False)
