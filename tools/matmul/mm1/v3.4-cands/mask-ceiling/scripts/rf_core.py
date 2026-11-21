#!/usr/bin/env python3
"""mask-ceiling (Q238 track C): the nonparametric learners, this lane's own numpy code (no library learner): a CART regression tree (least
squares splits at midpoints between distinct sorted values, a minimum leaf on both sides), a random forest of such trees (bootstrap rows,
mtry features drawn without replacement at each node, the prediction the mean of the trees), and k nearest neighbours (Euclidean on the
training rows' standardized features, the mean of the k nearest targets). Deterministic for a given numpy Generator.
Desk; /usr/bin/python3 3.12.3 -I -B, numpy 1.26.4, single-threaded.
SPDX-License-Identifier: Apache-2.0
"""
import numpy as np


class Tree:
    def __init__(self, feat, thr, left, right, val, imp):
        self.feat, self.thr, self.left, self.right, self.val, self.imp = feat, thr, left, right, val, imp

    def predict(self, X):
        node = np.zeros(len(X), int)
        while True:
            lf = self.left[node]
            go = lf >= 0
            if not go.any():
                return self.val[node]
            r = np.nonzero(go)[0]
            nd = node[r]
            x = X[r, self.feat[nd]]
            node[r] = np.where(x <= self.thr[nd], self.left[nd], self.right[nd])

    def to_json(self):
        return {'feat': self.feat.tolist(), 'thr': self.thr.tolist(), 'left': self.left.tolist(), 'right': self.right.tolist(),
                'val': self.val.tolist()}

    @staticmethod
    def from_json(d):
        return Tree(np.array(d['feat'], int), np.array(d['thr'], float), np.array(d['left'], int), np.array(d['right'], int),
                    np.array(d['val'], float), None)


def fit_tree(X, y, max_depth, min_leaf, mtry, rng):
    n, p = X.shape
    feat, thr, left, right, val = [], [], [], [], []
    imp = np.zeros(p)

    def build(idx, depth):
        node = len(val)
        yi = y[idx]
        feat.append(-1)
        thr.append(0.0)
        left.append(-1)
        right.append(-1)
        val.append(float(yi.mean()))
        n_ = len(idx)
        if depth >= max_depth or n_ < 2 * min_leaf:
            return node
        tot = float(yi.sum())
        base = tot * tot / n_
        if float(((yi - yi.mean()) ** 2).sum()) <= 1e-18:
            return node
        cand = rng.choice(p, size=mtry, replace=False) if mtry < p else np.arange(p)
        best_gain, best_j, best_t = 1e-15, None, None
        ii = np.arange(min_leaf - 1, n_ - min_leaf)
        nl = ii + 1.0
        nr = n_ - nl
        for j in cand:
            xj = X[idx, j]
            o = np.argsort(xj, kind='mergesort')
            xs = xj[o]
            cs = np.cumsum(yi[o])
            valid = xs[ii] < xs[ii + 1]
            if not valid.any():
                continue
            sl = cs[ii]
            sc = sl * sl / nl + (tot - sl) ** 2 / nr
            sc[~valid] = -np.inf
            k = int(np.argmax(sc))
            g = float(sc[k] - base)
            if g > best_gain:
                best_gain, best_j, best_t = g, int(j), 0.5 * (xs[ii[k]] + xs[ii[k] + 1])
        if best_j is None:
            return node
        m = X[idx, best_j] <= best_t
        feat[node] = best_j
        thr[node] = best_t
        imp[best_j] += best_gain
        left[node] = build(idx[m], depth + 1)
        right[node] = build(idx[~m], depth + 1)
        return node

    build(np.arange(n), 0)
    return Tree(np.array(feat, int), np.array(thr, float), np.array(left, int), np.array(right, int), np.array(val, float), imp)


class Forest:
    def __init__(self, trees):
        self.trees = trees

    def predict(self, X):
        return np.mean([t.predict(X) for t in self.trees], axis=0)

    def importance(self):
        return np.sum([t.imp for t in self.trees], axis=0)

    def to_json(self):
        return [t.to_json() for t in self.trees]

    @staticmethod
    def from_json(L):
        return Forest([Tree.from_json(d) for d in L])


def fit_forest(X, y, n_trees, max_depth, min_leaf, mtry, rng, bootstrap=True):
    n = len(y)
    trees = []
    for _ in range(n_trees):
        b = rng.integers(0, n, n) if bootstrap else np.arange(n)
        trees.append(fit_tree(X[b], y[b], max_depth, min_leaf, mtry, rng))
    return Forest(trees)


class KNN:
    def __init__(self, X, y, k):
        self.mu = X.mean(axis=0)
        sd = X.std(axis=0)
        self.sd = np.where(sd > 0, sd, 1.0)
        self.Z = (X - self.mu) / self.sd
        self.y = y
        self.k = min(k, len(y))

    def predict(self, X):
        Z = (X - self.mu) / self.sd
        d = ((Z[:, None, :] - self.Z[None, :, :]) ** 2).sum(axis=2)
        nn = np.argsort(d, axis=1, kind='mergesort')[:, :self.k]
        return self.y[nn].mean(axis=1)


def _selftest():
    """synthetic data only (no lab residual): a step function and an interaction must be found; prints the time a forest takes"""
    import time
    rng = np.random.default_rng(1)
    n, p = 1150, 24
    X = rng.normal(size=(n, p))
    y = 0.1 * (X[:, 3] > 0.5) - 0.05 * (X[:, 7] > 0) * (X[:, 11] < 0) + 0.01 * rng.normal(size=n)
    t0 = time.time()
    t = fit_tree(X, y, 4, 10, p, np.random.default_rng(2))
    print('tree: root feature', t.feat[0], 'nodes', len(t.val), 'time %.3f s' % (time.time() - t0))
    t0 = time.time()
    f = fit_forest(X, y, 200, 6, 5, 8, np.random.default_rng(3))
    tf = time.time() - t0
    Xt = rng.normal(size=(300, p))
    yt = 0.1 * (Xt[:, 3] > 0.5) - 0.05 * (Xt[:, 7] > 0) * (Xt[:, 11] < 0)
    e = f.predict(Xt) - yt
    print('forest 200 trees: %.2f s; test rms %.4f (signal rms %.4f); top importances %s' % (
        tf, np.sqrt(np.mean(e * e)), np.sqrt(np.mean(yt * yt)), np.argsort(-f.importance())[:3].tolist()))
    kn = KNN(X, y, 10)
    e2 = kn.predict(Xt) - yt
    print('knn: test rms %.4f' % np.sqrt(np.mean(e2 * e2)))
    t2 = Forest.from_json(f.to_json())
    assert np.array_equal(t2.predict(Xt), f.predict(Xt)), 'round trip'
    print('round trip exact')


if __name__ == '__main__':
    _selftest()
