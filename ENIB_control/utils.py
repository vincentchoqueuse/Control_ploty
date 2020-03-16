import numpy as np
import scipy as sp


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
        key_cl_mags = np.array([-40.0, -20.0, -12.0, -6.0, -3.0, -1.0, -0.5, 0.0, 0.25, 0.5, 1.0, 3.0, 6.0, 12.0])
        # Extend the range of magnitudes if necessary.
        cl_mag_step = -20.0  # dB
        extended_cl_mags = np.arange(np.min(key_cl_mags),
                                     ol_mag_min + cl_mag_step, cl_mag_step)
        cl_mags = np.concatenate((extended_cl_mags, key_cl_mags))

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
        assert ((-360.0 < np.min(cl_phases)) and (np.max(cl_phases) < 0.0))
    
    # Find the M-contours
    m = m_circles(cl_mags, phase_min=np.min(cl_phases), phase_max=np.max(cl_phases))
    m_mag = 20*sp.log10(np.abs(m))
    m_phase = sp.mod(sp.degrees(sp.angle(m)), -360.0)  # Unwrap
    
    # Find the N-contours
    n = n_circles(cl_phases, mag_min=np.min(cl_mags), mag_max=np.max(cl_mags))
    n_mag = 20*sp.log10(np.abs(n))
    n_phase = sp.mod(sp.degrees(sp.angle(n)), -360.0)  # Unwrap
    
    # Plot the contours behind other plot elements.
    # The "phase offset" is used to produce copies of the chart
    phase_offset_min = 360.0*np.ceil(ol_phase_min/360.0)
    phase_offset_max = 360.0*np.ceil(ol_phase_max/360.0) + 360.0
    phase_offsets = np.arange(phase_offset_min, phase_offset_max, 360.0)

    data_m_mag = []
    data_n_mag = []
    for phase_offset in phase_offsets:
        for indice in range(m_mag.shape[1]):
            name = "{} dB".format(cl_mags[indice])
            data_m_mag.append({"x":m_phase[:,indice] + phase_offset,"y":m_mag[:,indice],"name":name})
        for indice in range(n_mag.shape[1]):
            name = "{} deg".format(cl_phases[indice])
            data_n_mag.append({"x":n_phase[:,indice] + phase_offset,"y":n_mag[:,indice],"name":name})

    return data_m_mag,data_n_mag


def closed_loop_contours(Gcl_mags, Gcl_phases):
    Gcl = Gcl_mags*sp.exp(1.j*Gcl_phases)
    return Gcl/(1.0 - Gcl)


def m_circles(mags, phase_min=-359.75, phase_max=-0.25):
    phases = sp.radians(sp.linspace(phase_min, phase_max, 2000))
    Gcl_mags, Gcl_phases = sp.meshgrid(10.0**(mags/20.0), phases)
    return closed_loop_contours(Gcl_mags, Gcl_phases)


def n_circles(phases, mag_min=-40.0, mag_max=12.0):
    mags = sp.linspace(10**(mag_min/20.0), 10**(mag_max/20.0), 2000)
    Gcl_phases, Gcl_mags = sp.meshgrid(sp.radians(phases), mags)
    return closed_loop_contours(Gcl_mags, Gcl_phases)


def zpk(tf,show=False):
    z = tf.pole
    p = tf.pole
    k = tf.dcgain
    
    if show == True:
        print("gain : {)".format(k))
        print("zeros : {)".format(z))
        print("poles : {)".format(p))
    
    return z,p,k
