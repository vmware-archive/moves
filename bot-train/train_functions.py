import cPickle
import os
import random

import numpy as np
import pandas as pd
import scipy
from scipy.signal import butter, lfilter, periodogram
from sklearn.ensemble import RandomForestClassifier

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

#bin frequency data
def bin_array(X,n):
    X_binned = []
    for row in X:
        x_binned = []
        x_binned = np.array([np.mean(row[i*n : ((i*n) + n)]) for i in range(X.shape[1]/n)])
        X_binned.append(x_binned)
    return np.array(X_binned)

def gen_periodogram(ts,fmin,fmax,fs,norm = True):
    if norm:
        ts = znorm(ts)
    ts = bp_row_by_row(ts,fmin,fmax,fs) # bandpass filter
    ts = median_row_by_row(ts,1) # median filter
    return periodogram(ts,fs=fs)[1] # periodogram

def gen_fd_features(ts,fmin,fmax,fs):
    pc_norm = gen_periodogram(ts,fmin,fmax,fs,True)
    pc_no_norm = gen_periodogram(ts,fmin,fmax,fs,False)
    return np.hstack([pc_norm,pc_no_norm])

def gen_td_features(ts):
    f = []
    if len(ts.shape) == 1: # not enough training data!
        return
    f.append(np.mean(ts,axis=1))
    f.append(np.std(ts,axis=1))
    f.append(np.mean(abs(ts),axis=1))
    f.append(np.min(abs(ts),axis=1))
    f.append(np.max(abs(ts),axis=1))
    f.append(scipy.stats.kurtosis(abs(ts),axis=1))
    return np.transpose(f)

# time domain windows
def gen_td_examples(df,win_size,over_lap,headers,label):
    df = df[(df['label'] == label)]
    examples = [sliding_window(np.array(df[c]),win_size,over_lap) for c in headers]
    return (examples,[label] * len(examples[0]))

def apply_model(tc,clf):
    tF = np.hstack([gen_td_features(ts[None,:]) for ts in tc])
    fF = np.hstack([gen_fd_features(ts[None,:],0,8,15) for ts in tc])
    x = np.hstack([tF,fF])
    #TODO argmax?
    prob = max(clf.predict_proba(x)[0])
    pred_label = clf.predict(x)[0]
    return pred_label,prob

import random

def train_model(data_store_key, r):
    # variables
    win_size = 30 
    fmin,fmax,sr = 0,8,win_size
    over_lap = win_size/2
    component_names = ['x','y','z']
    cnames = ['time','label'] + component_names

    def json2ts(di):
        time_label = [eval(di)[v] for v in ['timestamp','label']]
        xyz = [float(eval(di)['motion'][c]) for c in ['x','y','z']]
        return time_label + xyz

    print data_store_key
    td = [json2ts(v) for v in r.lrange(data_store_key,0,-1)]
    df = pd.DataFrame(td,columns = cnames)
    movement_names = set(df['label'])
    print movement_names
    # build features
    y,mw = [],[]
    for label in movement_names:
        _mw,_y = gen_td_examples(df,win_size,over_lap,component_names,label)
        print "{}: {} training examples".format(label, _mw[0].shape[0])
        mw.append(_mw)
        y.extend(_y)
        
    if not mw:
        return 0
        
    mw = np.hstack(mw)
    y = np.array(y)

    tF = np.hstack([gen_td_features(ts) for ts in mw])
    fF = np.hstack([gen_fd_features(ts,fmin,fmax,sr) for ts in mw])
    X  = np.hstack([tF,fF])

    cl = RandomForestClassifier(n_estimators=150)
    cl.fit(X, y)

    return cl

