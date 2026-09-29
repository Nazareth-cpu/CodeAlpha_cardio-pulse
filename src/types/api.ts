export type ApiErrorCategory =
  | 'AUTHENTICATION_ERROR'
  | 'AUTHORIZATION_ERROR'
  | 'VALIDATION_ERROR'
  | 'NOT_FOUND'
  | 'SERVER_ERROR'
  | 'SERVICE_UNAVAILABLE'
  | 'NETWORK_ERROR'
  | 'CLIENT_ERROR';

export class ApiError extends Error {
  public readonly status: number;
  public readonly category: ApiErrorCategory;
  public readonly detail?: unknown;

  constructor(status: number, category: ApiErrorCategory, message: string, detail?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.category = category;
    this.detail = detail;
  }
}

export interface RequestOptions extends RequestInit {
  requiresAuth?: boolean;
}
