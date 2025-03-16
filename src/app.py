import os
import requests
import sqlite3
import time
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from bs4 import BeautifulSoup

# URL de la fuente de datos
url = "https://companies-market-cap-copy.vercel.app/index.html"

# Realizar la solicitud HTTP con manejo de errores
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    print(f"Error en la solicitud: {e}")
    exit()

# Procesar HTML con BeautifulSoup
soup = BeautifulSoup(response.text, "html.parser")
tabla = soup.find('table')

if tabla is None:
    print("No se encontró la tabla en la página.")
    exit()

filas = tabla.find_all("tr")
data = []

for row in filas[1:]:  # Saltar la primera fila (encabezados)
    cols = row.find_all("td")
    if len(cols) < 2:  # Verificar que haya suficientes columnas
        continue
    fecha = cols[0].text.strip()
    ingresos = cols[1].text.strip()
    data.append([fecha, ingresos])

# Crear DataFrame ordenado por fecha
df = pd.DataFrame(data, columns=['Fecha', 'Ingresos'])

# Función para limpiar y convertir ingresos a float
def limpiador(valor):
    try:
        valor = valor.replace("$", "").replace(",", "")
        if "B" in valor:
            return float(valor.replace("B", "")) * 1e9  # Convertir a número real (billones)
        elif "M" in valor:
            return float(valor.replace("M", "")) * 1e6  # Convertir a millones
        else:
            return float(valor)
    except ValueError:
        return None  # Manejo de errores

df["Ingresos"] = df["Ingresos"].apply(limpiador)
df.dropna(inplace=True)  # Eliminar filas con valores inválidos

# Convertir fechas a datetime para mejor visualización
df["Fecha"] = pd.to_datetime(df["Fecha"])

# Conectar a la base de datos SQLite
bd = sqlite3.connect('basededatospractica.db')
cursor = bd.cursor()

# Crear tabla con `fecha` como PRIMARY KEY para evitar duplicados
cursor.execute("""
CREATE TABLE IF NOT EXISTS ingresos (
    fecha TEXT PRIMARY KEY,
    ingresos REAL
)
""")

for index, row in df.iterrows():
    cursor.execute("INSERT OR IGNORE INTO ingresos (fecha, ingresos) VALUES (?, ?)", 
                   (row["Fecha"].strftime("%Y-%m-%d"), row["Ingresos"]))  # Convertir Timestamp a string

bd.commit()
bd.close()

# Graficar los ingresos
plt.figure(figsize=(10, 6))
plt.plot(df["Fecha"], df["Ingresos"], marker="o", linestyle="-", label="Ingresos", color="b")
plt.title('Ingreso Anual de Tesla')
plt.xlabel("Fecha")
plt.ylabel("Ingresos (en dólares)")
plt.xticks(rotation=45)
plt.legend()
plt.grid(True)

# Guardar la gráfica
plt.savefig("revenue_plot.png")
plt.show()

# Gráfico de barras
plt.figure(figsize=(10, 6))
plt.bar(df["Fecha"].dt.year, df["Ingresos"], color="skyblue", alpha=0.7)
plt.xlabel("Año")
plt.ylabel("Ingresos (en dólares)")
plt.title("Ingresos de Tesla por Año")
plt.xticks(rotation=45)
plt.grid(axis='y', linestyle="--", alpha=0.7)
plt.savefig("revenue_bar_chart.png")
plt.show()

# Gráfico de densidad (KDE) para distribución de ingresos
plt.figure(figsize=(10, 6))
sns.kdeplot(df["Ingresos"], fill=True, color="purple", alpha=0.5)
plt.xlabel("Ingresos (en dólares)")
plt.ylabel("Densidad")
plt.title("Distribución de los Ingresos de Tesla")
plt.grid(True)
plt.savefig("revenue_distribution.png")
plt.show()