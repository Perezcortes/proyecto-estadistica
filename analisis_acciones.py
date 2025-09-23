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

# Funciones para convertir entre monedas
def krw_a_usd(krw):
    return krw / usd_krw

def krw_a_mxn(krw):
    return (krw / usd_krw) * usd_mxn

def usd_a_mxn(usd):
    return usd * usd_mxn

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

# --- 4. MOSTRAR PRIMEROS Y ÚLTIMOS 5 DATOS EN LAS 3 MONEDAS ---
print("\n[Paso 3/9] Mostrando los primeros 5 y los últimos 5 precios de cierre:")
print("\nPrimeros 5 datos (en las 3 monedas):")
for fecha, precio_krw in precios_cierre.head().items():
    precio_usd = krw_a_usd(precio_krw)
    precio_mxn = krw_a_mxn(precio_krw)
    print(f"{fecha.strftime('%Y-%m-%d')}: {precio_krw:,.0f} KRW | ${precio_usd:,.2f} USD | ${precio_mxn:,.2f} MXN")

print("\nÚltimos 5 datos (en las 3 monedas):")
for fecha, precio_krw in precios_cierre.tail().items():
    precio_usd = krw_a_usd(precio_krw)
    precio_mxn = krw_a_mxn(precio_krw)
    print(f"{fecha.strftime('%Y-%m-%d')}: {precio_krw:,.0f} KRW | ${precio_usd:,.2f} USD | ${precio_mxn:,.2f} MXN")

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

# --- 8. ESTADÍSTICAS DESCRIPTIVAS DE LOS PRECIOS EN LAS 3 MONEDAS ---
print("\n[Paso 7/9] Calculando estadísticas descriptivas de los precios:")
min_precio_krw = precios_cierre.min()
max_precio_krw = precios_cierre.max()
media_precio_krw = precios_cierre.mean()
varianza_precio = precios_cierre.var()
desviacion_precio_krw = precios_cierre.std()
n_datos = len(precios_cierre)

# Convertir a las otras monedas
min_precio_usd = krw_a_usd(min_precio_krw)
max_precio_usd = krw_a_usd(max_precio_krw)
media_precio_usd = krw_a_usd(media_precio_krw)
desviacion_precio_usd = krw_a_usd(desviacion_precio_krw)

min_precio_mxn = krw_a_mxn(min_precio_krw)
max_precio_mxn = krw_a_mxn(max_precio_krw)
media_precio_mxn = krw_a_mxn(media_precio_krw)
desviacion_precio_mxn = krw_a_mxn(desviacion_precio_krw)

print(f"\nNúmero total de datos: {n_datos}")
print(f"\nPrecio mínimo:")
print(f"  • {min_precio_krw:,.0f} KRW | ${min_precio_usd:,.2f} USD | ${min_precio_mxn:,.2f} MXN")
print(f"\nPrecio máximo:")
print(f"  • {max_precio_krw:,.0f} KRW | ${max_precio_usd:,.2f} USD | ${max_precio_mxn:,.2f} MXN")
print(f"\nMedia muestral:")
print(f"  • {media_precio_krw:,.0f} KRW | ${media_precio_usd:,.2f} USD | ${media_precio_mxn:,.2f} MXN")
print(f"\nVarianza muestral: {varianza_precio:,.0f}")
print(f"\nDesviación estándar muestral:")
print(f"  • {desviacion_precio_krw:,.0f} KRW | ${desviacion_precio_usd:,.2f} USD | ${desviacion_precio_mxn:,.2f} MXN")

# --- 9. VISUALIZACIONES (GRÁFICAS) EN LAS 3 MONEDAS ---
print("\n[Paso 8/9] Generando visualizaciones...")

# Gráfica 1: Evolución del Precio de Cierre vs. Tiempo en las 3 monedas
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(16, 12))

# Gráfica en wones
ax1.plot(precios_cierre.index, precios_cierre.values, color='skyblue', linewidth=1.5)
promedio_30_krw = precios_cierre.rolling(window=30).mean()
promedio_90_krw = precios_cierre.rolling(window=90).mean()
ax1.plot(promedio_30_krw.index, promedio_30_krw.values, color='orange', linewidth=2, label='Promedio 30 días')
ax1.plot(promedio_90_krw.index, promedio_90_krw.values, color='red', linewidth=2, label='Promedio 90 días')
ax1.set_title(f'Evolución del Precio de Cierre de {TICKER_EMPRESA} (Won Surcoreano)\nTendencia: {"Alta" if precios_cierre.iloc[-1] > precios_cierre.iloc[0] else "Baja"}', fontsize=14)
ax1.set_ylabel('Precio de Cierre (KRW)', fontsize=12)
ax1.grid(True, linestyle='--', alpha=0.7)
ax1.legend()

