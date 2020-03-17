# ENIB_control : Python Control with Plotly

## Introduction

The goal of this project is to develop an alternative to the Matlab Control System Toolbox with python. Python is a powerful alternative to Matlab for numerical computing. Several libraries such as Numpy or Scipy offer functionnalities similar to Matlab.

However, for control engineering application, most of the functionalities of the Matlab Control Toolbox (Nichols plot, feedback systems, ...) are currently not supported with Python standard librairies. The python control library (https://python-control.readthedocs.io/en/0.8.3/) has been developed for this purpose but the graphic backend, based on Matplotlib, does not support the same level of interaction as Matlab.

In this project, we propose to provide an equivalent to the python control librairy with the following functionalities

* Matlab Control toolbox similar api (https://fr.mathworks.com/products/control.html)
* Jupyter  + plotly based graphic backend (https://plot.ly/python/)

## Requirements

* python-control (`pip install control`)
* plotly (`pip install plotly==4.5.4`)

## Getting Started

Start and launch the file `test.ipynb` with jupyter notebook.
