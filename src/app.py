import os
from bs4 import BeautifulSoup
import requests
import time
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

url = "https://companies-market-cap-copy.vercel.app/index.html"

response = requests.get(url)
if response.status_code == 200:
    html = response.text
else:
    print(f"Error en la solicitud: {response.status_code}")
    exit()
soup = BeautifulSoup(html, "html.parser")
tabla = soup.find('table')
filas = tabla.find_all("tr")
data = []
for row in filas[1:]: 
    cols = row.find_all("td")
    fecha = cols[0].text.strip()
    ingresos = cols[1].text.strip()
    data.append([fecha, ingresos])
df = pd.DataFrame(data, columns=['Fecha', 'Ingresos']).sort_values('Fecha')


def limpiador(valor):
    if "B" in valor:
        editar = float(valor.replace("B", "").replace("$", "").replace(",", ""))
        return editar   
df["Ingresos"] = df["Ingresos"].apply(limpiador)
bd = sqlite3.connect('basededatospractica.db')
cursor = bd.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS ingresos (
    fecha TEXT,
    ingresos REAL
)
""")
for index, row in df.iterrows():
    cursor.execute("INSERT INTO ingresos (fecha, ingresos) VALUES (?, ?)", (row["Fecha"], row["Ingresos"]))
bd.commit()
bd.close()

plt.figure(figsize=(10, 6))
plt.plot(df["Fecha"], df["Ingresos"], label="Ingresos")
plt.title('Ingreso anual TESLA')
plt.xlabel("FECHA")
plt.ylabel("Ingr. en B")
plt.xticks(rotation=45)
plt.legend()
plt.grid(True)

plt.savefig("revenue_plot.png")
plt.show()