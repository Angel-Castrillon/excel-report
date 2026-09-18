# 📊 Excel Report Dashboard

Aplicación local y offline para cargar archivos Excel (`.xlsx` / `.xls`), extraer y persistir sus datos en una base de datos local SQLite, y visualizarlos en un dashboard interactivo con KPIs, gráficos personalizables y filtros dinámicos.

---

## 🎯 Épica: Plataforma Local de Análisis y Visualización Dinámica de Archivos Excel

Este proyecto se desarrolla de forma modular y guiada mediante Historias de Usuario (HUs):

- [x] **HU-01: Inicialización del Repositorio, Git y Entorno Base**
- [ ] **HU-02: Capa de Base de Datos y Persistencia SQLite**
- [ ] **HU-03: Ingesta y Parseo Inteligente de Excel (.xlsx / .xls)**
- [ ] **HU-04: Biblioteca de Datasets y Gestión CRUD**
- [ ] **HU-05: Dashboard Interactivo de Visualización (KPIs, Gráficos y Tablas)**
- [ ] **HU-06: Personalización Dinámica de Visualizaciones y Filtros Avanzados**
- [ ] **HU-07: Script de Lanzamiento, Datasets de Prueba y Documentación Final**

---

## 🚀 Requisitos y Ejecución Rápida

1. Asegúrate de tener instalado **Python 3.10+**.
2. Clona el repositorio si aún no lo has hecho:
   ```bash
   git clone git@github.com:Angel-Castrillon/excel-report.git
   cd excel-report
   ```
3. Ejecuta la aplicación con un solo comando:
   ```bash
   python run.py
   ```
   *El script se encargará de verificar/instalar las dependencias de `requirements.txt`, levantar el servidor local e iniciar automáticamente tu navegador web.*
