/**
 * API Service Layer
 * 
 * Centralized service for all API calls.
 * Provides type-safe methods and consistent error handling.
 */

import { API_ENDPOINTS, apiFetch, APIError } from '@/config/api';

export class APIService {
  private static instance: APIService;
  
  private constructor() {}
  
  static getInstance(): APIService {
    if (!APIService.instance) {
      APIService.instance = new APIService();
    }
    return APIService.instance;
  }
  
  // =============================================================================
  // Weather APIs
  // =============================================================================
  
  async getCurrentWeather() {
    try {
      return await apiFetch<any>(API_ENDPOINTS.weather.current);
    } catch (error) {
      console.error('Error fetching current weather:', error);
      throw error;
    }
  }
  
  async getForecast() {
    try {
      return await apiFetch<any>(API_ENDPOINTS.weather.forecast);
    } catch (error) {
      console.error('Error fetching forecast:', error);
      throw error;
    }
  }
  
  async getHourlyToday() {
    try {
      return await apiFetch<any>(API_ENDPOINTS.weather.hourly);
    } catch (error) {
      console.error('Error fetching hourly data:', error);
      throw error;
    }
  }
  
  // =============================================================================
  // ML Prediction APIs
  // =============================================================================
  
  async getDashboardPredictions() {
    try {
      return await apiFetch<any>(API_ENDPOINTS.ml.dashboard);
    } catch (error) {
      console.error('Error fetching dashboard predictions:', error);
      throw error;
    }
  }
  
  async getQuickPrediction() {
    try {
      return await apiFetch<any>(API_ENDPOINTS.ml.quick);
    } catch (error) {
      console.error('Error fetching quick prediction:', error);
      throw error;
    }
  }
  
  // =============================================================================
  // Chat API
  // =============================================================================
  
  async sendChatMessage(message: string, history: any[] = []) {
    try {
      return await apiFetch<any>(API_ENDPOINTS.chat, {
        method: 'POST',
        body: JSON.stringify({ message, history }),
      });
    } catch (error) {
      console.error('Error sending chat message:', error);
      
      // Provide user-friendly error messages
      if (error instanceof APIError) {
        if (error.statusCode === 429) {
          throw new APIError(
            'Terlalu banyak permintaan. Silakan tunggu sebentar dan coba lagi.',
            429,
            'rate_limit_exceeded'
          );
        } else if (error.statusCode === 422) {
          throw new APIError(
            'Pesan tidak valid. Pastikan pesan Anda tidak terlalu panjang atau mengandung karakter khusus.',
            422,
            'validation_error'
          );
        }
      }
      
      throw error;
    }
  }
  
  // =============================================================================
  // Itinerary API
  // =============================================================================
  
  async generateItinerary(data: {
    destination: string;
    duration: number;
    travelStyle: string;
    budget: number;
    guests: number;
    interests: string[];
    vehicle: string;
  }) {
    try {
      return await apiFetch<any>(API_ENDPOINTS.itinerary.generate, {
        method: 'POST',
        body: JSON.stringify(data),
      });
    } catch (error) {
      console.error('Error generating itinerary:', error);
      
      // Provide user-friendly error messages
      if (error instanceof APIError) {
        if (error.statusCode === 422) {
          throw new APIError(
            'Data itinerary tidak valid. Periksa kembali input Anda.',
            422,
            'validation_error',
            error.details
          );
        } else if (error.statusCode === 503) {
          throw new APIError(
            'Layanan AI sedang sibuk. Silakan coba lagi dalam beberapa saat.',
            503,
            'service_unavailable'
          );
        }
      }
      
      throw error;
    }
  }
  
  // =============================================================================
  // Destinations API
  // =============================================================================
  
  async getDestinations() {
    try {
      return await apiFetch<any>(API_ENDPOINTS.destinations);
    } catch (error) {
      console.error('Error fetching destinations:', error);
      throw error;
    }
  }
  
  // =============================================================================
  // Realtime API
  // =============================================================================
  
  async getRealtimeStatus() {
    try {
      return await apiFetch<any>(API_ENDPOINTS.realtime.status);
    } catch (error) {
      console.error('Error fetching realtime status:', error);
      throw error;
    }
  }
  
  // =============================================================================
  // Health Check
  // =============================================================================
  
  async healthCheck() {
    try {
      return await apiFetch<any>(API_ENDPOINTS.health);
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }

}

// Export singleton instance
export const apiService = APIService.getInstance();
