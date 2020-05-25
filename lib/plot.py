import numpy as np
import control as ctl
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from .utils import get_T_max, nichols_grid

color_list = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#EF553B", "brown"]

# Utility Function
def default_layout(xlabel, ylabel, name):
    layout = {
        "xaxis": {"title": {"text": xlabel}},
        "yaxis": {"title": {"text": ylabel}},
        "title": {"text": name},
    }
    return layout


def impulse(tf_list=[], N=100, T=None, name=None):

    data = []
    T_max = get_T_max(tf_list,T=T,N=N)

    for index,tf in enumerate(tf_list):
        if ctl.isctime(tf):
            T = np.linspace(0,T_max,N)
            line_shape="linear"
        else:
            T = np.arange(0,T_max,tf.dt)
            line_shape="hv"
        
        t,y = ctl.impulse_response(tf, T=T)
        tf_name = "tf {}".format(index+1)
        data.append({"x":np.ravel(t),"y":np.ravel(y),"name":tf_name,"mode":"lines","showlegend":False,"line_shape":line_shape})

    layout = default_layout("time (s)", "response", name)
    fig = go.Figure(data, layout=layout)
    return fig


def step(tf_list=[], N=100, T=None, name=None):

    data = []
    T_max = get_T_max(tf_list,T=T,N=N)

    for index,tf in enumerate(tf_list):
        if ctl.isctime(tf):
            T = np.linspace(0,T_max,N)
            line_shape="linear"
        else:
            T = np.arange(0,T_max,tf.dt)
            line_shape="hv"
        
        t,y = ctl.step_response(tf, T=T)
        tf_name = "tf {}".format(index+1)
        data.append({"x":np.ravel(t),"y":np.ravel(y),"name":tf_name,"mode":"lines","showlegend":False,"line_shape":line_shape})

    layout = default_layout("time (s)", "response", name)
    fig = go.Figure(data, layout=layout)
    return fig


# ZERO POLE PLOT
def pzmap(tf_list=[], name=None, layout=None):

    hovertemplate_pole = (
        "<b>Pole<b><br><b>real</b>: %{x:.3f}<br><b>imag</b>: %{y:.3f}<br>"
    )
    hovertemplate_zero = (
        "<b>Zero<b><br><b>real</b>: %{x:.3f}<br><b>imag</b>: %{y:.3f}<br>"
    )

    data = []
    max = 0
    for index, tf in enumerate(tf_list):
        line_pole = dict(color=color_list[index])
        line_zero = dict(color=color_list[index])
        z = tf.zero()
        p = tf.pole()

        tf_name = "tf {}".format(index + 1)
        data.append(
            {
                "x": np.real(p),
                "y": np.imag(p),
                "name": tf_name,
                "line": line_pole,
                "hovertemplate": hovertemplate_pole,
                "mode": "markers",
                "marker": {"symbol": "x", "size": 8},
            }
        )
        data.append(
            {
                "x": np.real(z),
                "y": np.imag(z),
                "name": tf_name,
                "line": line_zero,
                "hovertemplate": hovertemplate_zero,
                "mode": "markers",
                "marker": {"symbol": "circle", "size": 8},
            }
        )
        # change max
        max_temp = np.max(np.hstack((np.abs(z), np.abs(p))))
        if max_temp > max:
            max = max_temp

    # create PLotly figure
    layout = default_layout("Real", "Imag", name)
    layout["xaxis"]["range"] = [-1.5 * max, 1.5 * max]
    layout["yaxis"]["scaleanchor"] = "x"
    layout["yaxis"]["scaleratio"] = 1
    fig = go.Figure(data, layout=layout)
    return fig


# BODE PLOT
def bode(tf_list=[], omega=None, name=None):

    hovertemplate_mag = "<b>w</b>: %{x:.3f} rad/s<br><b>mag</b>: %{y:.3f} dB<br><b>phase</b>: %{text:.3f} deg<br>"
    hovertemplate_phase = "<b>w</b>: %{x:.3f} rad/s<br><b>mag</b>: %{text:.3f} dB<br><b>phase</b>: %{y:.3f} deg<br>"

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True)

    for index, tf in enumerate(tf_list):

        mag_list, phase_list, omega = ctl.bode_plot(tf, omega=omega, Plot=False, omega_limits=None, omega_num=None, margins=None)
        mag = 20 * np.log10(mag_list)
        phase = phase_list * 180 / np.pi
        tf_name = "tf {}".format(index + 1)
        data_mag = {
            "x": omega,
            "y": mag,
            "name": tf_name,
            "hovertemplate": hovertemplate_mag,
            "text": phase,
            "showlegend": False,
        }
        data_phase = {
            "x": omega,
            "y": phase,
            "name": tf_name,
            "hovertemplate": hovertemplate_phase,
            "text": mag,
            "showlegend": False,
        }

        # add to plotly
        fig.add_trace(data_mag, row=1, col=1)
        fig.add_trace(data_phase, row=2, col=1)

    fig.update_yaxes(title_text="Magnitude", row=1, col=1)
    fig.update_xaxes(title_text="w (rad/s)", type="log", row=1, col=1)
    fig.update_yaxes(title_text="Phase", row=2, col=1)
    fig.update_xaxes(title_text="w (rad/s)", type="log", row=2, col=1)
    return fig


