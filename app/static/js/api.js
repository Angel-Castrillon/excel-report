/**
 * Cliente API para la aplicación Excel Report Dashboard.
 * Centraliza las llamadas HTTP fetch a los endpoints locales de FastAPI.
 */
const API = {
  baseUrl: '/api',

  async listDatasets() {
    const res = await fetch(`${this.baseUrl}/datasets`);
    if (!res.ok) throw new Error('Error al obtener la lista de datasets');
    return await res.json();
  },

  async getDataset(id) {
    const res = await fetch(`${this.baseUrl}/datasets/${id}`);
    if (!res.ok) throw new Error(`Error al obtener el dataset ${id}`);
    return await res.json();
  },

  async uploadDataset(file, onProgress) {
    const formData = new FormData();
    formData.append('file', file);

    const res = await fetch(`${this.baseUrl}/datasets/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Error al subir el archivo Excel');
    }
    return await res.json();
  },

  async deleteDataset(id) {
    const res = await fetch(`${this.baseUrl}/datasets/${id}`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error('Error al eliminar el dataset');
    return await res.json();
  },

  async saveConfig(id, customConfig) {
    const res = await fetch(`${this.baseUrl}/datasets/${id}/config`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ custom_config: customConfig }),
    });
    if (!res.ok) throw new Error('Error al guardar la configuración');
    return await res.json();
  },

  async getFilterOptions(id) {
    const res = await fetch(`${this.baseUrl}/datasets/${id}/filter-options`);
    if (!res.ok) throw new Error('Error al obtener opciones de filtro');
    return await res.json();
  },

  async getKPIs(id, filters = []) {
    const res = await fetch(`${this.baseUrl}/datasets/${id}/kpis`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(filters),
    });
    if (!res.ok) throw new Error('Error al calcular los KPIs');
    return await res.json();
  },

  async getTableData(id, queryRequest) {
    const res = await fetch(`${this.baseUrl}/datasets/${id}/table`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(queryRequest),
    });
    if (!res.ok) throw new Error('Error al consultar datos de la tabla');
    return await res.json();
  },

  async getChartData(id, aggregationRequest) {
    const res = await fetch(`${this.baseUrl}/datasets/${id}/chart`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(aggregationRequest),
    });
    if (!res.ok) throw new Error('Error al obtener datos del gráfico');
    return await res.json();
  },
};
