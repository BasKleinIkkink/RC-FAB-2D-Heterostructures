# -*- coding: utf-8 -*-
"""
Created on Thu Apr  8 14:42:15 2021.

@author: Nynra
"""
import numpy as np
import matplotlib.pyplot as plt
import copy
from typing import Union, Tuple, List
from numpy.typing import ArrayLike
from scipy import signal as sig
from scipy import fft as fft
from typeguard import typechecked


# @typechecked
# def set_aesthetics(theme : str='whitegrid', use_tex : bool=True) -> ...:
#     """
#     Set the graph aestetics to fancy.

#     Parameters
#     ----------
#     theme : str, optional
#         Theme that is set for seaborn. The default is 'whitegrid'.
#     use_tex : bool, optional
#         Boolean indicating if the system latex should be
#         used (True) or the matplotlib version (False). The default is True.
#     """
#     # Set the general graph parameters
#     # Set comma for decimals
#     locale.setlocale(locale.LC_NUMERIC, 'de_DE.UTF-8')
#     plt.rcParams['axes.formatter.use_locale'] = True
#     sns.set(rc={'text.usetex': use_tex})  # Turn on the LaTeX interpreter
#     sns.set_style(theme)  # Set the graph grid to white


@typechecked
def quick_plot_fft(t : ArrayLike, f : ArrayLike, ffilt : ArrayLike, 
                    L : ArrayLike, freq : ArrayLike, PSD : ArrayLike, 
                    PSDclean : ArrayLike, save_fig : bool=False,
                   filename : str='quick_plot.png'):
    """
    Make an overview plot of the data.

    Parameters
    ----------
    t : np.array
        1D numpy array containing the timestamp data in float.
    f : np.array
        1D numpy array containing the original data.
    ffilt : np.array
        1D numpy array containing the filtered data.
    L : np.array
        1D numpy array containing the real frequencies of the fft.
    freq : np.array
        1D numpy array containing the frequencies of the fft.
    PSD : np.array
        1D numpy array containing the original amplitude spectrum.
    PSDclean : np.array
        1D numpy array containing the filtered amplitude spectrum.
    save_fig : bool, optional
        True the figure will be saved with the given name, False not. 
        The default is False.
    filename : str, optional
        Name of the file if save_fig == True. The default is 'quick_plot.png'.
    """
    # Plot some shit
    plt.rcParams['figure.figsize'] = [16, 12]
    plt.rcParams.update({'font.size': 18})
    fig, axs = plt.subplots(3, 1)

    # Plot all the data
    plt.sca(axs[0])
    plt.plot(t, f, color='c', lw=1.5, label='$Noisy$')
    plt.plot(t, ffilt, color='k', lw=2, label='$Filtered$')
    plt.xlabel('$Time\; \mathrm{(s)}$')
    plt.ylabel('$Signal\; \mathrm{(?)}$')
    plt.xlim(t[0], t[-1])
    plt.grid(True)
    plt.legend(loc='upper right')

    # Plot the filtered data
    plt.sca(axs[1])
    plt.plot(t, ffilt, color='k', lw=2, label='$Filtered$')
    plt.xlabel('$Time\; \mathrm{(s)}$')
    plt.ylabel('$Signal\; \mathrm{(?)}$')
    plt.xlim(t[0], t[-1])
    plt.grid(True)
    plt.legend(loc='upper right')

    # Plot the amplitude spectrum
    plt.sca(axs[2])
    plt.plot(freq[L], PSD[L], color='c', lw=2, label='$Noisy$')
    plt.plot(freq[L], PSDclean[L], color='k', lw=1.5, label='$Filtered$')
    plt.xlim(freq[L[0]], freq[L[-1]])
    plt.xlabel('$Frequency\; \mathrm{(Hz)}$')
    plt.ylabel('$Amplitude\; \mathrm{(-)}$')
    plt.grid(True)
    plt.legend(loc='upper right')
    plt.tight_layout()

    if save_fig:
        plt.savefig(filename, dpi=1000)
    else:
        plt.show()


