# 📊 Excel Report Dashboard

Aplicación de escritorio/local (100% offline, sin necesidad de servidores en la nube) que permite a un usuario cargar archivos Excel (`.xlsx` / `.xls`), extraer y persistir sus datos en una base de datos local SQLite, y visualizarlos mediante un dashboard interactivo con KPIs, gráficos personalizables y filtros dinámicos adaptativos.

---

## 🖱️ Ejecución con Doble Clic (Directa en Windows)

Para abrir la aplicación sin necesidad de escribir comandos en una terminal:

1. **Opción A (Recomendada con consola)**: Haz doble clic en el archivo **`Iniciar-App.bat`**.
   - Mostrará una ventana de bienvenida, verificará las dependencias y abrirá automáticamente el navegador en `http://127.0.0.1:8000`.
2. **Opción B (Modo Silencioso / Sin ventana negra)**: Haz doble clic en **`Iniciar-App-Silencioso.vbs`**.
   - Arrancará el servidor en segundo plano y abrirá directamente tu navegador web sin dejar ninguna ventana negra de consola visible.
3. **Opción C (Desde la terminal)**:
   ```bash
   python run.py
   ```
4. **Opción D (Compilar a ejecutable .exe nativo)**:
   ```bash
   python build_exe.py
   ```
   *Genera el ejecutable binario en `dist/ExcelReportStudio/ExcelReportStudio.exe`.*

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
| **HU-08** | **Ejecutable y Lanzador con Doble Clic**: Lanzadores directos de Windows (`Iniciar-App.bat`, `Iniciar-App-Silencioso.vbs`) y script de compilación `build_exe.py`. |  Completado |

---

## 🏗️ Arquitectura y Estructura del Proyecto

```text
excel-report/
├── Iniciar-App.bat            # 🖱️ Lanzador directo con doble clic (Windows)
├── Iniciar-App-Silencioso.vbs # 🖱️ Lanzador sin ventana de consola (segundo plano)
├── build_exe.py               # 📦 Script para compilar a .exe con PyInstaller
├── run.py                     # Punto de entrada y verificador de dependencias
├── requirements.txt           # Dependencias de Python (FastAPI, Pandas, OpenPyXL, etc.)
├── .gitignore                 # Exclusiones de Git (bases de datos locales, temporales)
├── README.md                  # Documentación
├── app/
│   ├── __init__.py
│   ├── config.py              # Rutas absolutas y detección de entorno congelado (.exe)
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
└── data/
    ├── excel_dashboard.db     # Base de datos SQLite (se genera localmente, ignorada en git)
    └── ejemplo_ventas.xlsx    # Dataset de prueba listo para cargar (60 filas de ventas)
```

---

## 🧪 Cómo Probar la Aplicación

1. **Ejecuta la app**:
   - Haz doble clic en `Iniciar-App.bat` o `Iniciar-App-Silencioso.vbs`.
2. **Carga un archivo Excel**:
   - En la barra lateral izquierda, arrastra o selecciona el archivo de prueba incluido: `data/ejemplo_ventas.xlsx`.
   - El sistema extraerá los datos, inferirá tipos (fechas, regiones, categorías, montos) y persistirá la información en SQLite.
3. **Explora el Dashboard**:
   - Observa las tarjetas KPI (Registros filtrados, Total Unidades, Total Ventas, etc.).
   - Interactúa con el gráfico principal de barras y el gráfico de dona de distribución.
   - Revisa la tabla de registros en la parte inferior; haz clic en cualquier columna para ordenar.
4. **Prueba los Filtros Dinámicos**:
   - Selecciona una región específica (ej. *Norte*) o una categoría (ej. *Computación*).
   - O define un rango de fechas en el filtro de fecha.
   - Observa cómo los KPIs, los gráficos y la tabla se recalculan al instante.
5. **Personaliza la Visualización**:
   - Haz clic en el botón superior **"Personalizar Visualización"**.
   - Cambia el Eje X, el Eje Y, la operación (*Suma*, *Promedio*) y el tipo (*Líneas*, *Barras*).
   - Haz clic en **"Guardar vista para este archivo"**. Al cambiar de dataset y volver a seleccionarlo, recordará tu configuración.
6. **Gestión de Datasets (CRUD)**:
   - Sube otro archivo Excel.
   - Cambia entre ambos archivos haciendo clic en la biblioteca lateral.
   - Pasa el cursor sobre un archivo y haz clic en el icono de papelera para eliminarlo de forma segura.
