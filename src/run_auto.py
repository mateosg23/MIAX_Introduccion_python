from cartera import Cartera
from datetime import date
from IPython.display import Markdown, display

def run_auto():
    """
    Este método realiza todo el proceso pero con parámetros fijos. El usuario solo debe insertar n_days, n_sims e inversión 
    
    Debe pedir las variables necesarias al usuario para que funciones el programa:
    - Fecha de inicio = 01/01/2025
    - Fecha fin = Día actual
    - API = Yahoo
    - Intervalo = 1d -> Diaria
    - Número de días a simular en cada simulación: Decide el usuario
    - Número de simulaciones: Decide el usuario
    - Cantidad a invertir: Decide el usuario
    """
    
    try:
        n_days = int(input('Introduce el número de días a simular: '))
    except ValueError as ve:
        raise ValueError('Introduce un número entero positivo') from ve
    
    while n_days < 1:
        try:
            n_days = int(input('El número de días debe ser un número entero mayor que cero: '))
        except ValueError as ve:
            raise ValueError('El número de días de cada simulación debe ser un número entero mayor que cero.') from ve
    
    try:
        n_sims = int(input('Introduce el número simulaciones: '))
    except ValueError as ve:
        raise ValueError('Introduce un número entero positivo') from ve

    while n_sims < 1:
        try:
            n_sims = int(input('El número de simulaciones debe ser un número entero mayor que cero: '))
        except ValueError as ve:
            raise ValueError('El número de simulaciones de cada simulación debe ser un número entero mayor que cero.') from ve
    
    try:
        inversion = int(input('Introduce la cantidad a invertir: '))
    except ValueError as ve:
        raise ValueError('Introduce una cantidad para invertir mayor que cero') from ve

    while inversion <= 0:
        try:
            inversion = int(input('La cantidad a invertir ($) debe ser mayor que cero: '))
        except ValueError as ve:
            raise ValueError('La cantidad a invertir ($) debe ser mayor que cero.') from ve
    
    # Inicializamos la cartera
    cartera = Cartera('2025-01-01', date.today(), n_days = n_days, n_sims = n_sims, inversion = inversion)
    
    # Hacemos que los datos de los activos se unifiquen en un dataframe único
    cartera.rellenar_cartera()
    
    # Llamamos al método Monte Carlo para hacer las simulaciones
    MC = cartera.monte_carlo()
    
    # Mostramos el resultado de las simulaciones en un gráfico
    input('Presiona intro para ver el resultado de las simulaciones.')
    cartera.plot_monte_carlo(MC)

    # Mostramos los resultados estadísticos de la simulación
    input('Presiona intro para ver el resultado de las distribuciones de las simulaciones.')
    cartera.plots_report(MC)
    
    # Mostramos el resumen de las simulaciones
    input('Presiona intro para ver las conclusiones y recomendaciones tras las simulaciones.')
    msj = cartera.report(MC)
    display(Markdown(msj))