@typechecked
def fft_filter(data : ArrayLike, samplerate : Union[int, float], 
               PSD_cutoff : Union[float, int, None]=None, f_high_cutoff=None,
               f_low_cutoff : Union[float, int, None]=None, 
               f_cutoff_bands : List=[], apodization=False) -> Tuple:
    """
    Use an FFT filter to filter out noise.

    The filter supports two modes, Power Spectrum Density cutoff (PSD) and
    frequency filtering (bands, max and min f)

    Parameters
    ----------
    col : 1D np.array 
        Array containing the data that should be filtered.
    samplerate : int, float
        The used samplerate in Hz.
    PSD_cutoff : int, float, optional
        The amplitude at which a frequency should be filtered out. The default
        is None.
    f_cutoff_bands : [(int, int)], optional
        List containing the frequency bands that should be filtered out.
        The default is None.
    f_low_cutoff : int, optional
        Frequency below which everything will be filtered out. The default
        is None.
    f_high_cutoff : int, optional
        Frequency above which everything will be filtered out. The default
        is None.
    f_cutoff_bands : [(int, int)], optional
        List containing the frequency bands that should be filtered out.
        The default is None.
    apodization : bool, optional
        If True the data will be apodized before filtering. The default is False.
        The data is apodized using the Welch method with a Hamming window.

    Returns
    -------
    ffilt : np.array
        Array containing the filtered data.
    L : np.array
        Array containing the real frequencies of the fft.
    freq : np.array
        Array containing the frequencies of the fft.
    PSD : np.array
        1D np.array containing the original amplitude spectrum.
    PSDclean : np.array
        1D np.array containing the filtered amplitude spectrum.
    """
    n = len(data)
    dt = 1 / samplerate
    t = np.arange(0, n * dt, dt)  # Time vector
    
    # Compute the FFT
    fhat = fft.rfft(data)
    freq = fft.fftfreq(n, dt)
    
    # Compute the PSD
    if not apodization:
        # Compute power density spectrum
        PSD = fhat * np.conj(fhat) / n

        # Only keep the real part of the PSD
        PSD = PSD.real
        PSDclean = copy.deepcopy(PSD)
        L = np.arange(1, np.floor(n / 2), dtype='int')  # Only plot the real part
    else:
        L, PSD = sig.welch(data, samplerate, scaling='density', 
                             return_onesided=True, detrend='constant', axis=-1)
        PSDclean = copy.deepcopy(PSD)

    # Use PSD to filter out noise
    if not(type(PSD_cutoff) is type(None)):
        indices = PSD > PSD_cutoff  # Find all the freqs with large power
        PSDclean = PSD * indices  # Zero out all the options
        fhat = indices * fhat  # Zero out the small fourier coefficients

    # Apply the frequency and band filters
    if not isinstance(f_low_cutoff, type(None)):
        if f_low_cutoff < 0:
            raise ValueError('f_low_cutoff must be positive')
        elif f_low_cutoff > samplerate / 2:
            raise ValueError('f_low_cutoff must be smaller than half the samplerate')
        # Calculate the index of the cutoff frequency
        f_low_cutoff_index = np.argmin(np.abs(freq - f_low_cutoff))
        fhat[:f_low_cutoff_index] = 0
        PSDclean[:f_low_cutoff_index] = 0
    if not isinstance(f_high_cutoff, type(None)):
        if f_high_cutoff < 0:
            raise ValueError('f_high_cutoff must be positive')
        elif f_high_cutoff > samplerate / 2:
            raise ValueError('f_high_cutoff must be smaller than half the samplerate')
        # Calculate the index of the cutoff frequency
        f_high_cutoff_index = np.argmin(np.abs(freq - f_high_cutoff))
        fhat[f_high_cutoff_index:] = 0
        PSDclean[f_high_cutoff_index:] = 0
    for band in f_cutoff_bands:
        if band[0] < 0 or band[1] < 0:
            raise ValueError('f_cutoff_bands must be positive')
        elif band[0] > samplerate / 2 or band[1] > samplerate / 2:
            raise ValueError('f_cutoff_bands max must be smaller than half the samplerate')
        # Calculate the index of the cutoff frequency
        f_low_cutoff_index = np.argmin(np.abs(freq - band[0]))
        f_high_cutoff_index = np.argmin(np.abs(freq - band[1]))
        fhat[f_low_cutoff_index:f_high_cutoff_index] = 0
        PSDclean[f_low_cutoff_index:f_high_cutoff_index] = 0

    ffilt = fft.ifft(fhat)  # Inverse FFT filtered time signal

    return ffilt, L, freq, PSD, PSDclean, t


@typechecked
def quick_process(samplerate : Union[int, float], 
                  data : ArrayLike,
                  PSD_cutoff : Union[float, int, None]=None, 
                  f_high_cutoff : Union[float, int, None]=None, 
                  f_low_cutoff : Union[float, int, None]=None,
                  f_cutoff_bands : List=[], 
                  apodization : bool=False,
                  fancy_pants : bool=False):
    """
    Quickly filter and plot some data.

    .. note:: 
        This method is a combination of `func`fft_filter and 
        `func`quick_plot_fft . 
    
    Parameters:
    -----------
    samplerate : int, float
        The used samplerate in Hz.
    data : numpy 1D array
        1 D array containing the data to be processed
    PSD_cutoff : int, optional
        The amplitude at which a frequency should be filtered out.
        The default is None.
    f_cutoff_bands : tuple, optional
        List containing the frequency bands that should be filtered out.
        The default is [].
    f_low_cutoff : int, optional
        Frequency below which everything will be filtered out.
        The default is None.
    f_high_cutoff : int, optional
        Frequency above which everything will be filtered out.
        The default is None.
    apodization : bool, optional
        If True, the data will be apodized using a welch window.
        The default is False.
    fancy_pants : bool, optional
        If True, the plot will be made using the set_aesthetics function.
        The default is False.

    Returns:
    --------
    ffilt : np.array
        Array containing the filtered data.
    L : np.array
        Array containing the real frequencies of the fft.
    freq : np.array
        Array containing the frequencies of the fft.
    PSD : np.array
        1D np.array containing the original amplitude spectrum.
    PSDclean : np.array
        1D np.array containing the filtered amplitude spectrum.
    """
    # if fancy_pants:
    #     set_aesthetics()
    fdata, L, freq, PSD, PSDclean, t = fft_filter(data=data, samplerate=samplerate,
                                               PSD_cutoff=PSD_cutoff, 
                                               f_high_cutoff=f_high_cutoff,
                                               f_low_cutoff=f_low_cutoff, 
                                               f_cutoff_bands=f_cutoff_bands,
                                               apodization=apodization)
    quick_plot_fft(t, data, fdata, L, freq, PSD, PSDclean)

    return fdata, L, freq, PSD, PSDclean

