/**
 * Centralized API Client for CardioPulse FastAPI Backend.
 *
 * Automatically injects verified Firebase Bearer ID tokens for authenticated requests.
 * Normalizes HTTP status codes into structured ApiError instances without leaking stack traces.
 */

import { auth } from './firebase';
import { ApiError, type ApiErrorCategory, type RequestOptions } from '../types/api';

const env: Record<string, string | undefined> =
  (typeof import.meta !== 'undefined' && (import.meta as { env?: Record<string, string | undefined> }).env) ||
  (typeof process !== 'undefined' && process.env) ||
  {};

const BASE_URL = (env.VITE_API_BASE_URL || '').replace(/\/$/, '');

function categorizeStatus(status: number): ApiErrorCategory {
  switch (status) {
    case 400:
      return 'CLIENT_ERROR';
    case 401:
      return 'AUTHENTICATION_ERROR';
    case 403:
      return 'AUTHORIZATION_ERROR';
    case 404:
      return 'NOT_FOUND';
    case 422:
      return 'VALIDATION_ERROR';
    case 503:
      return 'SERVICE_UNAVAILABLE';
    default:
      if (status >= 500) return 'SERVER_ERROR';
      return 'CLIENT_ERROR';
  }
}

function getSanitizedMessage(status: number, serverDetail?: string): string {
  switch (status) {
    case 401:
      return 'Authentication required. Please sign in to continue.';
    case 403:
      return 'You do not have permission to access this medical record.';
    case 404:
      return 'The requested record or resource was not found.';
    case 422:
      return serverDetail || 'Input validation failed. Please check clinical attributes.';
    case 503:
      return 'The ML prediction service or database is temporarily unavailable.';
    case 500:
      return serverDetail || 'An internal server error occurred while processing the request.';
    default:
      return serverDetail || `Request failed with status code ${status}.`;
  }
}

async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { requiresAuth = true, headers: customHeaders = {}, ...customConfig } = options;

  const url = `${BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;

  const headers: Record<string, string> = {
    ...(customHeaders as Record<string, string>),
  };

  // Only set Content-Type for requests with a payload body
  if (customConfig.body) {
    headers['Content-Type'] = 'application/json';
  }

  // Attach Firebase ID token if authentication is required or user is signed in
  if (requiresAuth || auth.currentUser) {
    try {
      if (typeof (auth as any).authStateReady === 'function') {
        await (auth as any).authStateReady();
      }
      const token = await auth.currentUser?.getIdToken();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      } else if (requiresAuth) {
        throw new ApiError(
          401,
          'AUTHENTICATION_ERROR',
          'Authentication required. Please sign in to continue.',
        );
      }
    } catch (err) {
      if (err instanceof ApiError) throw err;
      throw new ApiError(
        401,
        'AUTHENTICATION_ERROR',
        'Failed to retrieve authentication token.',
      );
    }
  }

  let response: Response;
  try {
    response = await fetch(url, {
      credentials: 'include',
      ...customConfig,
      headers,
    });
  } catch (networkErr) {
    // Retry with backoff for transient connection establishment
    try {
      await new Promise((resolve) => setTimeout(resolve, 600));
      response = await fetch(url, {
        credentials: 'include',
        ...customConfig,
        headers,
      });
    } catch (secondErr) {
      try {
        await new Promise((resolve) => setTimeout(resolve, 1000));
        response = await fetch(url, {
          credentials: 'include',
          ...customConfig,
          headers,
        });
      } catch (thirdErr) {
        const detailMsg = thirdErr instanceof Error ? ` (${thirdErr.message})` : '';
        throw new ApiError(
          0,
          'NETWORK_ERROR',
          `Unable to connect to the CardioPulse API${detailMsg}. Please verify network connectivity.`,
          thirdErr,
        );
      }
    }
  }

  if (!response.ok) {
    let detail: unknown = undefined;
    let detailMessage: string | undefined = undefined;

    try {
      const errBody = await response.json();
      detail = errBody;
      if (typeof errBody?.detail === 'string') {
        detailMessage = errBody.detail;
      }
    } catch {
      // Body not JSON
    }

    const category = categorizeStatus(response.status);
    const message = getSanitizedMessage(response.status, detailMessage);
    throw new ApiError(response.status, category, message, detail);
  }

  // Handle empty 204 responses
  if (response.status === 204) {
    return {} as T;
  }

  return response.json() as Promise<T>;
}

export const apiClient = {
  get: <T>(endpoint: string, options?: RequestOptions): Promise<T> =>
    request<T>(endpoint, { ...options, method: 'GET' }),

  post: <T>(endpoint: string, data?: unknown, options?: RequestOptions): Promise<T> =>
    request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: data !== undefined ? JSON.stringify(data) : undefined,
    }),

  delete: <T>(endpoint: string, options?: RequestOptions): Promise<T> =>
    request<T>(endpoint, { ...options, method: 'DELETE' }),
};
