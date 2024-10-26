from flask import Flask, render_template, request
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from io import BytesIO
import base64
from scipy.optimize import minimize

app = Flask(__name__)

def objetivo(x, a, b):
    x1, x2, x3 = x
    return x1**2 + x2**2 + x3**2 + 12*(x1 - a) + 12*(x1 + x2 - b)

def restriccion1(x, a):
    return x[0] - a

def restriccion2(x, a, b):
    return x[0] - a + x[1] - b

def restriccion3(x, a, b):
    return x[0] + x[1] - (a + b) + x[2] - b

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        a = float(request.form['a'])
        b = float(request.form['b'])

        restricciones = [
            {'type': 'ineq', 'fun': lambda x: restriccion1(x, a)},
            {'type': 'ineq', 'fun': lambda x: restriccion2(x, a, b)},
            {'type': 'ineq', 'fun': lambda x: restriccion3(x, a, b)},
            {'type': 'ineq', 'fun': lambda x: x[1]}, # x2 >= 0
            {'type': 'ineq', 'fun': lambda x: x[2]}  # x3 >= 0
        ]

        x0 = [a, b, b]

        resultado = minimize(objetivo, x0, args=(a, b), constraints=restricciones)
        x1_opt, x2_opt, x3_opt = resultado.x
        z_opt = resultado.fun

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        x = np.linspace(0, 100, 100)
        y = np.linspace(0, 100, 100)
        X, Y = np.meshgrid(x, y)
        Z = X**2 + Y**2 + 12*(X - a) + 12*(X + Y - b)

        ax.plot_surface(X, Y, Z, cmap='viridis')

        ax.set_xlabel('x1')
        ax.set_ylabel('x2')
        ax.set_zlabel('Z')

        # Agregar el punto óptimo
        ax.scatter(x1_opt, x2_opt, z_opt, color='r', s=300, edgecolor='k', linewidth=5)
        ax.text(x1_opt, x2_opt, z_opt, f'({x1_opt:.1f}, {x2_opt:.1f}, {z_opt:.1f})', color='r')

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()

        graphic = base64.b64encode(image_png)
        graphic = graphic.decode('utf-8')

        return render_template('index.html', graphic=graphic, x1_opt=x1_opt, x2_opt=x2_opt, x3_opt=x3_opt, z_opt=z_opt)

    return render_template('index.html', graphic=None)

if __name__ == '__main__':
    app.run(debug=True)
