import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import date, timedelta
import matplotlib.dates as mdates

# --- 1. CONFIGURACIÓN INICIAL ---
TICKER_EMPRESA = "005930.KS"  # Ticker de Samsung Electronics
DIAS_ATRAS = 3 * 365         # Aproximadamente 3 años
NOMBRE_ARCHIVO_CSV = "precios_samsung.csv"

print(f"--- Análisis Financiero para {TICKER_EMPRESA} ---")

# --- 2. OBTENER TIPOS DE CAMBIO ---
print("\n[Paso 1/9] Obteniendo tipos de cambio...")
try:
    # Obtener tipo de cambio USD/KRW y USD/MXN
    usd_krw = yf.download("USDKRW=X", period="1d", progress=False)['Close'].iloc[0]
    usd_mxn = yf.download("USDMXN=X", period="1d", progress=False)['Close'].iloc[0]
    
    print(f"Tipo de cambio USD/KRW: {usd_krw:.2f}")
    print(f"Tipo de cambio USD/MXN: {usd_mxn:.2f}")
    print(f"Tipo de cambio KRW/MXN: {(usd_mxn/usd_krw)*100:.4f} (pesos por 100 wones)")
    
except Exception as e:
    print(f"Error al obtener tipos de cambio: {e}")
    print("Usando tipos de cambio aproximados...")
    usd_krw = 1300  # Aproximado
    usd_mxn = 18.0  # Aproximado

# Función para convertir wones a pesos mexicanos
def won_a_mxn(won):
    return (won / usd_krw) * usd_mxn

# --- 3. DESCARGA DE DATOS ---
print("\n[Paso 2/9] Descargando datos históricos...")
try:
    end_date = date.today()
    start_date = end_date - timedelta(days=DIAS_ATRAS)
    
    # Descargar datos con progress=False para evitar problemas
    datos_empresa = yf.download(TICKER_EMPRESA, start=start_date, end=end_date, 
                               auto_adjust=False, progress=False)

    if datos_empresa.empty:
        raise ValueError("No se encontraron datos para el ticker especificado en el rango de fechas.")

    # Guardar los datos en un archivo CSV
    datos_empresa.to_csv(NOMBRE_ARCHIVO_CSV)
    print(f"Datos descargados y guardados en '{NOMBRE_ARCHIVO_CSV}'")

except Exception as e:
    print(f"ERROR al descargar los datos: {e}")
    print("Intentando cargar datos desde archivo existente...")
    
    try:
        datos_empresa = pd.read_csv(NOMBRE_ARCHIVO_CSV, index_col=0, parse_dates=True)
        print(f"Datos cargados desde '{NOMBRE_ARCHIVO_CSV}'")
    except:
        print("No se pudo cargar el archivo. Verifica la conexión a internet.")
        exit()

# Nos quedamos solo con el precio de cierre para el análisis principal
precios_cierre = datos_empresa['Close'].dropna()

# Si tenemos un DataFrame con MultiIndex, convertirlo a Series simple
if isinstance(precios_cierre, pd.DataFrame):
    precios_cierre = precios_cierre.squeeze()  # Convierte DataFrame de 1 columna a Series

# Verificar si tenemos un MultiIndex y convertirlo a índice simple
if isinstance(precios_cierre.index, pd.MultiIndex):
    # Convertir MultiIndex a índice simple (solo fechas)
    precios_cierre.index = precios_cierre.index.get_level_values(1)

# Asegurarse de que es una Series unidimensional
precios_cierre = pd.Series(precios_cierre.values, index=precios_cierre.index)

# --- 4. MOSTRAR PRIMEROS Y ÚLTIMOS 5 DATOS ---
print("\n[Paso 3/9] Mostrando los primeros 5 y los últimos 5 precios de cierre:")
print("\nPrimeros 5 datos (en wones y pesos mexicanos):")
for fecha, precio in precios_cierre.head().items():
    precio_mxn = won_a_mxn(precio)
    print(f"{fecha.strftime('%Y-%m-%d')}: {precio:,.0f} KRW ≈ ${precio_mxn:,.2f} MXN")

print("\nÚltimos 5 datos (en wones y pesos mexicanos):")
for fecha, precio in precios_cierre.tail().items():
    precio_mxn = won_a_mxn(precio)
    print(f"{fecha.strftime('%Y-%m-%d')}: {precio:,.0f} KRW ≈ ${precio_mxn:,.2f} MXN")

# --- 5. CÁLCULO DE RENDIMIENTOS LOGARÍTMICOS ---
print("\n[Paso 4/9] Calculando rendimientos logarítmicos...")
rendimientos_log = np.log(precios_cierre / precios_cierre.shift(1)).dropna()

# Asegurarse de que rendimientos_log es una Series unidimensional
rendimientos_log = pd.Series(rendimientos_log.values, index=rendimientos_log.index)

print("Rendimientos logarítmicos calculados.")

# --- 6. MOSTRAR RENDIMIENTOS DE LOS PRIMEROS Y ÚLTIMOS 5 DÍAS ---
print("\n[Paso 5/9] Mostrando los rendimientos logarítmicos de los primeros 5 y últimos 5 días:")
print("\nPrimeros 5 rendimientos:")
print(rendimientos_log.head().to_string())

