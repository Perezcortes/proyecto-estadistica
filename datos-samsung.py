import yfinance as yf
import pandas as pd
from datetime import date, timedelta

# Definir la empresa (ticker)
samsung_ticker = "005930.KS"

# Calcular la fecha de inicio (3 años atrás) y la fecha de fin (hoy)
end_date = date.today()
start_date = end_date - timedelta(days=3 * 365) # Aproximadamente 3 años

# Descargar los datos
datos_samsung = yf.download(samsung_ticker, start=start_date, end=end_date)

# Mostrar las primeras 5 filas del DataFrame para verificar
print(datos_samsung.head())

# Guardar los datos en un archivo CSV
datos_samsung.to_csv("precios_samsung.csv")
print("Datos de precios de Samsung guardados en 'precios_samsung.csv'")