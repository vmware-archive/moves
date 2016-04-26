import os
import random
import cPickle

import pandas as pd
import numpy as np
#from matplotlib import pyplot as plt
from scipy import signal
import scipy
from scipy.signal import butter, lfilter
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import ExtraTreesClassifier
#from sklearn.lda import LDA
from sklearn.metrics import confusion_matrix

from sliding_window import sliding_window

def median_row_by_row(X,n):
    X_filter = np.zeros([X.shape[0],X.shape[1]])
    for i,x in enumerate(X):
        X_filter[i] = scipy.ndimage.filters.median_filter(x,size = n)
    return X_filter

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
    return signal.periodogram(ts,fs=fs)[1] # periodogram

def gen_fd_features(ts,fmin,fmax,fs):
    pc_norm = gen_periodogram(ts,fmin,fmax,fs,True)
    pc_no_norm = gen_periodogram(ts,fmin,fmax,fs,False)
    return np.hstack([pc_norm,pc_no_norm])

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