print("\nÚltimos 5 rendimientos:")
print(rendimientos_log.tail().to_string())

# --- 7. CÁLCULO DE ESTADÍSTICAS DESCRIPTIVAS DE LOS RENDIMIENTOS ---
print("\n[Paso 6/9] Calculando estadísticas descriptivas de los rendimientos:")
total_rendimientos = len(rendimientos_log)
max_rendimiento = rendimientos_log.max()
min_rendimiento = rendimientos_log.min()
promedio_rendimiento = rendimientos_log.mean()
varianza_rendimiento = rendimientos_log.var()
desviacion_estandar_rendimiento = rendimientos_log.std()

print(f"\nNúmero total de rendimientos: {total_rendimientos}")
print(f"Rendimiento máximo: {max_rendimiento:.6f} ({max_rendimiento*100:.2f}%)")
print(f"Rendimiento mínimo: {min_rendimiento:.6f} ({min_rendimiento*100:.2f}%)")
print(f"Promedio de rendimiento: {promedio_rendimiento:.6f} ({promedio_rendimiento*100:.2f}%)")
print(f"Varianza de rendimiento: {varianza_rendimiento:.6f}")
print(f"Desviación estándar de rendimiento: {desviacion_estandar_rendimiento:.6f} ({desviacion_estandar_rendimiento*100:.2f}%)")

# --- 8. ESTADÍSTICAS DESCRIPTIVAS DE LOS PRECIOS ---
print("\n[Paso 7/9] Calculando estadísticas descriptivas de los precios:")
min_precio = precios_cierre.min()
max_precio = precios_cierre.max()
media_precio = precios_cierre.mean()
varianza_precio = precios_cierre.var()
desviacion_precio = precios_cierre.std()
n_datos = len(precios_cierre)

# Convertir a pesos mexicanos
min_precio_mxn = won_a_mxn(min_precio)
max_precio_mxn = won_a_mxn(max_precio)
media_precio_mxn = won_a_mxn(media_precio)

print(f"\nNúmero total de datos: {n_datos}")
print(f"Precio mínimo: {min_precio:,.0f} KRW ≈ ${min_precio_mxn:,.2f} MXN")
print(f"Precio máximo: {max_precio:,.0f} KRW ≈ ${max_precio_mxn:,.2f} MXN")
print(f"Media muestral: {media_precio:,.0f} KRW ≈ ${media_precio_mxn:,.2f} MXN")
print(f"Varianza muestral: {varianza_precio:,.0f}")
print(f"Desviación estándar muestral: {desviacion_precio:,.0f} KRW ≈ ${won_a_mxn(desviacion_precio):,.2f} MXN")

# --- 9. VISUALIZACIONES (GRÁFICAS) ---
print("\n[Paso 8/9] Generando visualizaciones...")

# Gráfica 1: Evolución del Precio de Cierre vs. Tiempo con análisis de variabilidad
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

# Gráfica en wones
ax1.plot(precios_cierre.index, precios_cierre.values, color='skyblue', linewidth=1.5)
promedio_30 = precios_cierre.rolling(window=30).mean()
promedio_90 = precios_cierre.rolling(window=90).mean()
ax1.plot(promedio_30.index, promedio_30.values, color='orange', linewidth=2, label='Promedio 30 días')
ax1.plot(promedio_90.index, promedio_90.values, color='red', linewidth=2, label='Promedio 90 días')
ax1.set_title(f'Evolución del Precio de Cierre de {TICKER_EMPRESA} (Wones)\nTendencia: {"Alta" if precios_cierre.iloc[-1] > precios_cierre.iloc[0] else "Baja"}', fontsize=14)
ax1.set_ylabel('Precio de Cierre (KRW)', fontsize=12)
ax1.grid(True, linestyle='--', alpha=0.7)
ax1.legend()

# Gráfica en pesos mexicanos
precios_mxn = precios_cierre.apply(won_a_mxn)
ax2.plot(precios_mxn.index, precios_mxn.values, color='lightgreen', linewidth=1.5)
promedio_30_mxn = precios_mxn.rolling(window=30).mean()
promedio_90_mxn = precios_mxn.rolling(window=90).mean()
ax2.plot(promedio_30_mxn.index, promedio_30_mxn.values, color='orange', linewidth=2, label='Promedio 30 días')
ax2.plot(promedio_90_mxn.index, promedio_90_mxn.values, color='red', linewidth=2, label='Promedio 90 días')
ax2.set_title(f'Evolución del Precio de Cierre de {TICKER_EMPRESA} (Pesos Mexicanos)', fontsize=14)
ax2.set_ylabel('Precio de Cierre (MXN)', fontsize=12)
ax2.set_xlabel('Fecha', fontsize=12)
ax2.grid(True, linestyle='--', alpha=0.7)
ax2.legend()

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
print("Gráfica de Evolución de Precio generada.")

