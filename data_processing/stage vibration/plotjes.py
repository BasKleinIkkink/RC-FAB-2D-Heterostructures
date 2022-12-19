# The code uses the 1 DOF equation from the paper without the air dampener.
# Fy = k(x(t) + y(t))
import sympy as sp
sp.init_printing()

m, k, t = sp.symbols('m k t', real=True)
s = sp.symbols('s')
y = sp.Function('y')
x = sp.Function('x')

fy = sp.exp(m * sp.diff(y(t), t, t) - k * (x(t) - y(t)))
Fy = sp.laplace_transform(fy, t, s, noconds=True)
Fy.solve()
print(Fy)
