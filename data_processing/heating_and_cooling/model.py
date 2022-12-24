import sympy as sp

# Create a 2D model of an Al cilinder cooling in air starting at 60 degrees celcius
# and cooling to 20 degrees celcius in 10 minutes.

# The model is based on the following assumptions:
# - The surrounding air does not heat up
# - The cilinder is a perfect cylinder
# - The cilinder only transfers heat to the air
# - The cilinder has a homogeneous temperature distribution at t0

# The model is based on the following equations:
# - Heat flux equation: Q = k * A * dT/dx
# - Heat transfer equation: dT/dt = -Q / (m * c)
# - Heat capacity equation: m * c = rho * V

# The model is based on the following constants:
k = 0.1  # W/mK
rho = 2700  # kg/m3
V = 0.01  # m3
A = 0.01  # m2
T0 = 60  # degrees celcius
Tair = 20  # degrees celcius
t = 600  # seconds

# The model is based on the following variables:
x = sp.Symbol('x')
T = sp.Function('T')(x)
t = sp.Symbol('t')

# Solve the heat flux equation
Q = k * A * sp.diff(T, x)

