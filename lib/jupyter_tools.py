from ipywidgets import FloatSlider,FloatText, interact,Dropdown
from lib import figure
from control import tf

class Nichols_Interact():
    
    def __init__(self,sys):
        self.sys = sys
        self.grid_options = None
        self.init_plot()
        self.xlim=[-250,0]
        self.ylim=[-50,40]
        self.w = None
    
    def init_plot(self):
        self.controler_selector = Dropdown(options =['None','P','PI'])
        self.K_widget = FloatText(value=1,description='P:',disabled=False)
        self.Ti_widget = FloatText(value=1,description='Ti:')
    
    def get_controller(self):
        C = 1
        K = self.K_widget.value
        Ti = self.Ti_widget.value
        Te = self.sys.dt
        
        if self.controler_selector.value == "P":
            C = K
        if self.controler_selector.value == "PI":
            if Te is not None:
                C=K+K*tf([Te/Ti,0],[1,-1],Te)
            else:
                C=tf([K*Ti,K],[Ti,0])
        return C
    
    def open_loop_sys(self):
        C = self.get_controller()
        return C*self.sys
    
    def grid(self,**arg):
        self.grid_options=arg
    
    def set_xlim(self,xlim):
        self.xlim = xlim
    
    def set_ylim(self,ylim):
        self.ylim = ylim
    
    def update(self,controler,K,Ti):
        
        if self.controler_selector.value == "None":
            self.K_widget.disabled = True
            self.Ti_widget.disabled = True
        if self.controler_selector.value == "P":
            self.K_widget.disabled  = False
            self.Ti_widget.disabled = True
        if self.controler_selector.value == "PI":
            self.K_widget.disabled  = False
            self.Ti_widget.disabled  = False
        
        self.fig = figure("nichols")
        if self.grid_options is not None:
            self.fig.grid(**self.grid_options)
        self.fig.plot(self.open_loop_sys(),w=self.w)
        self.fig.x_range = self.xlim
        self.fig.y_range = self.ylim
        return self.fig.show()
    
    def show(self):
        interact(self.update,controler=self.controler_selector,K=self.K_widget,Ti=self.Ti_widget)
