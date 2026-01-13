import axios, { AxiosInstance } from 'axios';
import { Task, TaskCreateData, TaskUpdateData } from '@/types/task';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor to include JWT token
    // Note: Token will be added by the calling functions that have access to the auth context
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Redirect to login on 401
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  get(path: string, params?: any, token?: string) {
    const config = token ? { params, headers: { Authorization: `Bearer ${token}` } } : { params };
    return this.client.get(path, config);
  }

  post(path: string, data?: any, token?: string) {
    const config = token ? { headers: { Authorization: `Bearer ${token}` } } : {};
    return this.client.post(path, data, config);
  }

  put(path: string, data?: any, token?: string) {
    const config = token ? { headers: { Authorization: `Bearer ${token}` } } : {};
    return this.client.put(path, data, config);
  }

  patch(path: string, data?: any, token?: string) {
    const config = token ? { headers: { Authorization: `Bearer ${token}` } } : {};
    return this.client.patch(path, data, config);
  }

  delete(path: string, token?: string) {
    const config = token ? { headers: { Authorization: `Bearer ${token}` } } : {};
    return this.client.delete(path, config);
  }
}

const apiClient = new ApiClient();

// These functions need to be called with the token from the auth context
export class TaskApi {
  static async getTasks(userId: string, token: string, params?: any) {
    const response = await apiClient.get(`/users/${userId}/tasks`, params, token);
    return response.data.tasks as Task[];
  }

  static async getTask(userId: string, taskId: string, token: string) {
    const response = await apiClient.get(`/users/${userId}/tasks/${taskId}`, undefined, token);
    return response.data as Task;
  }

  static async createTask(userId: string, taskData: TaskCreateData, token: string) {
    const response = await apiClient.post(`/users/${userId}/tasks`, taskData, token);
    return response.data as Task;
  }

  static async updateTask(userId: string, taskId: string, taskData: TaskUpdateData, token: string) {
    const response = await apiClient.put(`/users/${userId}/tasks/${taskId}`, taskData, token);
    return response.data as Task;
  }

  static async deleteTask(userId: string, taskId: string, token: string) {
    await apiClient.delete(`/users/${userId}/tasks/${taskId}`, token);
  }

  static async toggleTaskCompletion(userId: string, taskId: string, complete: boolean, token: string) {
    const response = await apiClient.patch(`/users/${userId}/tasks/${taskId}/complete`, { complete }, token);
    return response.data as Task;
  }
}