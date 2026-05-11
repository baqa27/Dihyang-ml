const API_BASE = '/api'

async function fetchJSON(url, options = {}) {
  try {
    const res = await fetch(`${API_BASE}${url}`, {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      ...options,
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    return await res.json()
  } catch (err) {
    console.error(`API Error [${url}]:`, err)
    throw err
  }
}

// Weather APIs
export const weatherAPI = {
  getCurrent: () => fetchJSON('/weather/current'),
  getForecast: () => fetchJSON('/weather/forecast'),
  getHistorical: (days = 30) => fetchJSON(`/weather/historical?days=${days}`),
}

// Chat API (DITA)
export const chatAPI = {
  sendMessage: (message, history = []) =>
    fetchJSON('/chat', {
      method: 'POST',
      body: JSON.stringify({ message, history }),
    }),
}

// Destinations API
export const destinationsAPI = {
  getAll: () => fetchJSON('/destinations'),
  getById: (id) => fetchJSON(`/destinations/${id}`),
}

// Routes API
export const routesAPI = {
  getAll: () => fetchJSON('/routes'),
  getSafe: (vehicleType = 'car') => fetchJSON(`/routes/safe?vehicle=${vehicleType}`),
}

// Costs/Retribution API
export const costsAPI = {
  getAll: () => fetchJSON('/costs'),
}

// Accommodations API
export const accommodationsAPI = {
  getAll: () => fetchJSON('/accommodations'),
}

// Itinerary API
export const itineraryAPI = {
  generate: (preferences) =>
    fetchJSON('/itinerary/generate', {
      method: 'POST',
      body: JSON.stringify(preferences),
    }),
}

// ML Predictions API (DITA AI Engine)
export const mlAPI = {
  getQuickPrediction: () => fetchJSON('/ml/predict/quick'),
  getModelInfo: () => fetchJSON('/ml/model-info'),
  predictTemperature: (data) =>
    fetchJSON('/ml/predict/temperature', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  predictRain: (data) =>
    fetchJSON('/ml/predict/rain', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  predictRisk: (data) =>
    fetchJSON('/ml/predict/risk', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  predictRouteSafety: (data) =>
    fetchJSON('/ml/predict/route-safety', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
}

