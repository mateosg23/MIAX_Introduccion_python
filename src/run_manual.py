from cartera import Cartera
import pandas as pd
from IPython.display import Markdown, display

def run():
    """
    Este método realiza todo el proceso. 
    
    Debe pedir las variables necesarias al usuario para que funciones el programa:
    - Fecha de inicio
    - Fecha fin
    - API
    - Intervalo
    - Número de días a simular en cada simulación
    - Número de simulaciones
    - Cantidad a invertir
    """
    # La comprobación de fecha_inicio<fecha_fin se hace en la clase
    try: 
        fecha_inicio = pd.to_datetime(input('Introduce la fecha de inicio (YYYY-MM-DD): ')).date()
        fecha_fin = pd.to_datetime(input('Introduce la fecha fin (YYYY-MM-DD): ')).date()
    except ValueError as ve:
        raise ValueError('Introduce un formato correcto de fechas (YYYY-MM-DD)') from ve
    
    api = input('Introduce una API ("yahoo", "stooq", "avantage") desde la que se obtendrán los datos: ')
    intervalo = input('Introduce un intervalo válido: "1d", "1wk", "1mo", "3mo": ')
    
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
        n_sims = int(input('Introduce el número de simulaciones: '))
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
    cartera = Cartera(fecha_inicio, fecha_fin, api, intervalo, n_days, n_sims, inversion)
    
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
