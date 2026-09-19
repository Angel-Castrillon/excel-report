/**
 * Módulo de visualización del Dashboard.
 * Gestiona tarjetas KPI, instancias de Chart.js y tabla de datos interactiva paginada.
 */
const Dashboard = {
  currentDataset: null,
  activeFilters: [],
  
  // Instancias de Chart.js
  chartMain: null,
  chartSecondary: null,

  // Configuración actual de gráficos
  chartConfig: {
    type: 'bar',
    dimension: null,
    metric: null,
    aggregation: 'sum'
  },

  // Estado de la tabla
  tableState: {
    page: 1,
    limit: 25,
    total: 0,
    sortBy: null,
    sortOrder: 'asc',
    search: ''
  },

  init() {
    this.bindEvents();
  },

  bindEvents() {
    // Paginación de la tabla
    document.getElementById('table-prev-btn').addEventListener('click', () => {
      if (this.tableState.page > 1) {
        this.tableState.page--;
        this.loadTableData();
      }
    });

    document.getElementById('table-next-btn').addEventListener('click', () => {
      const maxPages = Math.ceil(this.tableState.total / this.tableState.limit);
      if (this.tableState.page < maxPages) {
        this.tableState.page++;
        this.loadTableData();
      }
    });

    document.getElementById('table-page-size').addEventListener('change', (e) => {
      this.tableState.limit = parseInt(e.target.value, 10);
      this.tableState.page = 1;
      this.loadTableData();
    });

    // Guardar configuración personalizada
    document.getElementById('save-custom-config-btn').addEventListener('click', () => {
      this.saveCurrentConfiguration();
    });
  },

  async loadDataset(dataset) {
    this.currentDataset = dataset;
    this.activeFilters = [];
    this.tableState.page = 1;
    this.tableState.sortBy = null;

    // Actualizar encabezado del dashboard
    document.getElementById('dash-filename').textContent = dataset.original_filename;
    document.getElementById('dash-rows-count').textContent = `${dataset.row_count.toLocaleString()} registros`;
    document.getElementById('dash-cols-count').textContent = `${dataset.column_count} columnas`;
    document.getElementById('dash-file-size').textContent = dataset.file_size_human;

    // Inicializar configuración de gráficos (usar guardada si existe, o inferir la mejor opción)
    this.setupChartConfig();
    this.renderCustomizerModalControls();

    // Cargar visualizaciones en paralelo
    await Promise.all([
      this.loadKPIs(),
      this.loadCharts(),
      this.loadTableData()
    ]);
  },

  setupChartConfig() {
    const cols = this.currentDataset.columns_metadata;
    const catOrDateCols = cols.filter(c => ['category', 'date'].includes(c.data_type));
    const numCols = cols.filter(c => c.data_type === 'numeric');

    if (this.currentDataset.custom_config && this.currentDataset.custom_config.chart) {
      // Usar la guardada por el usuario
      this.chartConfig = { ...this.currentDataset.custom_config.chart };
    } else {
      // Opciones por defecto inteligentes
      this.chartConfig = {
        type: 'bar',
        dimension: catOrDateCols.length > 0 ? catOrDateCols[0].clean_name : (cols[0] ? cols[0].clean_name : null),
        metric: numCols.length > 0 ? numCols[0].clean_name : null,
        aggregation: numCols.length > 0 ? 'sum' : 'count'
      };
    }
  },

  renderCustomizerModalControls() {
    const cols = this.currentDataset.columns_metadata;
    const dimSelect = document.getElementById('config-x-axis');
    const metricSelect = document.getElementById('config-y-metric');
    const aggSelect = document.getElementById('config-agg-func');
    const typeSelect = document.getElementById('config-chart-type');

    // Poblar Eje X (dimensiones recomendadas primero)
    dimSelect.innerHTML = cols.map(c => `
      <option value="${c.clean_name}" ${c.clean_name === this.chartConfig.dimension ? 'selected' : ''}>
        ${c.name} (${c.data_type})
      </option>
    `).join('');

    // Poblar Eje Y (métricas numéricas)
    const numCols = cols.filter(c => c.data_type === 'numeric');
    metricSelect.innerHTML = `
      <option value="" ${!this.chartConfig.metric ? 'selected' : ''}>-- Conteo de registros (COUNT) --</option>
      ${numCols.map(c => `
        <option value="${c.clean_name}" ${c.clean_name === this.chartConfig.metric ? 'selected' : ''}>
          ${c.name} (Numérico)
        </option>
      `).join('')}
    `;

    aggSelect.value = this.chartConfig.aggregation || 'sum';
    typeSelect.value = this.chartConfig.type || 'bar';

    // Escuchar cambios para previsualizar inmediatamente
    const onChange = () => {
      this.chartConfig.dimension = dimSelect.value;
      this.chartConfig.metric = metricSelect.value || null;
      this.chartConfig.aggregation = aggSelect.value;
      this.chartConfig.type = typeSelect.value;
      this.loadCharts();
    };

    dimSelect.onchange = onChange;
    metricSelect.onchange = onChange;
    aggSelect.onchange = onChange;
    typeSelect.onchange = onChange;
  },

  async updateFilters(filters) {
    this.activeFilters = filters;
    this.tableState.page = 1;
    await Promise.all([
      this.loadKPIs(),
      this.loadCharts(),
      this.loadTableData()
    ]);
  },

  async loadKPIs() {
    const container = document.getElementById('kpis-container');
    container.innerHTML = '<div class="col-span-full py-4 text-center text-xs text-slate-400">Calculando indicadores...</div>';

    try {
      const res = await API.getKPIs(this.currentDataset.id, this.activeFilters);
      const cards = res.kpi_cards || [];

      if (cards.length === 0) {
        container.innerHTML = '<div class="col-span-full text-xs text-slate-400">Sin datos para mostrar KPIs</div>';
        return;
      }

      container.innerHTML = cards.map(c => `
        <div class="kpi-card bg-white p-4 rounded-xl border border-slate-200/80 flex flex-col justify-between transition-all">
          <div class="flex items-center justify-between text-slate-400">
            <span class="text-xs font-medium text-slate-500 uppercase tracking-wider truncate">${c.title}</span>
            <div class="p-1.5 rounded-lg bg-blue-50 text-blue-600">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
          </div>
          <div class="mt-3">
            <p class="text-2xl font-bold text-slate-800 tracking-tight">${c.value}</p>
            <p class="text-xs text-slate-400 mt-1 truncate">${c.subtitle}</p>
          </div>
        </div>
      `).join('');
    } catch (err) {
      container.innerHTML = `<div class="col-span-full text-xs text-red-500">Error en KPIs: ${err.message}</div>`;
    }
  },

  async loadCharts() {
    if (!this.chartConfig.dimension) return;

    const ctxMain = document.getElementById('main-chart-canvas').getContext('2d');
    const ctxSec = document.getElementById('secondary-chart-canvas').getContext('2d');

    try {
      // 1. Cargar datos del gráfico principal
      const mainData = await API.getChartData(this.currentDataset.id, {
        dimension: this.chartConfig.dimension,
        metric: this.chartConfig.metric,
        aggregation_func: this.chartConfig.aggregation,
        filters: this.activeFilters,
        limit: 15
      });

      // Título del gráfico
      document.getElementById('main-chart-title').textContent = 
        `${mainData.metric_label} por ${mainData.dimension_name}`;

      if (this.chartMain) this.chartMain.destroy();

      const bgColors = [
        'rgba(59, 130, 246, 0.75)', 'rgba(99, 102, 241, 0.75)', 'rgba(168, 85, 247, 0.75)',
        'rgba(236, 72, 153, 0.75)', 'rgba(244, 63, 94, 0.75)', 'rgba(249, 115, 22, 0.75)',
        'rgba(234, 179, 8, 0.75)', 'rgba(16, 185, 129, 0.75)', 'rgba(20, 184, 166, 0.75)',
        'rgba(6, 182, 212, 0.75)', 'rgba(14, 165, 233, 0.75)'
      ];

      const borderColors = bgColors.map(c => c.replace('0.75', '1'));

      this.chartMain = new Chart(ctxMain, {
        type: this.chartConfig.type,
        data: {
          labels: mainData.labels,
          datasets: [{
            label: mainData.metric_label,
            data: mainData.values,
            backgroundColor: this.chartConfig.type === 'line' ? 'rgba(59, 130, 246, 0.15)' : bgColors,
            borderColor: this.chartConfig.type === 'line' ? '#3b82f6' : borderColors,
            borderWidth: 2,
            fill: this.chartConfig.type === 'line',
            tension: 0.35,
            borderRadius: this.chartConfig.type === 'bar' ? 6 : 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: ['doughnut', 'pie'].includes(this.chartConfig.type) },
            tooltip: {
              callbacks: {
                label: (ctx) => ` ${ctx.label}: ${Number(ctx.raw).toLocaleString('es-ES')}`
              }
            }
          },
          scales: ['doughnut', 'pie'].includes(this.chartConfig.type) ? {} : {
            y: {
              beginAtZero: true,
              grid: { color: '#f1f5f9' },
              ticks: { font: { size: 10 } }
            },
            x: {
              grid: { display: false },
              ticks: { font: { size: 10 }, maxRotation: 45 }
            }
          }
        }
      });

      // 2. Gráfico secundario (distribución de categoría o segundo numérico)
      const cols = this.currentDataset.columns_metadata;
      const otherCatCols = cols.filter(c => c.data_type === 'category' && c.clean_name !== this.chartConfig.dimension);
      const secDim = otherCatCols.length > 0 ? otherCatCols[0].clean_name : this.chartConfig.dimension;

      const secData = await API.getChartData(this.currentDataset.id, {
        dimension: secDim,
        metric: null, // Conteo de filas
        aggregation_func: 'count',
        filters: this.activeFilters,
        limit: 8
      });

      document.getElementById('secondary-chart-title').textContent = 
        `Distribución por ${secData.dimension_name}`;

      if (this.chartSecondary) this.chartSecondary.destroy();

      this.chartSecondary = new Chart(ctxSec, {
        type: 'doughnut',
        data: {
          labels: secData.labels,
          datasets: [{
            data: secData.values,
            backgroundColor: bgColors,
            borderWidth: 2,
            borderColor: '#ffffff'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'bottom', labels: { boxWidth: 10, font: { size: 10 } } }
          }
        }
      });

    } catch (err) {
      console.error("Error al renderizar gráficos:", err);
    }
  },

  async loadTableData() {
    const thead = document.getElementById('table-headers');
    const tbody = document.getElementById('table-body');
    const pageInfo = document.getElementById('table-page-info');

    tbody.innerHTML = '<tr><td colspan="100" class="py-8 text-center text-xs text-slate-400">Cargando registros...</td></tr>';

    try {
      const res = await API.getTableData(this.currentDataset.id, {
        filters: this.activeFilters,
        limit: this.tableState.limit,
        offset: (this.tableState.page - 1) * this.tableState.limit,
        sort_by: this.tableState.sortBy,
        sort_order: this.tableState.sortOrder
      });

      this.tableState.total = res.total;

      // Renderizar Encabezados con ordenamiento
      const cols = this.currentDataset.columns_metadata;
      thead.innerHTML = cols.map(c => {
        const isSorted = this.tableState.sortBy === c.clean_name;
        const arrow = isSorted 
          ? (this.tableState.sortOrder === 'asc' ? '▲' : '▼') 
          : '';

        return `
          <th 
            class="px-4 py-2.5 text-left text-[11px] font-semibold text-slate-600 uppercase tracking-wider bg-slate-50 border-b border-slate-200 cursor-pointer hover:bg-slate-100 transition-all select-none"
            onclick="Dashboard.sortTable('${c.clean_name}')"
          >
            <div class="flex items-center gap-1.5">
              <span>${c.name}</span>
              <span class="text-blue-600 text-xs">${arrow}</span>
            </div>
          </th>
        `;
      }).join('');

      // Renderizar Filas
      if (res.rows.length === 0) {
        tbody.innerHTML = '<tr><td colspan="100" class="py-8 text-center text-xs text-slate-400">No se encontraron registros con los filtros seleccionados.</td></tr>';
      } else {
        tbody.innerHTML = res.rows.map(row => `
          <tr class="hover:bg-slate-50/80 border-b border-slate-100 transition-all text-xs text-slate-700">
            ${cols.map(c => {
              const val = row[c.clean_name];
              const displayVal = (val === null || val === undefined) ? '<span class="text-slate-300">-</span>' : val;
              return `<td class="px-4 py-2.5 whitespace-nowrap">${displayVal}</td>`;
            }).join('')}
          </tr>
        `).join('');
      }

      // Actualizar información de paginación
      const start = res.total === 0 ? 0 : (this.tableState.page - 1) * this.tableState.limit + 1;
      const end = Math.min(this.tableState.page * this.tableState.limit, res.total);
      pageInfo.textContent = `Mostrando ${start} - ${end} de ${res.total.toLocaleString()} registros`;

      // Habilitar/deshabilitar botones de paginación
      document.getElementById('table-prev-btn').disabled = this.tableState.page <= 1;
      document.getElementById('table-next-btn').disabled = this.tableState.page >= res.pages;

    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="100" class="py-8 text-center text-xs text-red-500">Error: ${err.message}</td></tr>`;
    }
  },

  sortTable(colCleanName) {
    if (this.tableState.sortBy === colCleanName) {
      this.tableState.sortOrder = this.tableState.sortOrder === 'asc' ? 'desc' : 'asc';
    } else {
      this.tableState.sortBy = colCleanName;
      this.tableState.sortOrder = 'asc';
    }
    this.tableState.page = 1;
    this.loadTableData();
  },

  async saveCurrentConfiguration() {
    if (!this.currentDataset) return;
    
    const configToSave = {
      chart: this.chartConfig,
      saved_filters: Filters.activeFilters
    };

    try {
      await API.saveConfig(this.currentDataset.id, configToSave);
      this.currentDataset.custom_config = configToSave;
      window.App.showNotification('Configuración de vista guardada como predeterminada para este archivo.', 'success');
      document.getElementById('customizer-modal').classList.add('hidden');
    } catch (err) {
      window.App.showNotification(`Error al guardar configuración: ${err.message}`, 'error');
    }
  }
};
