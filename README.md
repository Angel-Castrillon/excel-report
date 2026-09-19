# 📊 Excel Report Dashboard

Aplicación de escritorio/local (100% offline, sin necesidad de servidores en la nube) que permite a un usuario cargar archivos Excel (`.xlsx` / `.xls`), extraer y persistir sus datos en una base de datos local SQLite, y visualizarlos mediante un dashboard interactivo con KPIs, gráficos personalizables y filtros dinámicos adaptativos.

---

## 🚀 Inicio Rápido en 1 Solo Comando

La aplicación está lista para ejecutarse localmente con un único comando:

```bash
python run.py
```

### ¿Qué hace `run.py` automáticamente?
1. Verifica si las dependencias de `requirements.txt` están instaladas (si falta alguna, la instala automáticamente).
2. Inicializa la base de datos local SQLite (`data/excel_dashboard.db`).
3. Inicia el servidor local FastAPI en `http://127.0.0.1:8000`.
4. Abre automáticamente tu navegador web predeterminado en la aplicación.

---

## 🎯 Épica y Trazabilidad de Historias de Usuario

El proyecto fue desarrollado bajo una metodología ágil modular:

| Historia de Usuario | Descripción | Estado |
| :--- | :--- | :--- |
| **HU-01** | **Inicialización de Entorno y Git**: Repositorio, conexión remota SSH, `.gitignore`, dependencias y configuraciones. |  Completado |
| **HU-02** | **Capa de Persistencia SQLite**: Base de datos local transaccional, tabla de metadatos `datasets` e índices. |  Completado |
| **HU-03** | **Ingesta y Parseo Inteligente**: Extracción con Pandas y OpenPyXL, saneamiento de columnas e inferencia automática de tipos (`date`, `numeric`, `category`, `text`). |  Completado |
| **HU-04** | **Biblioteca de Datasets (CRUD)**: Listado histórico, conmutación entre datasets sin perder datos, y borrado en cascada con `DROP TABLE`. |  Completado |
| **HU-05** | **Dashboard Interactivo**: Tarjetas KPI automáticas, gráficos responsivos con Chart.js y tabla de datos paginada/ordenable. |  Completado |
| **HU-06** | **Filtros Dinámicos y Personalización**: Generación de filtros según tipo de dato, mapeador de ejes X/Y para gráficos y persistencia de configuración por archivo. |  Completado |
| **HU-07** | **Lanzador, Dataset de Prueba y Documentación**: Script `run.py`, dataset `data/ejemplo_ventas.xlsx` y documentación completa. |  Completado |

---

## 🏗️ Arquitectura y Estructura del Proyecto

```text
excel-report/
├── app/
│   ├── __init__.py
│   ├── config.py              # Rutas absolutas, límites de archivo y servidor
│   ├── database.py            # Conexión SQLite, modo WAL y transacciones
│   ├── models.py              # Modelos y esquemas de validación (Pydantic v2)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── excel_parser.py    # Parseo e inferencia inteligente de tipos de columna
│   │   ├── dataset_service.py # CRUD de datasets y tablas dinámicas en SQLite
│   │   └── query_service.py   # Filtros dinámicos, cálculo de KPIs y agregaciones
│   └── static/
│       ├── css/
│       │   └── styles.css     # Estilos complementarios y animaciones
│       ├── js/
│       │   ├── api.js         # Cliente fetch centralizado
│       │   ├── library.js     # Barra lateral, subida drag&drop y CRUD
│       │   ├── filters.js     # Generador adaptativo de filtros dinámicos
│       │   ├── dashboard.js   # Renderizado de KPIs, Chart.js y tabla paginada
│       │   └── app.js         # Orquestador del estado y notificaciones toast
│       └── index.html         # Interfaz web SPA moderna (TailwindCSS + Chart.js)
├── data/
│   ├── excel_dashboard.db     # Base de datos SQLite (se genera localmente, ignorada en git)
│   └── ejemplo_ventas.xlsx    # Dataset de prueba listo para cargar (60 filas de ventas)
├── requirements.txt           # Dependencias de Python
├── run.py                     # Lanzador en 1 solo comando
├── .gitignore                 # Exclusiones de Git
└── README.md                  # Documentación
```

---

## 🧪 Cómo Probar la Aplicación

1. **Ejecuta el servidor**:
   ```bash
   python run.py
   ```
2. **Carga un archivo Excel**:
   - En la barra lateral izquierda, arrastra o selecciona el archivo de prueba incluido: `data/ejemplo_ventas.xlsx`.
   - El sistema extraerá los datos, inferirá tipos (fechas, regiones, categorías, montos) y persistirá la información en SQLite.
3. **Explora el Dashboard**:
   - Observa las tarjetas KPI (Registros filtrados, Total Unidades, Total Ventas, etc.).
   - Interactúa con el gráfico principal de barras y el gráfico de dona de distribución.
   - Revisa la tabla de registros en la parte inferior; haz clic en cualquier columna (por ejemplo, *Monto Total ($)*) para ordenar ascendentemente o descendentemente.
4. **Prueba los Filtros Dinámicos**:
   - Selecciona una región específica (ej. *Norte*) o una categoría (ej. *Computación*).
   - O define un rango de fechas en el filtro de fecha.
   - Observa cómo los KPIs, los gráficos y la tabla se recalculan al instante.
5. **Personaliza la Visualización**:
   - Haz clic en el botón superior **"Personalizar Visualización"**.
   - Cambia el Eje X (por ejemplo, a *Vendedor*), el Eje Y (*Monto Total*), la operación (*Suma*) y el tipo (*Líneas* o *Barras*).
   - Haz clic en **"Guardar vista para este archivo"**. Al cambiar de dataset y volver a seleccionarlo, recordará tu configuración.
6. **Gestión de Datasets (CRUD)**:
   - Sube un segundo archivo Excel.
   - Cambia entre ambos archivos haciendo clic en la biblioteca lateral: el dashboard cambiará de inmediato sin perder los datos del otro archivo.
   - Pasa el cursor sobre un archivo y haz clic en el icono de papelera para eliminarlo de forma segura (borrando su tabla en SQLite y sus metadatos).
