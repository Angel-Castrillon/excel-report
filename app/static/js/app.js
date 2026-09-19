/**
 * Orquestador principal de la aplicación frontend SPA.
 * Maneja eventos globales, estado activo y notificaciones de interfaz.
 */
window.App = {
  currentDataset: null,

  init() {
    Library.init();
    Dashboard.init();
    this.bindGlobalModals();
  },

  bindGlobalModals() {
    // Modal de Personalización de Gráficos
    const customizerModal = document.getElementById('customizer-modal');
    const openCustomizerBtn = document.getElementById('open-customizer-btn');
    const closeCustomizerBtn = document.getElementById('close-customizer-btn');

    openCustomizerBtn.addEventListener('click', () => {
      if (!this.currentDataset) return;
      customizerModal.classList.remove('hidden');
    });

    closeCustomizerBtn.addEventListener('click', () => {
      customizerModal.classList.add('hidden');
    });

    // Modal de Eliminación
    const deleteModal = document.getElementById('delete-modal');
    const cancelDeleteBtn = document.getElementById('delete-modal-cancel-btn');
    cancelDeleteBtn.addEventListener('click', () => {
      deleteModal.classList.add('hidden');
    });

    // Cerrar modales haciendo click fuera del diálogo
    [customizerModal, deleteModal].forEach(modal => {
      modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.classList.add('hidden');
      });
    });

    // Botón de limpiar filtros
    document.getElementById('clear-filters-btn').addEventListener('click', () => {
      Filters.clearFilters();
    });
  },

  async onDatasetSelected(datasetId) {
    document.getElementById('empty-state-view').classList.add('hidden');
    document.getElementById('dashboard-view').classList.remove('hidden');

    try {
      this.currentDataset = await API.getDataset(datasetId);
      await Filters.initForDataset(this.currentDataset);
      await Dashboard.loadDataset(this.currentDataset);
    } catch (err) {
      this.showNotification(`Error al cargar dataset: ${err.message}`, 'error');
    }
  },

  onNoDatasetSelected() {
    this.currentDataset = null;
    document.getElementById('dashboard-view').classList.add('hidden');
    document.getElementById('empty-state-view').classList.remove('hidden');
  },

  onFiltersChanged(activeFilters) {
    Dashboard.updateFilters(activeFilters);
  },

  showNotification(message, type = 'info') {
    const toast = document.getElementById('toast-notification');
    const toastText = document.getElementById('toast-message');
    const toastIcon = document.getElementById('toast-icon');

    toastText.textContent = message;

    // Colores e iconos según tipo
    if (type === 'success') {
      toast.className = 'fixed bottom-6 right-6 z-50 flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg border text-xs font-medium bg-emerald-50 border-emerald-200 text-emerald-800 transition-all';
      toastIcon.innerHTML = `
        <svg class="w-4 h-4 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
      `;
    } else if (type === 'error') {
      toast.className = 'fixed bottom-6 right-6 z-50 flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg border text-xs font-medium bg-red-50 border-red-200 text-red-800 transition-all';
      toastIcon.innerHTML = `
        <svg class="w-4 h-4 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      `;
    } else {
      toast.className = 'fixed bottom-6 right-6 z-50 flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg border text-xs font-medium bg-blue-50 border-blue-200 text-blue-800 transition-all';
      toastIcon.innerHTML = `
        <svg class="w-4 h-4 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      `;
    }

    toast.classList.remove('hidden', 'translate-y-4', 'opacity-0');

    // Ocultar automáticamente tras 4 segundos
    clearTimeout(this._toastTimeout);
    this._toastTimeout = setTimeout(() => {
      toast.classList.add('hidden');
    }, 4000);
  }
};

// Iniciar aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
  window.App.init();
});
