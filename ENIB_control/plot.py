from plotly.subplots import make_subplots
from scipy.signal.ltisys import _default_response_times
import plotly.graph_objects as go
import control as ctl
import numpy as np
from .utils import *

color_list = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",  "#EF553B", "brown"]   


# Utility Function
def default_layout(xlabel,ylabel,name):
        layout =   {"xaxis":{"title":{"text":xlabel}},
                    "yaxis":{"title":{"text":ylabel}},
                    "title":{"text":name}
                }
        return layout

def create_list(input):
    if not hasattr(input, "__len__"):
        input = [input]
    return input

def default_T(tf_list,N):
    t_max = 0
    for tf in tf_list:
        ss = ctl.tf2ss(tf)
        T_temp = _default_response_times(ss.A, N)
        t_max_temp = T_temp[-1]
        if t_max_temp > t_max:
            t_max = t_max_temp
            T = T_temp
    return T


def impulse(tf_list=[],N=100,T=None,name=None):
    
    data = []
    if T is None :
        T = default_T(tf_list,N=N)

    for index,tf in enumerate(create_list(tf_list)):
        t,y = ctl.impulse_response(tf, T=T)
        
        if hasattr(tf, "name"):
            tf_name = tf.name
        else:
            tf_name = "tf {}".format(index+1)
        data.append({"x":t,"y":y,"name":tf_name,"showlegend":False})


    layout = default_layout("time (s)","response",name)
    fig = go.Figure(data,layout=layout)
    fig.show()

def step(tf_list=[],N=100,T=None,name=None):
    
    data = []
    if T is None :
        T = default_T(tf_list,N=N)
        
    for index,tf in enumerate(create_list(tf_list)):
        t,y = ctl.step_response(tf, T=T)

        if hasattr(tf, "name"):
            tf_name = tf.name
        else:
            tf_name = "tf {}".format(index+1)
        data.append({"x":t,"y":y,"name":tf_name,"showlegend":False})
    
    
    layout = default_layout("time (s)","response",name)
    fig = go.Figure(data,layout=layout)
    fig.show()


# ZERO POLE PLOT
def pzmap(tf_list=[],name=None,layout=None):
    
    hovertemplate_pole = "<b>Pole<b><br><b>real</b>: %{x:.3f}<br><b>imag</b>: %{y:.3f}<br>"
    hovertemplate_zero = "<b>Zero<b><br><b>real</b>: %{x:.3f}<br><b>imag</b>: %{y:.3f}<br>"

    tf_list = create_list(tf_list)
    data = []
    for index,tf in enumerate(tf_list):
        line_pole = dict(color=color_list[index])
        line_zero = dict(color=color_list[index])
        z = tf.zero()
        p = tf.pole()
        
        if hasattr(tf, "name"):
            tf_name = tf.name
        else:
            tf_name = "tf {}".format(index+1)
        
        data.append({"x":np.real(p),"y":np.imag(p),"name":tf_name,"line":line_pole,"hovertemplate": hovertemplate_pole, "mode": "markers","marker":{"symbol":"x","size":8}})
        data.append({"x":np.real(z),"y":np.imag(z),"name":tf_name,"line":line_zero,"hovertemplate": hovertemplate_zero, "mode": "markers","marker":{"symbol":"circle","size":8}})

    # create PLotly figure
    layout = default_layout("Real","Imag",name)
    layout["yaxis"]["scaleanchor"] = "x"
    layout["yaxis"]["scaleratio"] = 1
   
    fig = go.Figure(data,layout=layout)
    fig.show()


# BODE PLOT
def bode(tf_list=[],omega=None,name=None):

    hovertemplate_mag = "<b>w</b>: %{x:.3f} rad/s<br><b>mag</b>: %{y:.3f} dB<br><b>phase</b>: %{text:.3f} deg<br>"
    hovertemplate_phase = "<b>w</b>: %{x:.3f} rad/s<br><b>mag</b>: %{text:.3f} dB<br><b>phase</b>: %{y:.3f} deg<br>"
    
    fig = make_subplots(rows=2, cols=1,shared_xaxes=True)
    tf_list = create_list(tf_list)
    
    mag_list,phase_list,omega_list = ctl.bode_plot(tf_list , omega=None,Plot=False, omega_limits=None, omega_num=None,margins=None)
    
    for index,tf in enumerate(tf_list):
        
        omega = omega_list[index]
        mag = 20*np.log10(mag_list[index])
        phase = phase_list[index]*180/np.pi
        
        if hasattr(tf, "name"):
            tf_name = tf.name
        else:
            tf_name = "tf {}".format(index+1)
    
        data_mag= {"x":omega,"y":mag,"name":tf_name,"hovertemplate": hovertemplate_mag ,"text":phase,"showlegend":False}
        data_phase = {"x":omega,"y":phase,"name":tf_name,"hovertemplate": hovertemplate_phase,"text":mag,"showlegend":False}

        #add to plotly
        fig.add_trace(data_mag,row=1, col=1)
        fig.add_trace(data_phase,row=2, col=1)
    
    fig.update_yaxes(title_text="Magnitude",row=1, col=1)
    fig.update_xaxes(title_text="w (rad/s)",type="log",row=1, col=1)
    fig.update_yaxes(title_text="Phase",row=2, col=1)
    fig.update_xaxes(title_text="w (rad/s)",type="log",row=2, col=1)
    fig.show()


def nichols(tf_list=[],omega=None,show_mag_grid=True,show_phase_grid=False,cl_mags = None,cl_phases = None, name=None):

    xlabel = "Phase (deg)"
    ylabel = "Magnitude (dB)"

    data_mag = []
    data_phase = []
    hovertemplate = "<b>w</b>: %{text:.3f} rad/s<br><b>mag</b>: %{y:.3f} dB<br><b>phase</b>: %{x:.3f} deg<br>"
    data = []

    mag_list,phase_list,omega_list = ctl.bode_plot(tf_list , omega=None,Plot=False, omega_limits=None, omega_num=None,margins=None)
    
    for index,tf in enumerate(tf_list):
        omega = omega_list[index]
        mag = 20*np.log10(mag_list[index])
        phase = phase_list[index]*180/np.pi
        
        if hasattr(tf, "name"):
            tf_name = tf.name
        else:
            tf_name = "tf {}".format(index+1)
        
        data.append({"x":phase,"y":mag,"name":tf_name,"hovertemplate": hovertemplate ,"text":omega,"showlegend":False})

    # create layout
    layout = default_layout("Phase (deg)","Magnitude (dB)",name)

    # create PLotly figure
    fig = go.Figure(data,layout=layout)
    
    # add contours
    mag_list, phase_list = nichols_grid(cl_mags,cl_phases)
    if show_mag_grid :
        line_mag = dict(color = '#555', width = 1,dash = "dot")
        for mag in mag_list:
            fig.add_trace(go.Scatter(mag,hoverinfo="name",showlegend=False,line = line_mag))
    
    if show_phase_grid :
        line_phase = dict(color = '#555', width = 1,dash = "dot")
        for phase in phase_list:
            fig.add_trace(go.Scatter(phase,hoverinfo="name",showlegend=False,line = line_phase))

    fig.show()


