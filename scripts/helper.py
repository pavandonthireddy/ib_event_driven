import numpy as np
import cvxpy as cp
import cvxopt
import scipy


def smooth(x, window_len=11, window='hanning'):
    """smooth the data using a window with requested size.

    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.

    input:
        x: the input signal
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal

    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)

    see also:

    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter

    TODO: the window parameter could be the window itself if an array instead of a string
    NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
    """

    if x.ndim != 1:
        raise ValueError("smooth only accepts 1 dimension arrays.")

    if x.size < window_len:
        raise ValueError("Input vector needs to be bigger than window size.")

    if window_len < 3:
        return x

    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman', 'gaussian']:
        raise ValueError("Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")

    s = np.r_[x[window_len - 1:0:-1], x, x[-2:-window_len - 1:-1]]
    # print(len(s))
    if window == 'flat':  # moving average
        w = np.ones(window_len, 'd')
    elif window == 'gaussian':
        w = scipy.signal.windows.gaussian(window_len, std=50, sym=True)
    else:
        w = eval('np.' + window + '(window_len)')

    y = np.convolve(w / w.sum(), s, mode='valid')
    return y


def l1_filter(y,vlambda = 50 ):
    n = y.size

    # Form second difference matrix.
    e = np.ones((1, n))
    D = scipy.sparse.spdiags(np.vstack((e, -2 * e, e)), range(3), n - 2, n)

    # Set regularization parameter.


    # Solve l1 trend filtering problem.
    x = cp.Variable(shape=n)
    obj = cp.Minimize(0.5 * cp.sum_squares(y - x)
                      + vlambda * cp.norm(D * x, 1))
    prob = cp.Problem(obj)

    # ECOS and SCS solvers fail to converge before
    # the iteration limit. Use CVXOPT instead.
    prob.solve(solver=cp.CVXOPT, verbose=True)
    print('Solver status: {}'.format(prob.status))

    # Check for error.
    if prob.status != cp.OPTIMAL:
        raise Exception("Solver did not converge!")

    # print("optimal objective value: {}".format(obj.value))

    return np.array(x.value)


def neigh_block(details, n, sigma):
    res = []
    L0 = int(np.log2(n) // 2)
    L1 = max(1, L0 // 2)
    L = L0 + 2 * L1
    def nb_beta(sigma, L, detail):
        S2 = np.sum(detail ** 2)
        lmbd = 4.2 # solution of lmbd - log(lmbd) = 3
        beta = (1 - lmbd * L * sigma**2 / S2)
        return max(0, beta)
    for d in details:
        d2 = d.copy()
        for start_b in range(0, len(d2), L0):
            end_b = min(len(d2), start_b + L0)
            start_B = start_b - L1
            end_B = start_B + L
            if start_B < 0:
                end_B -= start_B
                start_B = 0
            elif end_B > len(d2):
                start_B -= end_B - len(d2)
                end_B = len(d2)
            assert end_B - start_B == L
            d2[start_b:end_b] *= nb_beta(sigma, L, d2[start_B:end_B])
        res.append(d2)
    return res

def madev(d, axis=None):
    """ Mean absolute deviation of a signal """
    return np.mean(np.absolute(d - np.mean(d, axis)), axis)

def mead(arr):
    """ Median Absolute Deviation: a "Robust" version of standard deviation.
        Indices variabililty of the sample.
        https://en.wikipedia.org/wiki/Median_absolute_deviation
    """
    arr = np.ma.array(arr).compressed() # should be faster to not use masked arrays.
    med = np.median(arr)
    return np.median(np.abs(arr - med))