def nichols(tf_list=[], omega=None, show_mag_grid=True, show_phase_grid=False, cl_mags=None, cl_phases=None, name=None):

    xlabel = "Phase (deg)"
    ylabel = "Magnitude (dB)"
    hovertemplate = "<b>w</b>: %{text:.3f} rad/s<br><b>mag</b>: %{y:.3f} dB<br><b>phase</b>: %{x:.3f} deg<br>"

    data_mag = []
    data_phase = []
    data = []

    for index, tf in enumerate(tf_list):

        mag_list, phase_list, omega = ctl.bode_plot(
            tf, omega=omega, Plot=False, omega_limits=None, omega_num=None, margins=None
        )
        mag = 20 * np.log10(mag_list)
        phase = phase_list * 180 / np.pi
        tf_name = "tf {}".format(index + 1)
        data.append(
            {
                "x": phase,
                "y": mag,
                "name": tf_name,
                "hovertemplate": hovertemplate,
                "text": omega,
                "showlegend": False,
            }
        )

    # create PLotly figure
    layout = default_layout("Phase (deg)", "Magnitude (dB)", name)
    fig = go.Figure(data, layout=layout)

    # add contours
    mag_list, phase_list = nichols_grid(cl_mags, cl_phases)
    if show_mag_grid:
        line_mag = dict(color="#555", width=1, dash="dot")

        for mag in mag_list:
            fig.add_trace(
                go.Scatter(mag, hoverinfo="name", showlegend=False, line=line_mag)
            )

    if show_phase_grid:
        line_phase = dict(color="#555", width=1, dash="dot")

        for phase in phase_list:
            fig.add_trace(
                go.Scatter(phase, hoverinfo="name", showlegend=False, line=line_phase)
            )

    return fig


def rlocus(tf_list=[],kvect=np.logspace(-2,1.2,1000), xlim=None, ylim=None, show_grid=None):
    """Root locus plot
        
        Calculate the root locus by finding the roots of 1+k*TF(s) where TF is self.num(s)/self.den(s) and each k is an element of kvect.
    """

    xlabel = "Real Axis"
    ylabel = "Imag Axis"
    ylabel = "Magnitude (dB)"
    hovertemplate = "<b>K</b>: %{text:.3f}<br><b>imag</b>: %{y:.3f}<br><b>real</b>: %{x:.3f}<br>m: %{customdata[0]:.3f}<br>wn: %{customdata[1]:.3f} rad/s"
    
    data = []
    xlim = []
    ylim = []
    for index,tf in enumerate(tf_list):

        r_list,k_list  = ctl.rlocus(tf, kvect, xlim=xlim, ylim=ylim, Plot=False)
        
        #get ylim and xlim
        xlim_max = np.max(np.real(np.ravel(r_list)))
        xlim_min = np.min(np.real(np.ravel(r_list)))
        ylim_max = np.max(np.imag(np.ravel(r_list)))
        ylim_min = np.min(np.imag(np.ravel(r_list)))
        xlim = 1.2*np.array([xlim_min,xlim_max])
        ylim = 1.2*np.array([ylim_min,ylim_max])
        
        tf_name = "tf {}".format(index+1)
        r_list = np.transpose(r_list)
        
        first_point = dict(color = '#555', width = 1,dash = "dot")
        
        for index_r in range(len(r_list)) :
            r_temp = r_list[index_r]
            #compute equivalent continuous m, wn
            r_list_comp =r_list.astype(complex) # WTF: the python control "damp" function is buggy due to this missing cast !
            r_list_continuous = np.log(r_list_comp)/tf.dt
            wn_vect = np.abs(r_list_continuous)
            m_vect = -np.real(r_list_continuous)/wn_vect
            custom_data = np.dstack((m_vect, wn_vect))[0]

            data.append({"x":np.real(r_temp),"y":np.imag(r_temp),"name":tf_name,"customdata":custom_data,"hovertemplate": hovertemplate ,"text":k_list,"showlegend":False})
            data.append({"x":[np.real(r_temp[0])],"y":[np.imag(r_temp[0])],"line":first_point, "mode": "markers","marker":{"symbol":"x","size":8},"showlegend":False})


    layout = default_layout("Real Axis","Imag Axis",name=None)
    fig = go.Figure(data,layout=layout)
    return fig
