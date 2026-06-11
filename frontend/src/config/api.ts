/**
 * Centralized API Configuration
 * 
 * Single source of truth for all backend API endpoints.
 * Use environment variable VITE_API_URL to switch between environments.
 * 
 * Usage:
 *   import { API_ENDPOINTS, apiService } from '@/config/api';
 *   const data = await apiService.getCurrentWeather();
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const WS_BASE_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8000";
const WS_TOKEN = import.meta.env.VITE_WS_TOKEN || "";
const ENVIRONMENT = import.meta.env.VITE_ENVIRONMENT || "development";

// Validate configuration on load
if (ENVIRONMENT === "production" && API_BASE_URL.includes("localhost")) {
  console.warn("⚠️ Warning: Using localhost URL in production environment!");
}

export const API_ENDPOINTS = {
  // Weather endpoints
  weather: {
    current: `${API_BASE_URL}/api/weather/current`,
    forecast: `${API_BASE_URL}/api/weather/forecast`,
    hourly: `${API_BASE_URL}/api/weather/hourly-today`,
    historical: `${API_BASE_URL}/api/weather/historical`,
  },

  // ML Prediction endpoints
  ml: {
    dashboard: `${API_BASE_URL}/api/ml/predict/dashboard`,
    quick: `${API_BASE_URL}/api/ml/predict/quick`,
    temperature: `${API_BASE_URL}/api/ml/predict/temperature`,
    rain: `${API_BASE_URL}/api/ml/predict/rain`,
    risk: `${API_BASE_URL}/api/ml/predict/risk`,
    routeSafety: `${API_BASE_URL}/api/ml/predict/route-safety`,
    modelInfo: `${API_BASE_URL}/api/ml/model-info`,
  },

  // Itinerary endpoints
  itinerary: {
    generate: `${API_BASE_URL}/api/itinerary/generate`,
    generateSmart: `${API_BASE_URL}/api/itinerary/generate-smart`,
    activities: `${API_BASE_URL}/api/itinerary/activities`,
  },

  // Chat endpoint
  chat: `${API_BASE_URL}/api/chat`,

  // Destinations endpoint
  destinations: `${API_BASE_URL}/api/destinations`,

  // Realtime endpoints
  realtime: {
    status: `${API_BASE_URL}/api/realtime/status`,
    retrain: `${API_BASE_URL}/api/realtime/retrain`,
    wsWeather: `${WS_BASE_URL}/api/realtime/ws/weather${WS_TOKEN ? `?token=${WS_TOKEN}` : ''}`,
    wsPredictions: `${WS_BASE_URL}/api/realtime/ws/predictions${WS_TOKEN ? `?token=${WS_TOKEN}` : ''}`,
    wsDashboard: `${WS_BASE_URL}/api/realtime/ws/dashboard${WS_TOKEN ? `?token=${WS_TOKEN}` : ''}`,
  },
  
  // Health check
  health: `${API_BASE_URL}/health`,
};

// Export base URLs for custom endpoints
export { API_BASE_URL, WS_BASE_URL, WS_TOKEN, ENVIRONMENT };

/**
 * Custom API Error class for better error handling
 */
export class APIError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public errorType?: string,
    public details?: any
  ) {
    super(message);
    this.name = 'APIError';
  }
}

/**
 * Helper function for fetch with error handling
 * @throws {APIError} When request fails or validation errors occur
 */
export async function apiFetch<T>(
  url: string,
  options?: RequestInit
): Promise<T> {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    // Try to parse response as JSON
    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new APIError(
        data.message || `HTTP ${response.status}: ${response.statusText}`,
        response.status,
        data.error,
        data.details
      );
    }

    return data;
  } catch (error) {
    // If it's already an APIError, rethrow it
    if (error instanceof APIError) {
      throw error;
    }
    
    // Network error or other unexpected error
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new APIError(
        'Tidak dapat terhubung ke server. Pastikan backend berjalan di ' + API_BASE_URL,
        0,
        'network_error'
      );
    }
    
    // Unknown error
    throw new APIError(
      error instanceof Error ? error.message : 'Terjadi kesalahan yang tidak diketahui',
      0,
      'unknown_error'
    );
  }
}
