export type ApiErrorKind =
  | 'authentication'
  | 'forbidden'
  | 'validation'
  | 'server'
  | 'network'
  | 'http'
  | 'response';

export class ApiError extends Error {
  constructor(
    public readonly kind: ApiErrorKind,
    public readonly status: number | null,
    public readonly detail?: unknown,
  ) {
    // Use fixed messages rather than reflecting potentially sensitive payloads.
    const messages: Record<ApiErrorKind, string> = {
      authentication: 'Authentication failed',
      forbidden: 'Access denied',
      validation: 'Request validation failed',
      server: 'Server error',
      network: 'Could not connect to the server',
      http: 'Request failed',
      response: 'Invalid server response',
    };
    super(messages[kind]);
    this.name = 'ApiError';
  }
}

function classifyStatus(status: number): ApiErrorKind {
  if (status === 401) return 'authentication';
  if (status === 403) return 'forbidden';
  if (status === 422) return 'validation';
  if (status >= 500 && status <= 599) return 'server';
  return 'http';
}

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const headers = new Headers({ Accept: 'application/json' });
  new Headers(options.headers).forEach((value, name) => headers.set(name, value));

  let response: Response;
  try {
    response = await fetch(path, { ...options, headers });
  } catch {
    throw new ApiError('network', null);
  }

  if (!response.ok) {
    let detail: unknown;
    try {
      const payload: unknown = await response.json();
      if (typeof payload === 'object' && payload !== null && 'detail' in payload) {
        detail = payload.detail;
      }
    } catch {
      // An unreadable error body must not hide the HTTP status.
    }
    throw new ApiError(classifyStatus(response.status), response.status, detail);
  }

  try {
    return await response.json() as T;
  } catch {
    throw new ApiError('response', response.status);
  }
}
