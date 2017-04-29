# -*- coding: utf-8 -*-

"""
University of São Paulo
Mathematics and Statistics Institute
Course: MAC0460_5832 - Machine Learning - 2017/1

Student: Juliana Cavalcanti Correa
Assignment: EP1 - W-operators design
"""

from mac0460_5832.utils import *


def mask_borders(se_mask_shape):
    """
    Returns the borders to be cropped from the image
    Mask shape must consist of a pair of odd numbers
    """
    return ( (se_mask_shape[0]-1)/2, (se_mask_shape[1]-1)/2 )


def slide_window(src, se_mask, i, j):
    """
    Returns the pattern resulting from the structuring element mask
    centered at position (i,j) of the source img
    """
    (wl, wc) = mask_borders(se_mask.shape) # half-window size
    window = src[i-wl:i+wl+1, j-wc:j+wc+1]
    return np.logical_and(window, se_mask)


def pattern_hash(pattern):
    """
    Receives n-dim numpy array and converts it to a 1-dim tuple (hashable)
    """
    return tuple(pattern.flatten())


def add_to_freqtable(pattern, result, freqtable):
    pattern = pattern_hash(pattern)
    if not pattern in freqtable:
        freqtable[pattern] = { True : 0, False : 0 }
    freqtable[pattern][result] += 1


def build_pattern_freqs(trainingdata, se_mask):
    """
    Slides a window with the structuring element as a mask through the src image
    and counts the values, for each pattern, of the element in the target
    image corresponding to the position of the center of the window
    Returns a frequency table for all observed patterns, which serves as an
    estimator for P(X | pattern) where X in (True,False)
    """

    freqtable = {}
    bi, bj = mask_borders(se_mask.shape)

    for imgpair in trainingdata:
        src = imgpair[0]
        target = imgpair[1]

        for i in range(bi, src.shape[0]-bi):
            for j in range(bj, src.shape[1]-bj):
                pattern = slide_window(src, se_mask, i, j)
                result = target[i, j]
                add_to_freqtable(pattern, result, freqtable)
    return freqtable


def optimal_decision(pattern, freqtable):
    """
    Returns the value that minimizes MAE for this pattern considering the
    observations given by the frequency table
    """
    return freqtable[pattern][True] > freqtable[pattern][False]


def generate_operator(freqtable):
    """
    Returns the operator, which consists of a list of patterns for which the
    output is estimated to be valued True)
    """
    return filter(lambda x: optimal_decision(x, freqtable), freqtable.keys())


def learn_operator(trainingdata, se_mask):
    freqtable = build_pattern_freqs(trainingdata, se_mask)
    return generate_operator(freqtable)


def apply_operator(src, operator, se_mask):
    """
    Generates and returns the output image by applying the operator to src image
    """
    target = np.zeros_like(src, dtype=bool)
    bi, bj = mask_borders(se_mask.shape)
    for i in range(bi, src.shape[0]-bi):
        for j in range(bj, src.shape[1]-bj):
            if pattern_hash(slide_window(src, se_mask, i, j)) in operator:
                target[i,j] = True
    return target
