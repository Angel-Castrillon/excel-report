/**
 * Módulo de filtros dinámicos adaptativos.
 * Detecta los tipos de columnas del dataset activo y genera los controles de filtrado.
 */
const Filters = {
  currentDataset: null,
  filterOptions: {},
  activeFilters: [],

  async initForDataset(dataset) {
    this.currentDataset = dataset;
    this.activeFilters = [];
    
    // Obtener valores únicos y rangos desde el backend
    try {
      this.filterOptions = await API.getFilterOptions(dataset.id);
      this.renderFilterControls();
      this.loadSavedConfig();
    } catch (err) {
      console.error("Error al cargar opciones de filtro:", err);
    }
  },

  renderFilterControls() {
    const container = document.getElementById('dynamic-filters-container');
    const cols = this.currentDataset.columns_metadata;

    if (!cols || cols.length === 0) {
      container.innerHTML = '<p class="text-xs text-slate-400">No hay columnas disponibles para filtrar.</p>';
      return;
    }

    // Filtrar columnas relevantes para la barra de filtros rápidos (fechas, categorías y numéricos)
    const filterableCols = cols.filter(c => ['date', 'category', 'numeric'].includes(c.data_type));
    
    if (filterableCols.length === 0) {
      container.innerHTML = '<p class="text-xs text-slate-400">Este archivo no contiene columnas categóricas, numéricas o de fecha para filtrar.</p>';
      return;
    }

    container.innerHTML = filterableCols.map(col => {
      const opts = this.filterOptions[col.clean_name] || {};
      
      if (col.data_type === 'category') {
        const values = opts.values || [];
        return `
          <div class="flex flex-col gap-1 min-w-[170px] flex-1">
            <label class="text-[11px] font-semibold text-slate-600 flex items-center gap-1 truncate" title="${col.name}">
              <span class="w-1.5 h-1.5 rounded-full bg-purple-500 inline-block"></span>
              <span class="truncate">${col.name}</span>
            </label>
            <select 
              id="filter-${col.clean_name}"
              data-col="${col.clean_name}"
              data-type="category"
              class="w-full text-xs bg-white border border-slate-200 rounded-lg px-2.5 py-1.5 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none text-slate-700"
            >
              <option value="">(Todos)</option>
              ${values.map(v => `<option value="${v}">${v}</option>`).join('')}
            </select>
          </div>
        `;
      } else if (col.data_type === 'date') {
        return `
          <div class="flex flex-col gap-1 min-w-[240px] flex-1">
            <label class="text-[11px] font-semibold text-slate-600 flex items-center gap-1 truncate" title="${col.name}">
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 inline-block"></span>
              <span class="truncate">${col.name} (Rango)</span>
            </label>
            <div class="flex items-center gap-1">
              <input 
                type="date" 
                id="filter-${col.clean_name}-from"
                data-col="${col.clean_name}"
                data-type="date-from"
                class="w-full text-[11px] bg-white border border-slate-200 rounded-lg px-2 py-1 focus:ring-2 focus:ring-blue-500 outline-none text-slate-700"
              />
              <span class="text-xs text-slate-400">-</span>
              <input 
                type="date" 
                id="filter-${col.clean_name}-to"
                data-col="${col.clean_name}"
                data-type="date-to"
                class="w-full text-[11px] bg-white border border-slate-200 rounded-lg px-2 py-1 focus:ring-2 focus:ring-blue-500 outline-none text-slate-700"
              />
            </div>
          </div>
        `;
      } else if (col.data_type === 'numeric') {
        const minVal = opts.min !== undefined ? opts.min : '';
        const maxVal = opts.max !== undefined ? opts.max : '';
        return `
          <div class="flex flex-col gap-1 min-w-[200px] flex-1">
            <label class="text-[11px] font-semibold text-slate-600 flex items-center gap-1 truncate" title="${col.name}">
              <span class="w-1.5 h-1.5 rounded-full bg-blue-500 inline-block"></span>
              <span class="truncate">${col.name} (Mín - Máx)</span>
            </label>
            <div class="flex items-center gap-1">
              <input 
                type="number" 
                placeholder="Mín: ${minVal}"
                id="filter-${col.clean_name}-min"
                data-col="${col.clean_name}"
                data-type="num-min"
                class="w-full text-[11px] bg-white border border-slate-200 rounded-lg px-2 py-1 focus:ring-2 focus:ring-blue-500 outline-none text-slate-700"
              />
              <span class="text-xs text-slate-400">-</span>
              <input 
                type="number" 
                placeholder="Máx: ${maxVal}"
                id="filter-${col.clean_name}-max"
                data-col="${col.clean_name}"
                data-type="num-max"
                class="w-full text-[11px] bg-white border border-slate-200 rounded-lg px-2 py-1 focus:ring-2 focus:ring-blue-500 outline-none text-slate-700"
              />
            </div>
          </div>
        `;
      }
      return '';
    }).join('');

    // Escuchar cambios en los inputs para aplicar automáticamente o vía botón
    container.querySelectorAll('select, input').forEach(input => {
      input.addEventListener('change', () => this.applyFilters());
    });
  },

  getFiltersFromUI() {
    const filters = [];
    const container = document.getElementById('dynamic-filters-container');
    if (!container) return filters;

    // 1. Categorías (selects)
    container.querySelectorAll('select[data-type="category"]').forEach(sel => {
      if (sel.value) {
        filters.push({
          column: sel.dataset.col,
          operator: 'eq',
          value: sel.value
        });
      }
    });

    // 2. Fechas (between o gte / lte)
    const dateCols = new Set();
    container.querySelectorAll('input[data-type^="date-"]').forEach(inp => dateCols.add(inp.dataset.col));
    
    dateCols.forEach(col => {
      const fromInp = document.getElementById(`filter-${col}-from`);
      const toInp = document.getElementById(`filter-${col}-to`);
      const fromVal = fromInp ? fromInp.value : '';
      const toVal = toInp ? toInp.value : '';

      if (fromVal && toVal) {
        filters.push({
          column: col,
          operator: 'between',
          value: [fromVal, toVal]
        });
      } else if (fromVal) {
        filters.push({
          column: col,
          operator: 'gte',
          value: fromVal
        });
      } else if (toVal) {
        filters.push({
          column: col,
          operator: 'lte',
          value: toVal
        });
      }
    });

    // 3. Numéricos (min / max)
    const numCols = new Set();
    container.querySelectorAll('input[data-type^="num-"]').forEach(inp => numCols.add(inp.dataset.col));

    numCols.forEach(col => {
      const minInp = document.getElementById(`filter-${col}-min`);
      const maxInp = document.getElementById(`filter-${col}-max`);
      const minVal = minInp && minInp.value !== '' ? parseFloat(minInp.value) : null;
      const maxVal = maxInp && maxInp.value !== '' ? parseFloat(maxInp.value) : null;

      if (minVal !== null && maxVal !== null) {
        filters.push({
          column: col,
          operator: 'between',
          value: [minVal, maxVal]
        });
      } else if (minVal !== null) {
        filters.push({
          column: col,
          operator: 'gte',
          value: minVal
        });
      } else if (maxVal !== null) {
        filters.push({
          column: col,
          operator: 'lte',
          value: maxVal
        });
      }
    });

    return filters;
  },

  applyFilters() {
    this.activeFilters = this.getFiltersFromUI();
    const activeBadge = document.getElementById('active-filters-count');
    if (activeBadge) {
      activeBadge.textContent = `${this.activeFilters.length}`;
      activeBadge.classList.toggle('hidden', this.activeFilters.length === 0);
    }
    window.App.onFiltersChanged(this.activeFilters);
  },

  clearFilters() {
    const container = document.getElementById('dynamic-filters-container');
    if (!container) return;

    container.querySelectorAll('select').forEach(s => s.value = '');
    container.querySelectorAll('input').forEach(i => i.value = '');
    this.applyFilters();
  },

  loadSavedConfig() {
    if (!this.currentDataset || !this.currentDataset.custom_config) return;
    const config = this.currentDataset.custom_config;
    
    // Si hay filtros guardados
    if (config.saved_filters && Array.isArray(config.saved_filters)) {
      config.saved_filters.forEach(f => {
        if (f.operator === 'eq') {
          const sel = document.getElementById(`filter-${f.column}`);
          if (sel) sel.value = f.value;
        } else if (f.operator === 'between' && Array.isArray(f.value)) {
          const fromInp = document.getElementById(`filter-${f.column}-from`);
          const toInp = document.getElementById(`filter-${f.column}-to`);
          if (fromInp && toInp) {
            fromInp.value = f.value[0];
            toInp.value = f.value[1];
          }
        }
      });
      this.activeFilters = this.getFiltersFromUI();
    }
  }
};
