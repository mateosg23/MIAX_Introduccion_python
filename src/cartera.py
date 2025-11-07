from activo import Activo
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

class Cartera:
    
    """
    Incluye los datos del número de activos y activos que se quieran. Se pueden incluir acciones, índices, commodities,
    variables macroeconómicas. 
    Cada activo constituye una instancia de la clase Activo.
    """
    
    def __init__(self, fecha_inicio, fecha_fin, api = 'yahoo', intervalo = '1d', n_days=100, n_sims=100, inversion=1000):
        
        """
        Constructor de la clase Cartera
        Hay que indicar las fechas inicio y fin, la api, el intervalo, el número de activos, el número de simulaciones y
        el número de días para cada simulación de monte carlo
        """
        
        # Hay que incorporar los parámetros necesarios para cada Activo y el número de activos.
        
        try:
            self.fecha_inicio = pd.to_datetime(fecha_inicio).date()
            self.fecha_fin = pd.to_datetime(fecha_fin).date()
        except Exception as e:
            raise Exception('Las fechas deben tener el formato YYYY-MM-DD') from e
        
        if self.fecha_inicio>=self.fecha_fin:
            raise ValueError('La fecha de inicio debe ser menor que la fecha fin.')
        
        if self.fecha_fin > pd.Timestamp.today().normalize().date():
            self.fecha_fin = pd.Timestamp.today().normalize().date()
        
        self.api = api.lower()
        self.intervalo = intervalo.lower()
        
        self.cartera = dict()
        self.activos = dict()
        self.num_activos = 0
        self.n_days = n_days
        self.n_sims = n_sims
        self.inversion = inversion
        self.MC = None
        self.lista_ticker = list()
        
    def rellenar_cartera(self):
        
        """
        Pide al usuario que introduzca el número de activos y luego debe introducir el ticker asociado a los activos que
        quiera incluir en la cartera. Es requisito que el número de activos sea un número entero positivo.
        Los datos se descargan en el diccionario tras hacer la limpieza de los datos de cada activo.
        Todos estos activos se añaden a un diccionario con clave ticker y valor el dataframe
        """
        
        # Devuelve un diccionario con clave ticker y clave el dataframe desde la api
        try:
            self.num_activos = int(input('Introduce el número de activos a disponer en la cartera: '))
        except ValueError as ve:
            raise ValueError('Introduce un número entero positivo.') from ve
        
        while self.num_activos <=0:
            try:
                self.num_activos = int(input('Introduce el número positivo de activos a disponer en la cartera: '))
            except ValueError as ve:
                raise ValueError('Introduce un número entero positivo.') from ve
                
        ticker = ''
        for i in range(self.num_activos):
            ticker = input('Introduce el ticker del activo a incluir en la cartera: ').upper()
            self.lista_ticker.append(ticker)
            activo = Activo(ticker, self.fecha_inicio, self.fecha_fin, self.api, self.intervalo)
            self.cartera[ticker] = activo.limpieza()
            self.activos[ticker] = activo
        return self.cartera
    
    def rellenar_dataset(self):
        
        """
        Método que sirve para pasar los datos del formato diccionario a un dataframe conjunto. Con estos datos es con los que
        se trabajará
        """
        
        # Pasamos los datos de formato diccionario a dataframe conjunto con dos índices -> más fácil trabajar con los datos así
        df_list = []
        for ticker, df in self.cartera.items():
            df_clean = df.copy()
            if isinstance(df_clean.columns, pd.MultiIndex):
                df_clean.columns = df_clean.columns.get_level_values(1)
            # Añade una nueva columna donde incorpora el Ticker
            df_clean['Ticker'] = ticker
            # Establece a la columna Ticker como un índice (además de la fecha)
            df_clean = df_clean.set_index('Ticker', append=True)
            # Reordena los índices -> Ticker, Fecha
            df_clean = df_clean.reorder_levels(['Ticker', df_clean.index.names[0]])
            df_list.append(df_clean)
        dataset = pd.concat(df_list).sort_index()
        
        if self.api == 'avantage':
            return dataset.unstack(level = 0).dropna().stack(level=1).reorder_levels(['Ticker', 'date']).sort_index()
        else:
            return dataset.unstack(level = 0).dropna().stack(level=1).reorder_levels(['Ticker', 'Date']).sort_index()
    
    def get_data_pct_change(self):
        
        """
        Calculamos las variaciones porcentuales entre cada observación: cada día si los datos son diarios, cada semana si son mensuales, etc
        La salida es un diccionario y un dataframe con estos datos tras calcular la variación porcentual entre cada observación.
        Mantenemos la opción de tener los datos en formato dataframe y diccionario.
        En este método seleccionamos la columna de precios de cierre ajustados (si existen) y si no los de cierre.
        """
        
        # Devuelve el dataframe normalizado (y en formato diccionario)
        cartera_norm = dict()
        # Selecciona la columna Adj_close o close dependiendo de la api -> coge la penúltima columna
        df = self.rellenar_dataset().iloc[:,-2].unstack(level=0).pct_change().dropna()
        for i in range(self.num_activos):
            cartera_norm[self.lista_ticker[i]] = df.iloc[:,i]
        return df, cartera_norm
    
    def get_returns_stats(self):
        
        """
        Calculamos el vector de medias y la matriz de correlaciones de los activos presentes en la cartera
        """
        
        # Devuelve la media y matriz de covarianzas del dataframe normalizado
        df = []
        df = self.get_data_pct_change()[0]
        media = df.mean()
        cov = df.cov()
        return media, cov

    def download_data(self, url, extension):
        """
        Método que permite descargar los datos de la cartera en formato excel o csv
        """
        # Función para descargar los datos en csv o excel
        if not os.path.exists(url):
            os.makedirs(url)
        if not url.endswith('/'):
            url += '/'
        if extension.lower() == 'csv':
            self.rellenar_dataset().to_csv(os.path.join(str(url), 'data.csv'))
        elif extension.lower() == 'excel':
            self.rellenar_dataset().to_excel(os.path.join(str(url), 'data.xlsx'))
        else:
            raise ValueError('No existe un archivo que soporte la extensión introducida')
    
    def monte_carlo(self):
        
        """
        Este método realiza las simulaciones de monte carlo de forma matricial para cada simulación.
        La salida son los retornos esperados para cada simulación y día de la simulación [días, simulaciones]
        """
        
        # Pensar seriamente si lo de actualizar los pesos sirve de algo.
        # Cuando las frecuencias son diferentes a las diarias hay resultados raros
        media, cov = self.get_returns_stats()
        L = np.linalg.cholesky(cov)
        
        medias = np.full(shape=(self.n_days, self.num_activos), fill_value=media).T
        portfolio_sims = np.full(shape=(self.n_days, self.n_sims), fill_value=0)
        
        pesos = np.random.random(self.num_activos)
        pesos /= sum(pesos)
        
        for n in range(self.n_sims):
            Z = np.random.normal(size = (self.n_days, self.num_activos))
            retornos = medias + np.dot(L,Z.T)
            portfolio_sims[:,n] = np.cumprod(np.dot(pesos, retornos)+1)*self.inversion
            #portfolio_sims[:,n] = np.log(np.cumprod(np.dot(pesos, retornos)+1))*self.inversion
        self.MC = portfolio_sims
        
        return portfolio_sims
    
    def plot_monte_carlo(self, MC):
        
        """
        Gráfico que muestra el resultado de todas las simulaciones de monte carlo
        """
        
        plt.plot(MC)
        plt.xlabel('Número de dias')
        plt.ylabel('Resultado ($)')
        plt.title('Resultado de ' + str(self.n_sims) + ' simulaciones durante ' + str(self.n_days) + ' días.\nInversión inicial: '+str(self.inversion)+'$')
        plt.show()
    
    def report(self, MC):
        
        """
        Método que muestra un mensaje resumiendo los resultados de la simulación de monte carlo. Incluye:
        
        - Datos de los activos
        - Resultados finales de la simulación
        - Recomendación de inversión
        """
        
        mensaje = '--------------------------------------------------------------'
        mensaje = '# ACTIVOS DE LA CARTERA\n'
        for n in range(self.num_activos):
            mensaje += f'{self.activos[self.lista_ticker[n]].resumen()}\n'
            mensaje += '\n'

        mensaje += '# RESULTADOS DE LA SIMULACIÓN\n'
        mensaje += f'- Número de simulaciones favorables: {len(MC[-1,:][MC[-1,:]>=self.inversion])}\n'
        mensaje += f'\n- Número de simulaciones totales: {self.n_sims}\n'
        mensaje += f'\n- El número de simulaciones favorables es del {np.round(len(MC[-1,:][MC[-1,:]>=self.inversion])/self.n_sims*100,2)}%\n'
        mensaje += f'\n- Valor esperado de la mejor simulación: {MC[-1,:].max().round(2)}$\n'
        mensaje += f'\n- Valor esperado de la peor simulación: {MC[-1,:].min().round(2)}$\n'
        mensaje += f'\n- Percentil 5% de las simulaciones: {np.percentile(MC[-1,:],5).round(2)}$\n'
        mensaje += f'\n- Percentil 95% de las simulaciones: {np.percentile(MC[-1,:],95).round(2)}$\n'
        mensaje += '\n--------------------------------------------------------------'
        mensaje += f'\n- Inversión realizada {self.inversion}$\n'
        mensaje += f'\n- Valor esperado = {MC[-1,:].mean().round(2)}$'

        mensaje += '\n--------------------------------------------------------------'
        if MC[-1,:].mean() >= self.inversion:
            mensaje += '\n# RECOMENDACIÓN -> Invertir'
        else:
            mensaje += '\n# RECOMENDACIÓN -> No invertir'
        #display(Markdown(mensaje))
        mensaje += '\n--------------------------------------------------------------'
        print(mensaje)
        return mensaje
    
    def plots_report(self, MC):
        
        """
        Método que muestra gráficos estadísticos sobre las simulaciones de monte carlo:
        - Histograma con densidad de los datos
        - Intervalos de confianza del 95% de las simulaciones
        """
        
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        sns.histplot(MC[-1,:], kde=True, ax=axes[0])
        axes[0].set_xlabel('Inversión ($)')
        axes[0].set_ylabel('Número de simulaciones')
        axes[0].set_title('Histograma de la simulación de Monte Carlo')
        
        p2_5 = np.percentile(MC, 2.5, axis=1)
        p50 = np.percentile(MC, 50, axis=1)
        p97_5 = np.percentile(MC, 97.5, axis=1)
        
        axes[1].fill_between(np.arange(self.n_days), p2_5, p97_5, alpha=0.3)
        axes[1].plot(np.arange(self.n_days), p50, label="Mediana")
        axes[1].set_title(r"Intervalo de confianza de los precios finales de las simulaciones ($\alpha = 0{,}05$)")
        axes[1].set_xlabel("Días")
        axes[1].set_ylabel("Valor ($)")
        plt.tight_layout()
        plt.show()
        
