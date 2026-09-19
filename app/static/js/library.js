/**
 * Módulo de la biblioteca de datasets guardados.
 * Gestiona el listado histórico, selección, subida de nuevos archivos y eliminación (CRUD).
 */
const Library = {
  datasets: [],
  activeDatasetId: null,
  filterText: '',

  init() {
    this.bindEvents();
    this.loadDatasets();
  },

  bindEvents() {
    const fileInput = document.getElementById('file-upload-input');
    const dropZone = document.getElementById('drop-zone');
    const searchInput = document.getElementById('library-search-input');

    // Subida mediante input file
    fileInput.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (file) this.handleUpload(file);
      fileInput.value = ''; // Reset
    });

    // Drag and drop
    ['dragenter', 'dragover'].forEach(name => {
      dropZone.addEventListener(name, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.add('dragover');
      });
    });

    ['dragleave', 'drop'].forEach(name => {
      dropZone.addEventListener(name, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove('dragover');
      });
    });

    dropZone.addEventListener('drop', (e) => {
      const file = e.dataTransfer.files[0];
      if (file) this.handleUpload(file);
    });

    // Búsqueda en la biblioteca
    searchInput.addEventListener('input', (e) => {
      this.filterText = e.target.value.toLowerCase().trim();
      this.render();
    });
  },

  async loadDatasets(selectFirstIfNoneActive = true) {
    const listContainer = document.getElementById('library-list');
    listContainer.innerHTML = '<div class="p-4 text-center text-xs text-slate-400">Cargando biblioteca...</div>';
    
    try {
      this.datasets = await API.listDatasets();
      this.render();

      if (this.datasets.length > 0) {
        if (!this.activeDatasetId || !this.datasets.some(d => d.id === this.activeDatasetId)) {
          if (selectFirstIfNoneActive) {
            this.selectDataset(this.datasets[0].id);
          }
        }
      } else {
        this.activeDatasetId = null;
        window.App.onNoDatasetSelected();
      }
    } catch (err) {
      listContainer.innerHTML = `<div class="p-4 text-center text-xs text-red-500">Error: ${err.message}</div>`;
    }
  },

  render() {
    const listContainer = document.getElementById('library-list');
    const countBadge = document.getElementById('library-count-badge');
    
    countBadge.textContent = `${this.datasets.length}`;

    const filtered = this.datasets.filter(d => 
      d.original_filename.toLowerCase().includes(this.filterText)
    );

    if (filtered.length === 0) {
      if (this.datasets.length === 0) {
        listContainer.innerHTML = `
          <div class="py-8 px-4 text-center text-slate-400">
            <svg class="mx-auto h-8 w-8 text-slate-300 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p class="text-xs font-medium">No hay archivos cargados aún</p>
            <p class="text-[11px] text-slate-400 mt-1">Sube un Excel para comenzar el análisis</p>
          </div>
        `;
      } else {
        listContainer.innerHTML = `
          <div class="py-6 text-center text-xs text-slate-400">
            No se encontraron archivos con "${this.filterText}"
          </div>
        `;
      }
      return;
    }

    listContainer.innerHTML = filtered.map(d => {
      const isActive = d.id === this.activeDatasetId;
      const formattedDate = new Date(d.created_at).toLocaleDateString('es-ES', {
        day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit'
      });

      return `
        <div class="group relative flex items-center justify-between p-3 rounded-xl border transition-all cursor-pointer ${
          isActive 
            ? 'bg-blue-50/80 border-blue-300 shadow-sm text-blue-900' 
            : 'bg-white border-slate-200/80 hover:border-slate-300 hover:bg-slate-50/70 text-slate-700'
        }" onclick="Library.selectDataset(${d.id})">
          <div class="flex items-start gap-3 min-w-0 flex-1">
            <div class="p-2 rounded-lg ${isActive ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-500 group-hover:bg-slate-200'}">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div class="min-w-0 flex-1">
              <p class="text-xs font-semibold truncate ${isActive ? 'text-blue-900' : 'text-slate-800'}">
                ${d.original_filename}
              </p>
              <div class="flex items-center gap-2 mt-1 text-[11px] text-slate-400">
                <span>${d.row_count.toLocaleString()} filas</span>
                <span>•</span>
                <span>${d.file_size_human}</span>
                <span>•</span>
                <span>${formattedDate}</span>
              </div>
            </div>
          </div>
          <button 
            type="button"
            title="Eliminar archivo"
            onclick="event.stopPropagation(); Library.confirmDelete(${d.id}, '${encodeURIComponent(d.original_filename)}')"
            class="opacity-0 group-hover:opacity-100 p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      `;
    }).join('');
  },

  async handleUpload(file) {
    const dropZone = document.getElementById('drop-zone');
    const uploadStatus = document.getElementById('upload-status');
    
    // Validar extensión
    const ext = '.' + file.name.split('.').pop().toLowerCase();
    if (!['.xlsx', '.xls'].includes(ext)) {
      window.App.showNotification('Solo se permiten archivos Excel (.xlsx o .xls)', 'error');
      return;
    }

    uploadStatus.classList.remove('hidden');
    uploadStatus.innerHTML = `
      <div class="flex items-center gap-2 text-xs text-blue-700 font-medium">
        <svg class="animate-spin h-3.5 w-3.5 text-blue-600" viewBox="0 0 24 24" fill="none">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span>Procesando y extrayendo "${file.name}"...</span>
      </div>
    `;

    try {
      const created = await API.uploadDataset(file);
      window.App.showNotification(`¡Archivo "${file.name}" cargado y analizado con éxito!`, 'success');
      await this.loadDatasets(false);
      this.selectDataset(created.id);
    } catch (err) {
      window.App.showNotification(err.message, 'error');
    } finally {
      uploadStatus.classList.add('hidden');
      uploadStatus.innerHTML = '';
    }
  },

  selectDataset(id) {
    if (this.activeDatasetId === id) return;
    this.activeDatasetId = id;
    this.render();
    window.App.onDatasetSelected(id);
  },

  confirmDelete(id, encodedFilename) {
    const filename = decodeURIComponent(encodedFilename);
    const modal = document.getElementById('delete-modal');
    const filenameSpan = document.getElementById('delete-modal-filename');
    const confirmBtn = document.getElementById('delete-modal-confirm-btn');

    filenameSpan.textContent = filename;
    modal.classList.remove('hidden');

    // Asignar acción al botón de confirmar
    confirmBtn.onclick = async () => {
      modal.classList.add('hidden');
      try {
        await API.deleteDataset(id);
        window.App.showNotification(`Dataset "${filename}" eliminado correctamente.`, 'info');
        
        // Si el dataset eliminado era el activo, resetear
        if (this.activeDatasetId === id) {
          this.activeDatasetId = null;
        }
        await this.loadDatasets(true);
      } catch (err) {
        window.App.showNotification(err.message, 'error');
      }
    };
  }
};
