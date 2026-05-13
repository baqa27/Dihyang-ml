const API_BASE = '/api'
const WS_BASE = 'ws://localhost:8000/api'

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

// WebSocket Manager untuk realtime updates
class RealtimeManager {
  constructor(endpoint) {
    this.endpoint = endpoint
    this.ws = null
    this.listeners = []
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectDelay = 3000
  }

  connect() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      return Promise.resolve()
    }

    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(`${WS_BASE}${this.endpoint}`)

        this.ws.onopen = () => {
          console.log(`[WebSocket] Connected to ${this.endpoint}`)
          this.reconnectAttempts = 0
          resolve()
        }

        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            this.listeners.forEach(listener => listener(data))
          } catch (err) {
            console.error('[WebSocket] Parse error:', err)
          }
        }

        this.ws.onerror = (error) => {
          console.error(`[WebSocket] Error on ${this.endpoint}:`, error)
          reject(error)
        }

        this.ws.onclose = () => {
          console.log(`[WebSocket] Disconnected from ${this.endpoint}`)
          this.attemptReconnect()
        }
      } catch (err) {
        reject(err)
      }
    })
  }

  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`[WebSocket] Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
      setTimeout(() => this.connect(), this.reconnectDelay)
    } else {
      console.error('[WebSocket] Max reconnect attempts reached')
    }
  }

  subscribe(callback) {
    this.listeners.push(callback)
    return () => {
      this.listeners = this.listeners.filter(l => l !== callback)
    }
  }

  send(message) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(typeof message === 'string' ? message : JSON.stringify(message))
    }
  }

  requestLatest() {
    this.send('get_latest')
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }
}

// Realtime API instances
export const realtimeAPI = {
  weather: new RealtimeManager('/realtime/ws/weather'),
  predictions: new RealtimeManager('/realtime/ws/predictions'),
  dashboard: new RealtimeManager('/realtime/ws/dashboard'),
  
  getStatus: () => fetchJSON('/realtime/status'),
}

// Weather APIs
export const weatherAPI = {
  getCurrent:   () => fetchJSON('/weather/current'),
  getForecast:  () => fetchJSON('/weather/forecast'),
  getHourlyToday: () => fetchJSON('/weather/hourly-today'),
  getHistorical: () => fetchJSON('/weather/historical'),
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
  generate: (preferences) => {
    console.log('[API] Generating itinerary with preferences:', preferences)
    return fetchJSON('/itinerary/generate', {
      method: 'POST',
      body: JSON.stringify(preferences),
    })
  },
}

// ML Predictions API (DITA AI Engine)
export const mlAPI = {
  // Dashboard endpoint - format sederhana untuk frontend
  getDashboardPredictions: () => fetchJSON('/ml/predict/dashboard'),
  
  // Quick prediction - format lengkap
  getQuickPrediction: () => fetchJSON('/ml/predict/quick'),
  
  // Model info
  getModelInfo: () => fetchJSON('/ml/model-info'),
  
  // Individual predictions
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


