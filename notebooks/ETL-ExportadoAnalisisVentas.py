# %% [markdown]
# # 📊Sistema de Análisis de Ventas con Proceso ETL
# 
# Este notebook implementa un **proceso ETL completo** para consolidar datos de clientes, productos y ventas desde múltiples fuentes y cargarlos en MySQL para análisis.
# <div>
#     <h4>Diagramas:</h4>
#     <img alt="Imagen del Diagrama ER" src="../docs/DiagramaER.png" style="float: left;"/>
#     <img alt="Imagen del flujo ETL" src="../docs/DiagramaFlujoETL.png" style="*float: right;"/>
# </div>

# %%
# Imports y Conexión a la Base de Datos
import pandas as pd
import mysql.connector
from sqlalchemy import create_engine

# Datos de conexión
DB_USER = "root"
DB_PASS = ""
DB_HOST = "localhost"
DB_NAME = "sales_db"

engine = create_engine(f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}")

# %% [markdown]
# ## 2. Carga de Datos
# 
# Cargo los CSV desde la carpeta `data/`:
# 
# - `customers.csv` Información de clientes
# - `products.csv` Información de productos
# - `orders.csv` Información de pedidos/ventas
# - `order_details.csv` Detalles de pedidos

# %%
# Cargar CSVs
customers = pd.read_csv("../data/customers.csv")
products = pd.read_csv("../data/products.csv")
orders = pd.read_csv("../data/orders.csv")
order_details = pd.read_csv("../data/order_details.csv")

print(customers.head())
print(products.head())
print(orders.head())
print(order_details.head())

# %% [markdown]
# ## 3. Limpieza y Normalización
# 
# - Elimino los duplicados, aplicando algo de normalización
# - Relleno valores nulos básicos en los registros
# - Aseguro que los tipos de datos sean correctos

# %%
# Limpiar y Normalizar

# Quitar duplicados
customers.drop_duplicates(inplace=True)
products.drop_duplicates(inplace=True)
orders.drop_duplicates(inplace=True)
order_details.drop_duplicates(inplace=True)

# Rellenar nulos básicos
customers.fillna({"Email":"", "Phone":""}, inplace=True)
products.fillna({"Category":"Unknown"}, inplace=True)

# Asegurar tipos
customers["CustomerID"] = customers["CustomerID"].astype(int)
products["ProductID"] = products["ProductID"].astype(int)
orders["OrderID"] = orders["OrderID"].astype(int)
orders["CustomerID"] = orders["CustomerID"].astype(int)
orders["OrderDate"] = pd.to_datetime(orders["OrderDate"], errors="coerce")
order_details["OrderID"] = order_details["OrderID"].astype(int)
order_details["ProductID"] = order_details["ProductID"].astype(int)

# %% [markdown]
# ## 4. Carga Inicial a MySQL
# 
# - Limpio las tablas existentes
# - Procedo a insertar clientes, productos y pedidos en la base de datos

# %%
# Cargar en MySQL
with engine.begin() as conn:
    # Limpiar tablas antes de insertar
    conn.exec_driver_sql("DELETE FROM order_details")
    conn.exec_driver_sql("DELETE FROM orders")
    conn.exec_driver_sql("DELETE FROM products")
    conn.exec_driver_sql("DELETE FROM customers")

customers.to_sql("customers", engine, if_exists="append", index=False)
products.to_sql("products", engine, if_exists="append", index=False)
orders.to_sql("orders", engine, if_exists="append", index=False)

# %% [markdown]
# ## 5. Manejo de Duplicados en Detalles de Pedido
# 
# - Detecto y busco duplicados por `OrderID` y `ProductID`
# - Para despues agrupar y sumar `Quantity` y `TotalPrice`

# %%
# Manejar duplicados en order_details sumando cantidades y precios
dups = order_details[order_details.duplicated(subset=["OrderID","ProductID"], keep=False)]
print(dups.head())
print("Duplicados encontrados:", len(dups))

order_details = order_details.drop_duplicates(subset=["OrderID","ProductID"])

# Agrupar duplicados sumando Quantity y TotalPrice
order_details = (
    order_details
    .groupby(["OrderID","ProductID"], as_index=False)
    .agg({"Quantity":"sum","TotalPrice":"sum"})
)

# %% [markdown]
# ## 6. Carga Optimizada de Order Details
# 
# - Aqui debido a que son mas de 60 mil registros voy a usar una inserción por bloques (`chunksize`) y multi-insert (`method='multi'`) para que el MySQL pueda recibir los datos en paquetes de 10 mil registros evitando que el servidor se atasque y controlando un poco el rendimiento

# %%
# Cargar order_details con optimizaciones chunksize y multi-insert
order_details.to_sql(
    "order_details",
    engine,
    if_exists="append",
    index=False,
    chunksize=10000,   # inserta de 10000 en 10000
    method="multi"    # agrupa filas en un solo INSERT
)

# %% [markdown]
# ## 7. Validación de Datos Cargados
# 
# - Estas consultas rápidas van a confirmar la cantidad de registros en cada tabla

# %%
# Validación 
with engine.connect() as conn:
    print(pd.read_sql("SELECT COUNT(*) AS total_customers FROM customers", conn))
    print(pd.read_sql("SELECT COUNT(*) AS total_products FROM products", conn))
    print(pd.read_sql("SELECT COUNT(*) AS total_orders FROM orders", conn))
    print(pd.read_sql("SELECT COUNT(*) AS total_order_details FROM order_details", conn))



