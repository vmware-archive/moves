# -*- coding: utf-8 -*-

"""
model_functions.py
~~~~~~~~~~~~~
Functions for building a movement classification model
"""

import numpy as np
import scipy
from scipy.signal import butter, lfilter, periodogram
from sklearn.ensemble import RandomForestClassifier

from sliding_window import sliding_window

# median filter
def median_row_by_row(X,n):
    X_filter = np.zeros([X.shape[0],X.shape[1]])
    for i,x in enumerate(X):
        X_filter[i] = scipy.ndimage.filters.median_filter(x,size = n)
    return X_filter

# bandpass filter
def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def butter_bandpass_filter(data, lowcut, highcut, fs, order):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

def bp_row_by_row(X,lowcut, highcut, fs, order=5):
    X_filter = np.zeros([X.shape[0],X.shape[1]])
    for i,x in enumerate(X):
        X_filter[i] = butter_bandpass_filter(x,lowcut, highcut, fs, order)
    return X_filter

# z-normalization
def znorm(s):
    s_mean   = np.mean(s,axis=1)
    s_std    = np.std(s,axis=1)
    s_demean = s - s_mean[:,None]
    s_znorm  = s_demean/s_std[:,None]
    return s_znorm

def gen_periodogram(ts,fmin,fmax,fs,norm = True):
    if norm:
        ts = znorm(ts)
    ts = bp_row_by_row(ts,fmin,fmax,fs) # bandpass filter
    ts = median_row_by_row(ts,1) # median filter
    return periodogram(ts,fs=fs)[1] # periodogram

# fd (feature domain)
def gen_fd_features(ts,fmin,fmax,fs):
    pc_norm = gen_periodogram(ts,fmin,fmax,fs,True)
    pc_no_norm = gen_periodogram(ts,fmin,fmax,fs,False)
    return np.hstack([pc_norm,pc_no_norm])

# td (time domain)
def gen_td_features(ts):
    f = []
    f.append(np.mean(ts,axis=1))
    f.append(np.std(ts,axis=1))
    f.append(np.mean(abs(ts),axis=1))
    f.append(np.min(abs(ts),axis=1))
    f.append(np.max(abs(ts),axis=1))
    f.append(scipy.stats.kurtosis(abs(ts),axis=1))
    return np.transpose(f)

def apply_model(tc,clf,fmin,fmax,sr):
    tF = np.hstack([gen_td_features(ts[None,:]) for ts in tc])
    fF = np.hstack([gen_fd_features(ts[None,:],fmin,fmax,sr) for ts in tc])
    x = np.hstack([tF,fF])
    #TODO argmax?
    prob = max(clf.predict_proba(x)[0])
    pred_label = clf.predict(x)[0]
    return pred_label,prob