# Gráfica en dólares
precios_usd = precios_cierre.apply(krw_a_usd)
ax2.plot(precios_usd.index, precios_usd.values, color='lightcoral', linewidth=1.5)
promedio_30_usd = precios_usd.rolling(window=30).mean()
promedio_90_usd = precios_usd.rolling(window=90).mean()
ax2.plot(promedio_30_usd.index, promedio_30_usd.values, color='orange', linewidth=2, label='Promedio 30 días')
ax2.plot(promedio_90_usd.index, promedio_90_usd.values, color='red', linewidth=2, label='Promedio 90 días')
ax2.set_title(f'Evolución del Precio de Cierre de {TICKER_EMPRESA} (Dólares Estadounidenses)', fontsize=14)
ax2.set_ylabel('Precio de Cierre (USD)', fontsize=12)
ax2.grid(True, linestyle='--', alpha=0.7)
ax2.legend()

# Gráfica en pesos mexicanos
precios_mxn = precios_cierre.apply(krw_a_mxn)
ax3.plot(precios_mxn.index, precios_mxn.values, color='lightgreen', linewidth=1.5)
promedio_30_mxn = precios_mxn.rolling(window=30).mean()
promedio_90_mxn = precios_mxn.rolling(window=90).mean()
ax3.plot(promedio_30_mxn.index, promedio_30_mxn.values, color='orange', linewidth=2, label='Promedio 30 días')
ax3.plot(promedio_90_mxn.index, promedio_90_mxn.values, color='red', linewidth=2, label='Promedio 90 días')
ax3.set_title(f'Evolución del Precio de Cierre de {TICKER_EMPRESA} (Pesos Mexicanos)', fontsize=14)
ax3.set_ylabel('Precio de Cierre (MXN)', fontsize=12)
ax3.set_xlabel('Fecha', fontsize=12)
ax3.grid(True, linestyle='--', alpha=0.7)
ax3.legend()

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
print("Gráfica de Evolución de Precio en las 3 monedas generada.")

# Gráfica 2: Estadísticas Descriptivas de Precios (Gráfica de Barras)
plt.figure(figsize=(12, 8))
estadisticas = ['Mínimo', 'Máximo', 'Media', 'Varianza/10000', 'Desv. Estándar']
valores_krw = [min_precio_krw, max_precio_krw, media_precio_krw, varianza_precio/10000, desviacion_precio_krw]
valores_usd = [min_precio_usd, max_precio_usd, media_precio_usd, varianza_precio/(10000*usd_krw**2), desviacion_precio_usd]