# Gráfica 2: Gráfica de Caja y Bigotes para los Rendimientos Logarítmicos
plt.figure(figsize=(10, 6))
rendimientos_df = pd.DataFrame({'Rendimientos': rendimientos_log.values.flatten()})

sns.boxplot(y='Rendimientos', data=rendimientos_df, color='lightgreen')
plt.title(f'Distribución de Rendimientos Logarítmicos de {TICKER_EMPRESA}\n(Gráfica de Caja y Bigotes)', fontsize=16)
plt.ylabel('Rendimiento Logarítmico', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()
print("Gráfica de Caja y Bigotes de Rendimientos generada.")

# --- 10. TABLA DE ANÁLISIS DE PRECIOS Y RENDIMIENTOS ---
print("\n[Paso 9/9] Generando tablas de análisis...")

# Tabla de estadísticas de precios (en ambas monedas)
tabla_estadisticas_precios = pd.DataFrame({
    'Estadística': ['Número de datos', 'Mínimo', 'Máximo', 'Media muestral', 'Desviación estándar muestral'],
    'Valor KRW': [n_datos, f"{min_precio:,.0f}", f"{max_precio:,.0f}", f"{media_precio:,.0f}", f"{desviacion_precio:,.0f}"],
    'Valor MXN': [n_datos, f"${min_precio_mxn:,.2f}", f"${max_precio_mxn:,.2f}", f"${media_precio_mxn:,.2f}", f"${won_a_mxn(desviacion_precio):,.2f}"]
})

print("\n--- Tabla de Estadísticas de Precios (Últimos 3 años) ---")
print(tabla_estadisticas_precios.to_string(index=False))

# Tabla de estadísticas de rendimientos
tabla_estadisticas_rendimientos = pd.DataFrame({
    'Estadística': ['Número de rendimientos', 'Mínimo', 'Máximo', 'Promedio', 'Desviación estándar'],
    'Valor': [total_rendimientos, f"{min_rendimiento:.6f} ({min_rendimiento*100:.2f}%)", 
              f"{max_rendimiento:.6f} ({max_rendimiento*100:.2f}%)", 
              f"{promedio_rendimiento:.6f} ({promedio_rendimiento*100:.2f}%)", 
              f"{desviacion_estandar_rendimiento:.6f} ({desviacion_estandar_rendimiento*100:.2f}%)"]
})

print("\n--- Tabla de Estadísticas de Rendimientos Logarítmicos ---")
print(tabla_estadisticas_rendimientos.to_string(index=False))

# --- 11. COMPARACIÓN DETALLADA DE PRECIOS ---
print("\n--- Tabla Detallada de Comparación de Precios ---")
df_comparacion = pd.DataFrame({
    'Fecha': precios_cierre.index,
    'Precio KRW': precios_cierre.values,
    'Precio MXN': [won_a_mxn(precio) for precio in precios_cierre.values]
})

df_comparacion.reset_index(drop=True, inplace=True)

print("Primeros 5 registros:")
print(df_comparacion.head().to_string(index=False))
print("\nÚltimos 5 registros:")
print(df_comparacion.tail().to_string(index=False))

# Pedir al usuario que ingrese dos índices para comparar
try:
    idx1 = int(input(f"\nIngresa el índice de la primera fecha a comparar (entre 0 y {len(df_comparacion)-1}): "))
    idx2 = int(input(f"Ingresa el índice de la segunda fecha a comparar (entre 0 y {len(df_comparacion)-1}): "))

    if not (0 <= idx1 < len(df_comparacion) and 0 <= idx2 < len(df_comparacion)):
        raise IndexError("Índices fuera del rango válido.")

    fecha1 = df_comparacion.loc[idx1, 'Fecha']
    precio1_krw = df_comparacion.loc[idx1, 'Precio KRW']
    precio1_mxn = df_comparacion.loc[idx1, 'Precio MXN']
    fecha2 = df_comparacion.loc[idx2, 'Fecha']
    precio2_krw = df_comparacion.loc[idx2, 'Precio KRW']
    precio2_mxn = df_comparacion.loc[idx2, 'Precio MXN']

    diferencia_krw = precio2_krw - precio1_krw
    diferencia_mxn = precio2_mxn - precio1_mxn
    porcentaje_cambio = (diferencia_krw / precio1_krw) * 100 if precio1_krw != 0 else 0

    print(f"\n--- Comparación Detallada ---")
    print(f"Fecha 1: {fecha1.strftime('%Y-%m-%d')} | Precio: {precio1_krw:,.0f} KRW ≈ ${precio1_mxn:,.2f} MXN")
    print(f"Fecha 2: {fecha2.strftime('%Y-%m-%d')} | Precio: {precio2_krw:,.0f} KRW ≈ ${precio2_mxn:,.2f} MXN")
    print(f"Diferencia: {diferencia_krw:,.0f} KRW ≈ ${diferencia_mxn:,.2f} MXN")
    print(f"Porcentaje de Cambio: {porcentaje_cambio:.2f}%")

except ValueError:
    print("Entrada inválida. Por favor, ingresa números enteros para los índices.")
except IndexError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"Ocurrió un error inesperado durante la comparación: {e}")

print("\n--- Programa Finalizado ---")