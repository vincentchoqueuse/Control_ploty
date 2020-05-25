import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from scipy import signal
from .utils import nichols_grid
from .core import nicchart, rlocus_chart, drlocus_chart,pole_info
from control import feedback, bode_plot
import plotly
import json



def figure(type):
    if type=="time":
        fig = Time_Figure()
    if type == "pzmap":
        fig = PZmap_Figure()
    if type == "bode":
        fig = Bode_Figure()
    if type == "nichols":
        fig = Nichols_Figure()
    if type == "rlocus":
        fig = Rlocus_Figure()
    return fig

class Figure():

    color_list = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#EF553B", "brown"]
    
    def __init__(self):
        self.data = []
        self.type = None
        self.layout = None
        self.index = 0
        self.x_range = None
        self.y_range = None
    
    def get_layout(self):
        layout =  { "xaxis": {"title": {"text": ""}},"yaxis": {"title": {"text": ""}}}
        return layout
    
    def get_next_color(self):
        color = self.color_list[self.index]
        self.index +=1
        return color
    
    def get_grid_line(self):
        return dict(color="#555", width=1, dash="dot")
    
    def get_line_shape(self,sys):
        if isinstance(sys,signal.dlti):
            line_shape = "hv"
        else:
            line_shape = "linear"
        return line_shape 
    
    def get_sys(self,tf):
        num = tf.num[0][0]
        den = tf.den[0][0]
        
        if tf.dt is None:
            sys = signal.lti(num, den)
        else :
            sys = signal.dlti(num,den, dt=tf.dt)
        return sys
    
    def xlim(self,range):
        self.x_range = range
    
    def ylim(self,range):
        self.y_range = range

    def show(self):
        fig = go.Figure(self.data, layout=self.get_layout())
        
        if self.x_range is not None:
            fig.update_xaxes(range=self.x_range)
        if self.y_range is not None:
            fig.update_yaxes(range=self.y_range)
        
        return fig

    def json(self):
        fig = self.show()
        return json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)



class Time_Figure(Figure):
    
    def get_layout(self):
        layout =  { "xaxis": {"title": {"text": "time (s)"}},"yaxis": {"title": {"text": "amp"}}}
        return layout
    
    def plot(self,tf,type="step",T=None,label="sys"):

        if tf.dt is not None:
            sys_class = "dlti"
        else:
            sys_class = "lti"

        sys = self.get_sys(tf)
        line_shape = self.get_line_shape(sys)
        line = dict(color=self.get_next_color())
        
        if type == "step":
            if sys_class == "lti":
                t,s = sys.step(T=T)
            else:
                t,s = sys.step(t=T)
        if type == "impulse":
            if sys_class == "lti":
                t,s = sys.impulse(T=T)
            else:
                t,s = sys.impulse(t=T)
        
        data = {"x":np.ravel(t),"y":np.ravel(s),"line": line,"name":label,"mode":"lines","line_shape":line_shape}
        self.data.append(data)


class PZmap_Figure(Figure):

    def get_layout(self):
        layout =  { "xaxis": {"title": {"text": "Real Axis"}},"yaxis": {"title": {"text": "Iamg Axis"}, "scaleanchor":"x","scaleratio":1}}
        return layout

    def plot(self,tf,label="sys"):
        line = dict(color=self.get_next_color())
    
        p = tf.pole()
        data1 =  {  "x": np.real(p),
                    "y": np.imag(p),
                    "name": label,
                    "line": line,
                    "hovertemplate": "<b>Pole<b><br><b>real</b>: %{x:.3f}<br><b>imag</b>: %{y:.3f}<br>",
                    "mode": "markers",
                    "marker": {"symbol": "x", "size": 8},
                }
    
        z = tf.zero()
        data2 = {   "x": np.real(z),
                    "y": np.imag(z),
                    "name": label,
                    "line": line,
                    "hovertemplate": "<b>Zero<b><br><b>real</b>: %{x:.3f}<br><b>imag</b>: %{y:.3f}<br>",
                    "mode": "markers",
                    "marker": {"symbol": "circle", "size": 8},
                }
        
        self.data.append(data1)
        self.data.append(data2)

class Bode_Figure(Figure):

    def __init__(self):
        self.data_mag = []
        self.data_phase = []
        self.type = None
        self.layout = None
        self.index = 0
        self.x_range = None
        self.y_range = None

    def plot(self,tf,w=None,label="sys"):
        line = dict(color=self.get_next_color())
        sys = self.get_sys(tf)
        
        mag_list, phase_list, w = bode_plot(tf, omega=w, Plot=False, omega_limits=None, omega_num=None, margins=None)
        mag = 20 * np.log10(mag_list)
        phase = phase_list * 180 / np.pi

        data_mag = {
            "x": w,
            "y": mag,
            "line": line,
            "name": label,
            "hovertemplate": "<b>w</b>: %{x:.3f} rad/s<br><b>mag</b>: %{y:.3f} dB<br><b>phase</b>: %{text:.3f} deg<br>",
            "text": phase,
            "showlegend": False,
            }
        data_phase = {
            "x": w,
            "y": phase,
            "line": line,
            "name": label,
            "hovertemplate": "<b>w</b>: %{x:.3f} rad/s<br><b>mag</b>: %{text:.3f} dB<br><b>phase</b>: %{y:.3f} deg<br>",
            "text": mag,
            "showlegend": False,
            }
            
        self.data_mag.append(data_mag)
        self.data_phase.append(data_phase)

    def show(self):
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True)
        
        for data in self.data_mag:
            fig.add_trace(data, row=1, col=1)
        for data in self.data_phase:
            fig.add_trace(data, row=2, col=1)

        if self.x_range is not None:
            fig.update_xaxes(range=self.x_range)
        if self.y_range is not None:
            fig.update_yaxes(range=self.y_range)
        
        fig.update_yaxes(title_text="Magnitude", row=1, col=1)
        fig.update_xaxes(title_text="w (rad/s)", type="log", row=1, col=1)
        fig.update_yaxes(title_text="Phase", row=2, col=1)
        fig.update_xaxes(title_text="w (rad/s)", type="log", row=2, col=1)
        return fig


