# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 13:40:38 2022

@author: baskl
"""
import numpy as np
import matplotlib.pyplot as plt

Vbin = 0.26 * 0.18 * 0.14  #  m^3 
Vbout = 0.3 * 0.22 * 0.18  # m^3
Vb = Vbout - Vbin
Ab = 0.26 * 0.18
nc = 6  # -
Vc = 0.03**2 * np.pi * 0.125 * nc  # m^3
Isun = 1165.2  # J/s*m^3
Ishade = 482.08  # J/s*m^3

Db = 1300  # J/(kg * m^3)
Dw = 4186  # J(kg * m^3)
rhow = 1000  # kg / m^3
rhob = 4186 # kg / m^3

Et = lambda A, I, t: A * I * t  # J
Dtot = lambda Vb, Db, rhob, Vc, Dw, rhow: (Vb * Db * rhob) + (Vc * Dw * rhow)

Tt = lambda Et, Dtot: Et / Dtot

D = Dtot(Vb, Db, rhob, Vc, Dw, rhow)
Tt_sun = Tt(Et(Ab, Isun, 24*60**2), D)
Tt_shade = Tt(Et(Ab, Ishade, 24*60**2), D)
dTt = Tt_sun - Tt_shade 
print(dTt)