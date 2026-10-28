import { clearSession, getStoredToken } from "./auth";
import type { DocumentRecord, LoginResponse } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  details: unknown;

  constructor(message: string, status: number, details?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

type RequestOptions = RequestInit & {
  auth?: boolean;
  query?: Record<string, string | number | boolean | undefined | null>;
};

function buildUrl(path: string, query?: RequestOptions["query"]) {
  const url = new URL(path, API_BASE_URL);
  Object.entries(query ?? {}).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      url.searchParams.set(key, String(value));
    }
  });
  return url.toString();
}

async function parseError(response: Response) {
  try {
    const payload = await response.json();
    return payload?.error?.message ?? payload?.detail ?? payload?.message ?? response.statusText;
  } catch {
    return response.statusText;
  }
}

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const token = getStoredToken();
  const headers = new Headers(options.headers);
  const hasBody = options.body !== undefined && !(options.body instanceof FormData);
  if (hasBody && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  if (options.auth !== false && token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(buildUrl(path, options.query), {
    ...options,
    headers,
  });

  if (response.status === 401) {
    clearSession();
    if (typeof window !== "undefined") {
      window.location.assign("/login");
    }
    throw new ApiError("Sesion expirada. Inicia sesion nuevamente.", 401);
  }

  if (!response.ok) {
    throw new ApiError(await parseError(response), response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export function login(username: string, password: string) {
  return apiRequest<LoginResponse>("/auth/login", {
    auth: false,
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
}

export function logout() {
  return apiRequest<void>("/auth/logout", { method: "POST" }).catch(() => undefined);
}

export async function uploadDocument(file: File, options?: { tipo_archivo_id?: number; nombre_archivo?: string }) {
  const body = new FormData();
  body.append("file", file);
  const query = {
    tipo_archivo_id: options?.tipo_archivo_id,
    nombre_archivo: options?.nombre_archivo,
  };
  return apiRequest<DocumentRecord>("/documents/upload", {
    method: "POST",
    body,
    query,
  });
}

export async function downloadDocument(documentId: number, filename = "documento") {
  const token = getStoredToken();
  const response = await fetch(buildUrl(`/documents/${documentId}/download`), {
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
  });
  if (!response.ok) {
    throw new ApiError(await parseError(response), response.status);
  }
  const blob = await response.blob();
  const objectUrl = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = objectUrl;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(objectUrl);
}
