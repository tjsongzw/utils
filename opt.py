"""

"""


import numpy as np
import scipy.linalg as la
from scipy.optimize import fmin_l_bfgs_b, fmin_tnc


def check_grad(f, fprime, x0, args, eps=10**-4, verbose=False):
    """
    """
    # computed gradient at x0
    grad = fprime(x0, **args)
    # space for the numeric gradient
    ngrad = np.zeros(grad.shape)
    # for every component of x:
    if verbose: 
        print "Number of total function calls: 2*%d"% x0.shape[0]
    for i in xrange(x0.shape[0]):
        # inplace change
        x0[i] += eps
        f1 = f(x0, **args)
        # inplace change
        x0[i] -= 2*eps
        f2 = f(x0, **args)
        # second order approximation
        ngrad[i] = (f1-f2)/(2*eps)
        # undo previous _inplace_ change 
        x0[i] += eps
    delta_2 = np.sum((grad-ngrad)**2)
    if verbose:
        print "Squared distance: %f"% delta_2
    return np.sqrt(delta_2)


def msgd(x0, fandprime, args, batch_args,
        epochs, nos, lr, btsz, beta = 0., 
        verbose=False, **params):
    """
    Minibatch stochastic gradient descent.
    """
    lr /= btsz
    #
    start = 0
    end = 0
    score = 0
    scores = []
    passes = 0
    _delta = 0
    while True:
        # prepare batches
        start = end
        end = start + btsz
        for item in batch_args:
            args[item] = batch_args[item][start:end]
        # do the work
        sc, delta = fandprime(x0, **args)
        delta += beta * _delta
        _delta = delta
        x0 -= lr*delta
        score += sc
        if (end >= nos):
            # start at beginning of data again
            end = 0
            if verbose:
                print "Epoch %d, Score %f" % (passes, score)
            scores.append(score)
            score = 0
            passes += 1
            if passes >= epochs:
                break
    lr *= btsz
    return x0, scores


def olbfgs(x0, fandprime, args, batch_args,
        eta_0, m, tau, epochs, nos, btsz, verbose=False, 
        **params):
    """
    """
    SMALL = 10**-10
    S = np.zeros((m, x0.shape[0]))
    Y = np.zeros((m, x0.shape[0]))
    rho = np.zeros(m)
    delta = np.zeros(m)
    alpha = np.zeros(m)
    index = -1
    s = 0
    y = 0
    iters = 0
    start = 0
    end = 0
    score = 0
    scores = []
    passes = 0
    while True:
        # get batch
        start = end
        end = start+btsz
        for item in batch_args:
            args[item] = batch_args[item][start:end]
        score, grad = fandprime(x0, **args)
        # compute update direction
        if iters > 0:
            eta = eta_0 * tau/(tau + iters)
            #print 'eta', eta
            p = -eta * grad
            sy = np.dot(s, y)
            if sy < 10**-8:
                print "Skipping update", iters, sy, start
                index = (index - 1)%m
                cap = min(m, iters-1)
            else:
                S[index] = s
                Y[index] = y
                yy = np.dot(y, y) 
                #print 'sx, yy', sy, yy
                rho[index] = 1./sy
                delta[index] = sy/yy
                #
                cap = min(m, iters)
            #
            alpha *= 0
            #
            i = index
            weight = 0
            for _t in xrange(cap):
                alpha[i] = rho[i] * np.dot(S[i], p)
                #print 'rho, alpha', rho[i], alpha[i]
                p -= alpha[i] * Y[i]
                # weight update
                weight += delta[i]
                #print "-", i
                i = (i-1)%m
            #print "done with -", weight/cap
            #
            p *= (weight/cap)
            #
            counter = 0
            i = (index - (cap-1)) % m
            for _t in xrange(cap):
                beta = rho[i] * np.dot(Y[i], p)
                p += (alpha[i] - beta) * S[i]
                #print "+", i
                i = (i+1)%m
            #print "done with + "
            s = p
        else:
            s = -SMALL * grad
        #
        x0 += s
        #
        _sc, y = fandprime(x0, **args)
        y -= grad
        #
        iters += 1
        index = (index + 1)%m
        del grad
        #print score
        if (end >= nos):
            # start at beginning of data again
            end = 0
            if verbose:
                print passes, score
            scores.append(score)
            score = 0
            passes += 1
            if passes >= epochs:
                break
    return x0, scores


def lbfgs(x0, fandprime, corrections):
    """
    """
    pass
#    g = ...
#    t = 0
#    for iters in xrange(maxiters):
#        if iters == 1:
#            # Start with steepes desecent direction
#            d = -g
#        else:
#            lbfgsUpdate(y, s, corrections, dirs, steps, Hdiag, idx)
#            d = lbfgsDir(-g, dirs, steps, Hdiag, idx) 
#        g_old = g
#        #
#        check_progress
#        # Initial guess for steprate
#        t = 1
#        f_old = f
#        gtd_old = gtd


def lbfgsb(func, x0, fprime=None, args=(), approx_grad=0, 
        bounds=None, m=10, factr=10000000.0, pgtol=1e-05, 
        epsilon=1e-08, iprint=-1, maxfun=15000, disp=2, **params):
    """
    """
    return fmin_l_bfgs_b(func=func, x0=x0, fprime=fprime, 
            args=args, approx_grad=approx_grad, bounds=bounds, 
            m=m, factr=factr, pgtol=pgtol, epsilon=epsilon, 
            iprint=iprint, maxfun=maxfun, disp=disp)


def tnc(func, x0, fprime=None, args=(), approx_grad=0, bounds=None,
        epsilon=1e-08, scale=None, offset=None, messages=15, 
        maxCGit=-1, maxfun=None, eta=-1, stepmx=0, accuracy=0, fmin=0, 
        ftol=-1, xtol=-1, pgtol=-1, rescale=-1, disp=5, **params):
    """
    """
    return fmin_tnc(func=func, x0=x0, fprime=fprime, args=args, 
            approx_grad=approx_grad, bounds=bounds, epsilon=epsilon, 
            scale=scale, offset=offset, messages=messages, 
            maxCGit=maxCGit, maxfun=maxfun, eta=eta, stepmx=stepmx, 
            accuracy=accuracy, fmin=fmin, ftol=ftol, xtol=xtol, 
            pgtol=pgtol, rescale=rescale, disp=disp)

def test_olbfgs(lr):
    import nn
    nn.demo_mnist(hiddens=300, opt=olbfgs, epochs=5, lr=lr, 
            btsz=128, tau=10000, m=50)
