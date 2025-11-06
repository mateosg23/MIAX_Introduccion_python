import os
import pandas as pd
import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
import pandas_datareader.data as web

class Activo:  
    """
    La clase activo considera a cada instancia como un dataframe que recopila los precios de acciones, indices, commodities, etc
    """

    def __init__(self, ticker, fecha_inicio, fecha_fin, api = 'yahoo', intervalo = '1d'):
        
        """
        Constructor de la clase Activo. Se requieren las fechas de inicio y fin, el ticker asociado al activo, la api y el 
        intervalo de días entre observaciones.
        """
        
        # Aseguramos que el ticker de entrada quede siempre en mayúsculas porque lo leen así las apis
        self.ticker = ticker.upper()
        
        try:
            self.fecha_inicio = pd.to_datetime(fecha_inicio).date()
            self.fecha_fin = pd.to_datetime(fecha_fin).date()
        except Exception as e:
            raise Exception('Las fechas deben tener el formato YYYY-MM-DD') from e
        
        if self.fecha_inicio>=self.fecha_fin:
            raise ValueError('La fecha de inicio debe ser menor que la fecha fin.')
        
        if self.fecha_fin > pd.Timestamp.today().normalize().date():
            self.fecha_fin = pd.Timestamp.today().normalize().date()
        
        self.intervalo = intervalo.lower()
        self.trans_interval = {'1d': 'D', '1wk':'W', '1mo': 'ME','3mo': 'QE'}
        if self.intervalo not in self.trans_interval.keys():
            raise ValueError('Intervalo no válido. Introduce ' + str(list(self.trans_interval.keys())) + 
                             ' para datos diarios, semanales, mensuales o trimestrales.')
        
        self.api = api.lower()
        self.apis_validas = ['yahoo', 'stooq', 'avantage']
        if self.api not in self.apis_validas:
            raise ValueError('Introduce una de las apis válidas ' + str(self.apis_validas))
        
        self.data = None
        self.api_key = '0Q6NHU770VI5HXCX'
        self.mean = 0
        self.std = 0
        
    def get_data(self):
        
        """
        Método que descarga los datos desde tres APIs diferentes:
        - YAHOO
        - STOOQ
        - ALPHA VANTAGE
        
        La salida de las descargas de los datos están estandarizadas entre las distintas opciones. 
        Se pueden filtrar los datos en función de las fechas de inicio, fin e intervalo. También por la API utilizada.
        """
        
        # Descarga datos de acciones e índices con la opción de yfinance.
        # Los datos obtenidos por stooq y alpha avantage no están ajustados. Simplemente para ver que se
        # pueden obtener de diferentes fuentes pero hay que usar los da yahoo.
        
        # Para añadir varias hay que hacer uso de diccionarios y bucles -> estandarizado para todos los métodos
        # La cartera habrá que ponerla en formato diccionario y en formato dataset conjunto
        
        if self.api == 'yahoo':
            # Desde yahoo se pueden usar datos de acciones, índices, commodities y bonos
            self.data = yf.download(self.ticker, start=self.fecha_inicio, end=self.fecha_fin, interval = self.intervalo, 
                                    group_by='ticker', auto_adjust=False)
            
        elif self.api == 'stooq':
            # No recomendable para índices
            self.data = web.DataReader(str(self.ticker), self.api, self.fecha_inicio, self.fecha_fin).sort_index()
            
            if not isinstance(self.data.index, pd.DatetimeIndex):
                raise ValueError('El ticker ' + self.ticker + ' no existe en Stooq.')
            # Transformación para tener una estimación de datos semanales, mensuales y trimestrales
            if self.intervalo != '1d':
                interval = self.trans_interval[self.intervalo]
                self.data = self.data.resample(interval).agg({'Open': 'first',
                                                         'High': 'max',
                                                         'Low': 'min',
                                                         'Close': 'last',
                                                         'Volume': 'sum'})
            self.data = self.data.loc[self.fecha_inicio:self.fecha_fin]
                
        elif self.api == 'avantage':
            # Comprobar la función comentada para obtener datos en el periodo que nos interesa
            # Interesa solamente para los días porque solo toma los 100 primeros. Para el resto no hay problema.
            ts = TimeSeries(key=self.api_key, output_format='pandas')
            if self.intervalo == '1d':
                try:
                    self.data = ts.get_daily(symbol=self.ticker, outputsize='full')[0].sort_index()
                    # Parece que es de pago
                    #self.data = ts.get_daily_adjusted(symbol=self.ticker, outputsize='full')[0].sort_index()
                    #self.data = ts.get_intraday(symbol=self.ticker, interval=self.intervalo, outputsize='full', adjusted=True)
                except ValueError as ve:
                    raise ValueError('Introduce un ticker válido') from ve
            elif self.intervalo == '1wk':
                try:
                    self.data = ts.get_weekly(symbol=self.ticker)[0].sort_index()
                except ValueError as ve:
                    raise ValueError('Introduce un ticker válido') from ve
            elif self.intervalo == '1mo':
                try:
                    self.data = ts.get_monthly(symbol=self.ticker)[0].sort_index()
                except ValueError as ve:
                    raise ValueError('Introduce un ticker válido') from ve
            elif self.intervalo == '3mo':
                # Estimamos los datos trimestrales -> no se pueden obtener directamente
                try:
                    self.data = ts.get_daily(symbol=self.ticker, outputsize='full')[0].sort_index().resample('QE').agg({'1. open': 'first',
                                                         '2. high': 'max',
                                                         '3. low': 'min',
                                                         '4. close': 'last',
                                                         '5. volume': 'sum'})
                except ValueError as ve:
                    raise ValueError('Introduce un ticker válido') from ve
            
            # Hacemos que el formato de los dataframes (columnas) coincida con el de los otros casos
            rename_cols = {'1. open': 'Open','2. high': 'High','3. low': 'Low','4. close': 'Close','5. volume': 'Volume'}
            self.data = self.data.rename(columns=rename_cols)
            new_columns = pd.MultiIndex.from_product([[self.ticker], self.data.columns],names=["Ticker", "Price"])
            self.data.columns = new_columns
            self.data = self.data.loc[self.fecha_inicio:self.fecha_fin]
            
        return self.data
    
    def download_data(self, url, extension):
        
        """
        Método que permite descargar los datos de un activo en formato excel o csv
        """
        
        # Función para descargar los datos en csv o excel
        if not os.path.exists(url):
            os.makedirs(url)
        if not url.endswith('/'):
            url += '/'
        if extension.lower() == 'csv':
            self.data.to_csv(os.path.join(str(url), 'data.csv'))
        elif extension.lower() == 'excel':
            self.data.to_excel(os.path.join(str(url), 'data.xlsx'))
        else:
            raise ValueError('No existe un archivo que soporte la extensión introducida')
            
    def get_open(self):
        
        """
        Método que obtiene los datos de apertura del activo
        """
        # Función para obtener la columma de precios de apertura
        if self.api == 'yahoo':
            return self.get_data()[self.ticker].iloc[:,0]
        else:
            return self.get_data().iloc[:,0]
    
    def get_high(self):
        
        """
        Método que obtiene los datos máximos del activo
        """
        # Función para obtener la columma de precios máximos
        if self.api == 'yahoo':
            return self.get_data()[self.ticker].iloc[:,1]
        else:
            return self.get_data().iloc[:,1]
    
    def get_low(self):
        
        """
        Método que obtiene los datos mínimos del activo
        """
        # Función para obtener la columma de precios mínimos
        if self.api == 'yahoo':
            return self.get_data()[self.ticker].iloc[:,2]
        else:
            return self.get_data().iloc[:,2]
    
    def get_close(self):
        
        """
        Método que obtiene los datos de cierre del activo
        """
        # Función para obtener la columma de precios de cierre
        if self.api == 'yahoo':
            return self.get_data()[self.ticker].iloc[:,3]
        else:
            return self.get_data().iloc[:,3]
    
    def get_adj_close(self):
        
        """
        Método que obtiene los datos de cierre ajustados del activo
        """
        # Función para obtener la columma de precios de cierre ajustados
        if self.api == 'yahoo':
            return self.get_data()[self.ticker].iloc[:,4]
        else:
            raise ValueError('Las APIs stooq y alpha vantage no guardan los precios ajustados. Prueba con la API yfinance.')
        
    def get_volume(self):
        
        """
        Método que obtiene los datos del número de acciones en circulación del activo
        """
        # Función para obtener la columma de volumen de acciones en circulación
        if self.api == 'yahoo':
            return self.get_data()[self.ticker].iloc[:,-1]
        else:
            return self.get_data().iloc[:,-1]
    
    def get_min(self):
        
        """
        Método que obtiene el precio mínimo del periodo del activo
        """
        # Función para obtener el valor mínimo de cotización del periodo seleccionado
        return self.get_data().min().min()
    
    def get_max(self):
        """
        Método que obtiene el precio máximo del periodo del activo
        """
        # Función para obtener el valor máximo de cotización del periodo seleccionado
        return self.get_data().iloc[:,:-1].max().max()
    
    def get_mean(self, indicador):
        """
        Método que obtiene el precio medio del periodo del activo para la variable que se indique
        """
        # Función para obtener la nedia de cada variable
        if indicador.lower() == 'open':
            return self.get_open().mean()
        elif indicador.lower() == 'high':
            return self.get_high().mean()
        elif indicador.lower() == 'low':
            return self.get_low().mean()
        elif indicador.lower() == 'close':
            return self.get_close().mean()
        elif indicador.lower() == 'adj_close':
            return self.get_adj_close().mean()
        elif indicador.lower() == 'volume':
            return self.get_volume().mean()
    
    def get_std(self, indicador):
        """
        Método que obtiene el desviación típica del precio del activo durante el periodo para la variable que se indique
        """
        # Función para obtener la desviación típica de cada variable
        if indicador.lower() == 'open':
            return self.get_open().std()
        elif indicador.lower() == 'high':
            return self.get_high().std()
        elif indicador.lower() == 'low':
            return self.get_low().std()
        elif indicador.lower() == 'close':
            return self.get_close().std()
        elif indicador.lower() == 'adj_close':
            return self.get_adj_close().std()
        elif indicador.lower() == 'volume':
            return self.get_volume().std()
    
    def get_stats(self, ind = 'adj_close'):
        """
        Método que obtiene la media y desviación típica para el indicador que se indique
        """
        if ind.lower() in ['open', 'high', 'low', 'close', 'adj_close']:
            self.mean = self.get_mean(ind)
            self.std = self.get_std(ind)
        else:
            raise ValueError('Introduce una columna para calcular las métricas: Open, High, Low, Close o Adj Close')
        return self.mean, self.std
    
    def resumen(self):
        """
        Método que muestra el resumen de la información del activo
        """
        # Solo existe la columnna Adj Close en yfinance, por eso la condición es tan específica.
        # Tomamos precios de cierre ajustados para datos de yahoo y datos de cierre para el resto.
        texto = ''
        ind = ''
        if 'Adj Close' in self.get_data().columns.get_level_values(-1):
            ind = 'adj_close'
        else:
            ind = 'close'
        texto += f'## Resumen de los activos de **{self.ticker}** en el periodo **{self.fecha_inicio}**: **{self.fecha_fin}**:\n'
        texto += f'- Precio mínimo: {self.get_min().round(2)}$\n\n'
        texto += f'- Precio máximo: {self.get_max().round(2)}$\n\n'
        texto += f'- Precio medio del periodo: {self.get_mean(ind).round(2)}$\n\n'
        texto += f'- Desviación típica de precios del periodo: {self.get_std(ind).round(2)}$\n\n'
        return texto
    
    def limpieza(self):
        """
        Método que realiza el preprocesamiento de los datos:
        
        - Elimina las filas duplicadas
        - Reemplaza los valores nulos por la mediana
        """
        # Eliminamos índices duplicados
        self.data = self.get_data().drop_duplicates()
        # Rellenamos valores nulos por la mediana
        return self.data.fillna(self.data.median())
    
    def info(self):
        """
        Método que devuelve el tipo de activo de la instancia procesada. Acciones, índices, commodities, etc
        """
        # Devuelve el tipo de activo del dataframe según el Ticker
        return yf.Ticker(self.ticker).info['quoteType']
    
    def get_returns(self):
        """
        Método que calcula la variación porcentual de los datos
        """
        # Calcula la variación porcentual de cada activo tomando los valores de cierre ajustados (si existen) sino los de cierre
        # No cogemos el valor de la primera fecha porque es nula
        return self.get_data().pct_change().iloc[1:]
    
    def diff(self):
        """
        Método que calcula las primeras diferencias de los datos
        """
        return self.get_data().diff().iloc[1:]