import control as ctl
import numpy as np
from .utils import get_T_max
from scipy.signal.ltisys import _default_response_times

def pole(sys):
    return sys.pole()

def zero(sys):
    return sys.zero()

def damp(sys):
    
    is_continuous = ctl.isctime(sys)
    
    for pole in sys.pole():
        pole = pole.astype(complex) # WTF: the python control "damp" function is buggy due to this missing cast !

        if is_continuous:
            pole_continuous = pole
        else:
            pole_continuous = np.log(pole)/sys.dt
        
        wn = np.abs(pole_continuous)
        m = -np.real(pole_continuous)/wn
        print("poles {:.3f} : wn={:.3f} rad/s, m= {:.3f}".format(pole, wn, m))


def stepinfo(sys, display=False, T=None, SettlingTimeThreshold=0.05,RiseTimeLimits=(0.1, 0.9)):

    T_max = get_T_max([sys],T=None,N=200)

    if T is None:
        if ctl.isctime(sys):
            T = np.linspace(0,T_max,200)
        else:
            # For discrete time, use integers
            T = np.arange(0,T_max,sys.dt)

    info = ctl.step_info(sys,T,SettlingTimeThreshold=0.05,RiseTimeLimits=(0.1, 0.9))
    
    if display == True :
        for keys,values in info.items():
            print("{} :\t{:.5f}".format(keys,values))

    return info
