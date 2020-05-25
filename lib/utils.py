import numpy as np
import scipy as sp
from scipy.signal.ltisys import _default_response_times
import control as ctl


def get_T_max(tf_list,T=None,N=100):
    """ Get Time vector """
    if T is None:
        T_max = 100000
        for tf in tf_list:
            
            if ctl.isctime(tf):
                ss = ctl.tf2ss(tf)
                T_temp = _default_response_times(ss.A, N)
                t_max_temp = T_temp[-1]
            else:
                t_max_temp = N*tf.dt

            if t_max_temp < T_max :
                T_max = t_max_temp
    else:
        T_max = T[-1]
    return T_max


def nichols_grid(cl_mags=None, cl_phases=None):
    """Nichols chart grid
        Parameters
        ----------
        cl_mags : array-like (dB), optional
        Array of closed-loop magnitudes defining the iso-gain lines on a
        custom Nichols chart.
        cl_phases : array-like (degrees), optional
        Array of closed-loop phases defining the iso-phase lines on a custom
        Nichols chart. Must be in the range -360 < cl_phases < 0
        Returns
        -------
        None
        """
    # Default chart size
    ol_phase_min = -359.99
    ol_phase_max = 0.0
    ol_mag_min = -40.0
    ol_mag_max = default_ol_mag_max = 50.0

    # M-circle magnitudes.
    if cl_mags is None:
        # Default chart magnitudes
        key_cl_mags = np.array(
            [
                -40.0,
                -20.0,
                -12.0,
                -6.0,
                -3.0,
                -1.0,
                -0.5,
                0.0,
                0.25,
                0.5,
                1.0,
                3.0,
                6.0,
                12.0,
            ]
        )
        # Extend the range of magnitudes if necessary.
        cl_mag_step = -20.0  # dB
        extended_cl_mags = np.arange(
            np.min(key_cl_mags), ol_mag_min + cl_mag_step, cl_mag_step
        )
        cl_mags = np.concatenate((extended_cl_mags, key_cl_mags))
    else:
        cl_mags = np.array(cl_mags)

    # N-circle phases (should be in the range -360 to 0)
    if cl_phases is None:
        # Choose a reasonable set of default phases
        key_cl_phases = np.array([-0.25, -45.0, -90.0, -180.0, -270.0, -325.0, -359.75])
        if np.abs(ol_phase_max - ol_phase_min) < 90.0:
            other_cl_phases = np.arange(-10.0, -360.0, -10.0)
        else:
            other_cl_phases = np.arange(-10.0, -360.0, -20.0)
        cl_phases = np.concatenate((key_cl_phases, other_cl_phases))
    else:
        cl_phases = np.array(cl_phases)
        assert (-360.0 < np.min(cl_phases)) and (np.max(cl_phases) < 0.0)

    # Find the M-contours
    m = m_circles(cl_mags, phase_min=np.min(cl_phases), phase_max=np.max(cl_phases))
    m_mag = 20 * sp.log10(np.abs(m))
    m_phase = sp.mod(sp.degrees(sp.angle(m)), -360.0)  # Unwrap

    # Find the N-contours
    n = n_circles(cl_phases, mag_min=np.min(cl_mags), mag_max=np.max(cl_mags))
    n_mag = 20 * sp.log10(np.abs(n))
    n_phase = sp.mod(sp.degrees(sp.angle(n)), -360.0)  # Unwrap

    # Plot the contours behind other plot elements.
    # The "phase offset" is used to produce copies of the chart
    phase_offset_min = 360.0 * np.ceil(ol_phase_min / 360.0)
    phase_offset_max = 360.0 * np.ceil(ol_phase_max / 360.0) + 360.0
    phase_offsets = np.arange(phase_offset_min, phase_offset_max, 360.0)

    data_m_mag = []
    data_n_mag = []
    for phase_offset in phase_offsets:
        for indice in range(m_mag.shape[1]):
            name = "{} dB".format(cl_mags[indice])
            data_m_mag.append(
                {
                    "x": m_phase[:, indice] + phase_offset,
                    "y": m_mag[:, indice],
                    "name": name,
                }
            )
        for indice in range(n_mag.shape[1]):
            name = "{} deg".format(cl_phases[indice])
            data_n_mag.append(
                {
                    "x": n_phase[:, indice] + phase_offset,
                    "y": n_mag[:, indice],
                    "name": name,
                }
            )

    return data_m_mag, data_n_mag


def closed_loop_contours(Gcl_mags, Gcl_phases):
    Gcl = Gcl_mags * sp.exp(1.0j * Gcl_phases)
    return Gcl / (1.0 - Gcl)


def m_circles(mags, phase_min=-359.75, phase_max=-0.25):
    phases = sp.radians(sp.linspace(phase_min, phase_max, 2000))
    Gcl_mags, Gcl_phases = sp.meshgrid(10.0 ** (mags / 20.0), phases)
    return closed_loop_contours(Gcl_mags, Gcl_phases)


def n_circles(phases, mag_min=-40.0, mag_max=12.0):
    mags = sp.linspace(10 ** (mag_min / 20.0), 10 ** (mag_max / 20.0), 2000)
    Gcl_phases, Gcl_mags = sp.meshgrid(sp.radians(phases), mags)
    return closed_loop_contours(Gcl_mags, Gcl_phases)


# ROOT LOCUS (comes from the python control lib)

def _default_zetas(xlim, ylim):
    """Return default list of dumps coefficients"""
    sep1 = -xlim[0]/4
    ang1 = [np.arctan((sep1*i)/ylim[1]) for i in np.arange(1, 4, 1)]
    sep2 = ylim[1] / 3
    ang2 = [np.arctan(-xlim[0]/(ylim[1]-sep2*i)) for i in np.arange(1, 3, 1)]
    
    angules = np.concatenate((ang1, ang2))
    angules = np.insert(angules, len(angules), np.pi/2)
    zeta = np.sin(angules)
    return zeta.tolist()


def _default_wn(xloc, ylim):
    """Return default wn for root locus plot"""
    
    wn = xloc
    sep = xloc[1]-xloc[0]
    while np.abs(wn[0]) < ylim[1]:
        wn = np.insert(wn, 0, wn[0]-sep)
    
    while len(wn) > 7:
        wn = wn[0:-1:2]
    
    return wn


def rlocus_grid(xlim,ylim,zeta=None, wn=None):
    
    m_lines = []
    wn_lines = []
    
    return m_lines,wn_lines