class Nichols_Figure(Figure):
    
    def __init__(self):
        self.data = []
        self.type = None
        self.layout = None
        self.index = 0
        self.gmin = 1000
        self.pmin = 1000
        self.pmax = -1000
        self.x_range = None
        self.y_range = None
        self.add_critical_point()
    
    def add_critical_point(self):
        line = dict(color="#FF0000", width=1)
        data = {"x":[-180],"y":[0],"hoverinfo":"none",  "mode": "markers","marker": {"size": 3,"line":line},"showlegend": False,}
        self.data.append(data)
    
    def get_layout(self):
        layout =  { "xaxis": {"title": {"text": "Open-Loop Phase (deg)"}},"yaxis": {"title": {"text": "Open-Loop Gain (dB)"}}}
        return layout
    
    def update_min_max(self,mag,phase):
        self.gmin = min(np.min(mag),self.gmin)
        self.pmin = min(np.min(phase),self.pmin)
        self.pmax = max(np.max(phase),self.pmax)
    
    def plot(self,tf,w=None,label="sys"):
        line = dict(color=self.get_next_color())
        sys = self.get_sys(tf)

        mag_list, phase_list, w = bode_plot(tf, omega=w, Plot=False, omega_limits=None, omega_num=None, margins=None)
        mag = 20 * np.log10(mag_list)
        phase = phase_list * 180 / np.pi

        data ={
            "x": phase,
            "y": mag,
            "name": label,
            "line": line,
            "hovertemplate": "<b>w</b>: %{text:.3f} rad/s<br><b>mag</b>: %{y:.3f} dB<br><b>phase</b>: %{x:.3f} deg<br>",
            "text": w,
            "showlegend": False,
            }
        
        self.update_min_max(mag,phase)
        self.data.append(data)

    def grid(self,cm=None,cp=None,show_mag=True,show_phase=True):

        mag_list, phase_list = nicchart(self.gmin,self.pmin,self.pmax,cm=cm,cp=cp)
        line = self.get_grid_line()
        data = []
        if show_mag == True:
            for mag in mag_list:
                data ={
                    "x": mag["x"],
                    "y": mag["y"],
                    "name": mag["name"],
                    "hoverinfo": "name",
                    "line": line,
                    "showlegend": False,
                    }
                self.data.append(data)

        if show_phase == True:
            
            for phase in phase_list:
                data ={
                        "x": phase["x"],
                        "y": phase["y"],
                        "name": phase["name"],
                        "hoverinfo": "name",
                        "line": line,
                        "showlegend": False,
                        }
                self.data.append(data)

        self.data.append(data)

class Rlocus_Figure(Figure):
    
    def __init__(self):
        self.data = []
        self.type = None
        self.layout = None
        self.index = 0
        self.x_range = None
        self.y_range = None
        self.rad_max = 0
        self.sys_class = None
    
    def get_layout(self):
        layout =  { "xaxis": {"title": {"text": "Real Axis"}},"yaxis": {"title": {"text": "Imag Axis"}}}
        return layout
    
    def update_rad_max(self,poles):
        abs_poles = np.max(np.abs(np.ravel(poles)))
        if abs_poles > self.rad_max:
            self.rad_max = abs_poles
    
    def grid(self):
        if self.sys_class == "dlti":
            grid_data = drlocus_chart()
        else:
            grid_data = rlocus_chart(self.rad_max)
        
        line = self.get_grid_line()
        for grid_temp in grid_data:
            data ={
                    "x": grid_temp["x"],
                    "y": grid_temp["y"],
                    "name": grid_temp["name"],
                    "hoverinfo": "name",
                    "line": line,
                    "showlegend": False,
                    }
            self.data.append(data)
    
    
    def plot(self,tf,k_vect=np.logspace(-2,1.2,1000),label="sys"):
        
        poles = []
        
        if tf.dt is not None:
            self.sys_class = "dlti"
            dt = tf.dt
        else:
            self.sys_class = "lti"
            dt = None
        
        for k in k_vect :
            tf_cl = feedback(k*tf,1)
            sys = self.get_sys(tf_cl)
            poles.append(sys.poles)

        #prepare_data
        poles = np.array(poles)
        nb_poles = poles.shape[1]
        data = []
        
        #update rad max
        self.update_rad_max(poles)
        
        hovertemplate = "<b>K</b>: %{text:.3f}<br><b>imag</b>: %{y:.3f}<br><b>real</b>: %{x:.3f}<br>m: %{customdata[0]:.3f}<br>wn: %{customdata[1]:.3f} rad/s"

        for index in range(nb_poles):
            pole = poles[:,index]
            line = dict(color=self.get_next_color())
            x = np.real(pole)
            y = np.imag(pole)
            name = "{} p{}".format(label,index+1)
            
            #get info
            custom_data = np.zeros((len(x),2))
            for index, pole_temp in enumerate(pole):
                wn, m = pole_info(pole_temp,dt=dt)
                custom_data[index,:]= [m,wn]
            
            data = {"x":x,"y":y,"text":k_vect,"name":name,"line":line,"showlegend":False,"customdata":custom_data,"hovertemplate": hovertemplate}
            self.data.append(data)
            
            data = {"x":[x[0]],"y":[y[0]],"line":line, "mode": "markers","marker":{"symbol":"x","size":8},"showlegend":False}
            self.data.append(data)