x = np.arange(len(estadisticas))
width = 0.35

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Gráfica en KRW
bars1 = ax1.bar(x, valores_krw, width, label='KRW', color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'])
ax1.set_xlabel('Estadísticas')
ax1.set_ylabel('Valores (KRW)')
ax1.set_title('Estadísticas Descriptivas de Precios Samsung (KRW)')
ax1.set_xticks(x)
ax1.set_xticklabels(estadisticas, rotation=45)
ax1.grid(True, linestyle='--', alpha=0.7)

# Agregar valores encima de las barras
for bar, valor in zip(bars1, valores_krw):
    height = bar.get_height()
    ax1.annotate(f'{valor:,.0f}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),  # 3 puntos de offset vertical
                textcoords="offset points",
                ha='center', va='bottom', fontsize=9)

# Gráfica en USD
bars2 = ax2.bar(x, valores_usd, width, label='USD', color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'])
ax2.set_xlabel('Estadísticas')
ax2.set_ylabel('Valores (USD)')
ax2.set_title('Estadísticas Descriptivas de Precios Samsung (USD)')
ax2.set_xticks(x)
ax2.set_xticklabels(estadisticas, rotation=45)
ax2.grid(True, linestyle='--', alpha=0.7)

# Agregar valores encima de las barras
for bar, valor in zip(bars2, valores_usd):
    height = bar.get_height()
    ax2.annotate(f'${valor:.2f}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.show()
print("Gráfica de Estadísticas Descriptivas generada.")

# Gráfica 3: Tiempo vs Rendimientos Logarítmicos
plt.figure(figsize=(14, 8))
plt.plot(rendimientos_log.index, rendimientos_log.values, color='purple', linewidth=0.8, alpha=0.7)
plt.axhline(y=0, color='black', linestyle='-', linewidth=1, alpha=0.5)
plt.axhline(y=promedio_rendimiento, color='red', linestyle='--', linewidth=2, label=f'Media ({promedio_rendimiento*100:.3f}%)')
plt.axhline(y=promedio_rendimiento + desviacion_estandar_rendimiento, color='orange', linestyle='--', linewidth=1.5, alpha=0.7, label=f'+1σ ({(promedio_rendimiento + desviacion_estandar_rendimiento)*100:.2f}%)')
plt.axhline(y=promedio_rendimiento - desviacion_estandar_rendimiento, color='orange', linestyle='--', linewidth=1.5, alpha=0.7, label=f'-1σ ({(promedio_rendimiento - desviacion_estandar_rendimiento)*100:.2f}%)')

# Resaltar rendimientos extremos
rendimientos_extremos = rendimientos_log[(rendimientos_log > promedio_rendimiento + 2*desviacion_estandar_rendimiento) | 
                                        (rendimientos_log < promedio_rendimiento - 2*desviacion_estandar_rendimiento)]
if not rendimientos_extremos.empty:
    plt.scatter(rendimientos_extremos.index, rendimientos_extremos.values, 
               color='red', s=30, zorder=5, label=f'Valores extremos (±2σ): {len(rendimientos_extremos)}')

plt.title(f'Evolución de Rendimientos Logarítmicos de {TICKER_EMPRESA} a lo Largo del Tiempo', fontsize=16)
plt.xlabel('Fecha', fontsize=12)
plt.ylabel('Rendimiento Logarítmico', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.3)
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
print("Gráfica de Tiempo vs Rendimientos generada.")

# Gráfica 4: Gráfica de Caja y Bigotes para los Rendimientos Logarítmicos
plt.figure(figsize=(10, 6))
rendimientos_df = pd.DataFrame({'Rendimientos': rendimientos_log.values.flatten()})

sns.boxplot(y='Rendimientos', data=rendimientos_df, color='lightgreen')
plt.title(f'Distribución de Rendimientos Logarítmicos de {TICKER_EMPRESA}\n(Gráfica de Caja y Bigotes)', fontsize=16)
plt.ylabel('Rendimiento Logarítmico', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()
print("Gráfica de Caja y Bigotes de Rendimientos generada.")

# --- 10. TABLA DE ANÁLISIS DE PRECIOS EN LAS 3 MONEDAS ---
print("\n[Paso 9/9] Generando tablas de análisis...")

# Tabla de estadísticas de precios (en las 3 monedas)
tabla_estadisticas_precios = pd.DataFrame({
    'Estadística': ['Número de datos', 'Mínimo', 'Máximo', 'Media muestral', 'Desviación estándar'],
    'Won (KRW)': [
        n_datos, 
        f"{min_precio_krw:,.0f}", 
        f"{max_precio_krw:,.0f}", 
        f"{media_precio_krw:,.0f}", 
        f"{desviacion_precio_krw:,.0f}"
    ],
    'Dólares (USD)': [
        n_datos, 
        f"${min_precio_usd:,.2f}", 
        f"${max_precio_usd:,.2f}", 
        f"${media_precio_usd:,.2f}", 
        f"${desviacion_precio_usd:,.2f}"
    ],
    'Pesos (MXN)': [
        n_datos, 
        f"${min_precio_mxn:,.2f}", 
        f"${max_precio_mxn:,.2f}", 
        f"${media_precio_mxn:,.2f}", 
        f"${desviacion_precio_mxn:,.2f}"
    ]
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

# --- 11. COMPARACIÓN DETALLADA DE PRECIOS EN LAS 3 MONEDAS ---
print("\n--- Tabla Detallada de Comparación de Precios (3 Monedas) ---")
df_comparacion = pd.DataFrame({
    'Fecha': precios_cierre.index,
    'Precio KRW': precios_cierre.values,
    'Precio USD': [krw_a_usd(precio) for precio in precios_cierre.values],
    'Precio MXN': [krw_a_mxn(precio) for precio in precios_cierre.values]
})

df_comparacion.reset_index(drop=True, inplace=True)

print("Primeros 5 registros:")
primeros_5 = df_comparacion.head().copy()
primeros_5['Precio KRW'] = primeros_5['Precio KRW'].apply(lambda x: f"{x:,.0f}")
primeros_5['Precio USD'] = primeros_5['Precio USD'].apply(lambda x: f"${x:,.2f}")
primeros_5['Precio MXN'] = primeros_5['Precio MXN'].apply(lambda x: f"${x:,.2f}")
print(primeros_5.to_string(index=False))

print("\nÚltimos 5 registros:")
ultimos_5 = df_comparacion.tail().copy()
ultimos_5['Precio KRW'] = ultimos_5['Precio KRW'].apply(lambda x: f"{x:,.0f}")
ultimos_5['Precio USD'] = ultimos_5['Precio USD'].apply(lambda x: f"${x:,.2f}")
ultimos_5['Precio MXN'] = ultimos_5['Precio MXN'].apply(lambda x: f"${x:,.2f}")
print(ultimos_5.to_string(index=False))

# Pedir al usuario que ingrese dos índices para comparar
try:
    idx1 = int(input(f"\nIngresa el índice de la primera fecha a comparar (entre 0 y {len(df_comparacion)-1}): "))
    idx2 = int(input(f"Ingresa el índice de la segunda fecha a comparar (entre 0 y {len(df_comparacion)-1}): "))

    if not (0 <= idx1 < len(df_comparacion) and 0 <= idx2 < len(df_comparacion)):
        raise IndexError("Índices fuera del rango válido.")

    fecha1 = df_comparacion.loc[idx1, 'Fecha']
    precio1_krw = df_comparacion.loc[idx1, 'Precio KRW']
    precio1_usd = df_comparacion.loc[idx1, 'Precio USD']
    precio1_mxn = df_comparacion.loc[idx1, 'Precio MXN']
    
    fecha2 = df_comparacion.loc[idx2, 'Fecha']
    precio2_krw = df_comparacion.loc[idx2, 'Precio KRW']
    precio2_usd = df_comparacion.loc[idx2, 'Precio USD']
    precio2_mxn = df_comparacion.loc[idx2, 'Precio MXN']

    diferencia_krw = precio2_krw - precio1_krw
    diferencia_usd = precio2_usd - precio1_usd
    diferencia_mxn = precio2_mxn - precio1_mxn
    porcentaje_cambio = (diferencia_krw / precio1_krw) * 100 if precio1_krw != 0 else 0

    print(f"\n=== COMPARACIÓN DETALLADA EN LAS 3 MONEDAS ===")
    print(f"\nFecha 1: {fecha1.strftime('%Y-%m-%d')}")
    print(f"  • {precio1_krw:,.0f} KRW | ${precio1_usd:,.2f} USD | ${precio1_mxn:,.2f} MXN")
    print(f"\nFecha 2: {fecha2.strftime('%Y-%m-%d')}")
    print(f"  • {precio2_krw:,.0f} KRW | ${precio2_usd:,.2f} USD | ${precio2_mxn:,.2f} MXN")
    print(f"\nDiferencia:")
    print(f"  • {diferencia_krw:+,.0f} KRW | ${diferencia_usd:+,.2f} USD | ${diferencia_mxn:+,.2f} MXN")
    print(f"\nPorcentaje de Cambio: {porcentaje_cambio:+.2f}%")
    
    if porcentaje_cambio > 0:
        print("📈 La acción ha aumentado de valor")
    elif porcentaje_cambio < 0:
        print("📉 La acción ha disminuido de valor")
    else:
        print("➡️ La acción mantiene el mismo valor")

except ValueError:
    print("Entrada inválida. Por favor, ingresa números enteros para los índices.")
except IndexError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"Ocurrió un error inesperado durante la comparación: {e}")

print(f"\n=== RESUMEN DE TIPOS DE CAMBIO UTILIZADOS ===")
print(f"1 USD = {usd_krw:,.2f} KRW")
print(f"1 USD = {usd_mxn:,.2f} MXN")
print(f"1,000 KRW = ${krw_a_usd(1000):,.2f} USD = ${krw_a_mxn(1000):,.2f} MXN")

print("\n--- Programa Finalizado ---")