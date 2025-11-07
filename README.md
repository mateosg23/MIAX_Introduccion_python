# MIAX_Introduccion_python
# Simulador de Monte Carlo de Cartera Financiera

> **Análisis y simulación de carteras con descargas automáticas de precios (Yahoo, Stooq, Alpha Vantage), generación de trayectorias vía Monte Carlo y reportes gráficos y en texto.**  

## 🧭 Tabla de contenidos
- [Características](#-características)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Configuración (APIs)](#-configuración-apis)
- [Uso](#-uso)
  - [Ejecución rápida (Automático)](#ejecución-rápida-automático)
  - [Ejecución manual](#ejecución-manual)
  - [Entradas que solicitará el programa](#entradas-que-solicitará-el-programa)
  - [Salidas](#salidas)
- [Estructura del proyecto](#-estructura-del-proyecto)
- [Notas importantes](#-notas-importantes)
- [Limitaciones y mejoras sugeridas](#-limitaciones-y-mejoras-sugeridas)
- [Roadmap / TODO](#-roadmap--todo)
- [Licencia](#-licencia)
- [Créditos](#-créditos)
- [Descargo de responsabilidad](#-descargo-de-responsabilidad)

---

## ✨ Características

- **Fuentes de datos**:
  - **Yahoo Finance** (`yfinance`)
  - **Stooq** (`pandas_datareader`)
  - **Alpha Vantage** (`alpha_vantage`) — opcional
- **Preprocesamiento**:
  - Limpieza por activo (elimina duplicados y rellena nulos por la mediana)
  - Unificación en un **DataFrame multi-índice** (`Ticker`, `Date`)
  - Cálculo de **retornos porcentuales**
- **Simulación Monte Carlo**:
  - Media y covarianza muestrales de retornos
  - **Estructura de dependencia** vía **descomposición de Cholesky**
  - Trayectorias de valor de cartera con **pesos aleatorios normalizados**
- **Visualización**:
  - **Todas las trayectorias** simuladas
  - **Histograma + KDE** del valor final
  - **Banda de confianza** (2.5%–97.5%) y mediana temporal
- **Reporte** en texto (Markdown) con:
  - Resumen por activo (min, max, media, desviación)
  - Estadísticos de resultados (mejor/peor, percentiles, % de simulaciones ≥ inversión)
  - **Recomendación** (Invertir / No invertir) en función del valor esperado
- **Exportación** de datos por activo a CSV/Excel

---

## 📦 Requisitos

Versión recomendada de Python: **3.10 – 3.12**

Fichero `requirements.txt`:

```
pandas==2.2.3
numpy==2.1.1
yfinance==0.2.43
alpha_vantage==3.0.0
pandas_datareader==0.10.0
matplotlib==3.9.0
seaborn==0.13.2
ipython==8.27.0
scipy==1.14.1
```

---

## ⚙️ Instalación

```bash
# 1) Clonar el repositorio
git clone <URL_DE_TU_REPO>
cd <NOMBRE_DEL_REPO>

# 2) Crear y activar entorno virtual
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows (PowerShell)
# .venv\Scripts\Activate.ps1

# 3) Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🔐 Configuración (APIs)

- **Yahoo Finance**: no requiere clave (se usa por defecto y es la más completa).
- **Stooq**: no requiere clave.
- **Alpha Vantage**: requiere **API key**.  
  En el código actual hay una clave embebida, pero **se recomienda** usar una **variable de entorno**:

---

## ▶️ Uso

### Ejecución rápida (Automático)

```bash
python main.py
```

El programa mostrará un banner y te preguntará si deseas usar la **versión automatizada**.  
Responde `S` y completa:

- **n_days**: número de días a simular por trayectoria
- **n_sims**: número de simulaciones
- **inversión**: capital inicial (p. ej., `10000`)

Fechas y origen de datos vienen preconfigurados en automático:
- **Fecha inicio**: `2025-01-01`
- **Fecha fin**: *hoy*
- **API**: `yahoo`
- **Intervalo**: `1d` (diario)

Luego te pedirá:
- **Número de activos** y
- **Ticker** de cada activo (p. ej. `AAPL`, `MSFT`, `SPY`)

### Ejecución manual

Responde `N` al prompt inicial y completa:

- **Fecha de inicio** (YYYY-MM-DD)  
- **Fecha de fin** (YYYY-MM-DD)  
- **API**: "yahoo", "stooq" o "avantage" (Alpha Vantage)  
- **Intervalo**: "1d", "1wk", "1mo", "3mo"  
- **n_days**, **n_sims**, **inversión**  
- **Número de activos** y sus **tickers**

### Entradas que solicitará el programa

- Fechas: comprobación de formato y que `inicio < fin`
- API e intervalo válidos (valores aceptados arriba)
- Valores enteros positivos para **n_days**, **n_sims** e **inversion**.

Luego te pedirá:
- **Número de activos** y
- **Ticker** de cada activo (p. ej. `AAPL`, `MSFT`, `SPY`)

### Salidas

1. **Gráfico de trayectorias** (todas las simulaciones).  
2. **Panel estadístico**:
   - Histograma + densidad (KDE) del **valor final**
   - Banda **[2.5%, 97.5%]** y **mediana** a lo largo del tiempo
3. **Reporte** (texto/Markdown) con:
   - Resumen por activo (min, max, media, desviación)
   - Mejor, peor, percentiles (5% y 95%), % simulaciones favorables
   - Recomendación: **Invertir** / **No invertir**

> **Exportación de datos por activo**:  
> Con `Activo.download_data(url, extension)` puedes guardar `csv` o `excel` (por activo).

---

## 🗂️ Estructura del proyecto

```
.
├── main.py               # Selector de flujo (automático/manual)
├── run_auto.py           # Flujo automatizado (fechas fijas, API Yahoo, 1d)
├── run_manual.py         # Flujo manual (todas las variables por input)
├── cartera.py            # Clase Cartera: integración, MC, plots y report
├── activo.py             # Clase Activo: descargas, limpieza, métricas
├── requirements.txt      # Dependencias del proyecto
└── README.md             # Este archivo
```

---

## ⚠️ Notas importantes

- El proyecto es **100% Python**.  
- Descargas de mercado requieren **internet**.  
- Los **tickers** deben existir en la API seleccionada.  
- Las **unidades** por defecto en textos/gráficos se expresan como `$`.  
- Para **Alpha Vantage**, limita el uso según el plan (número de llamadas por minuto/día).

---

## 🧪 Limitaciones y mejoras sugeridas

- **Prompts**:
  - `run_manual.py`: la segunda fecha solicitada dice “inicio” pero debería ser **“fin”**.
  - `run_auto.py`: los mensajes de `n_sims` e `inversion` repiten el texto de *“número de días a simular”*.
- **Selección de precios**: en `Cartera.get_data_pct_change()` se usa `iloc[:, -2]` (penúltima columna).  
  Es **frágil** si cambia el orden de columnas. Mejor seleccionar por nombre:
  - `Adj Close` si existe (Yahoo), si no `Close` (Stooq/Alpha Vantage).
- **Cholesky**: si la **covarianza** no es **definida positiva**, `np.linalg.cholesky` fallará.  
  Sugerencia: **regularización** `cov += λ * I` con `λ` pequeño (p. ej. `1e-6`).
- **Media de retornos en MC**:  
  `np.full(..., fill_value=media)` no admite arrays como `fill_value`.  
  Alternativa robusta:
  ```python
  medias = np.tile(media.values.reshape(-1, 1), (1, self.n_days))
  ```
- **Pesos**: se generan aleatoriamente 1 sola vez por simulación. Podría:
  - Permitir pesos fijos definidos por el usuario,
  - Rebalanceo periódico,
  - Restricciones (no short, límites máximos).
- **Alpha Vantage API key**: actualmente embebida en `activo.py`.  
  Recomiendo **variable de entorno** y no versionar claves.
- **Exportación**: `download_data()` guarda `data.csv` / `data.xlsx`.  
  Mejora: incluir el **ticker** en el nombre (`{ticker}_data.csv`).
- **Unidades**: se mezclan `$` y `€` en etiquetas. Unificar o parametrizar moneda.

---

## 🗺️ Roadmap / TODO

- [ ] Parámetro para **moneda** (símbolo y formato)
- [ ] Selección de columna de precio por **nombre** (no por posición)
- [ ] Manejo de **covarianza no definida positiva** (regularización)
- [ ] **Pesos configurables** (fijos / rebalanceo / límites)
- [ ] Lectura de **API keys** desde variables de entorno
- [ ] **Pruebas unitarias** y CI
- [ ] **Dockerfile** / `Makefile`
- [ ] **Diagrama de flujo** del proceso (p. ej., con FossFLOW)
- [ ] Ejemplos reproducibles con tickers de demo

---

## 📄 Licencia

**Por definir.**  
Puedes considerar **MIT** para máxima permisividad. Si lo deseas, añado el archivo `LICENSE`.

---

## 👤 Créditos

- Autor: **Santos Garcia, Mateo**
- Colaboración / feedback: bienvenidas PRs y issues.

---

## 📌 Descargo de responsabilidad

Este proyecto tiene fines **educativos y de simulación**.  
**No constituye asesoramiento financiero.** Invierte bajo tu propio criterio y responsabilidad.

