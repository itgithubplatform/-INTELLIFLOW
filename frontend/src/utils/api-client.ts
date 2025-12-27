import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { apiConfig } from '@/config/api.config';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
    baseURL: apiConfig.baseUrl,
    timeout: 30000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
    (config) => {
        // Get token from session storage or Descope SDK
        const token = typeof window !== 'undefined'
            ? sessionStorage.getItem('DS_SESSION_TOKEN')
            : null;

        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }

        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
        if (error.response?.status === 401) {
            // Token expired - redirect to login
            if (typeof window !== 'undefined') {
                window.location.href = '/auth/signin';
            }
        }
        return Promise.reject(error);
    }
);

export default apiClient;

// Type-safe request helpers
export const api = {
    get: <T>(url: string, config?: AxiosRequestConfig) =>
        apiClient.get<T>(url, config).then((res) => res.data),

    post: <T>(url: string, data?: unknown, config?: AxiosRequestConfig) =>
        apiClient.post<T>(url, data, config).then((res) => res.data),

    put: <T>(url: string, data?: unknown, config?: AxiosRequestConfig) =>
        apiClient.put<T>(url, data, config).then((res) => res.data),

    delete: <T>(url: string, config?: AxiosRequestConfig) =>
        apiClient.delete<T>(url, config).then((res) => res.data),
};
