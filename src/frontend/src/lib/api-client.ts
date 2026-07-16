import { z } from "zod";

const API_URL = import.meta.env.VITE_API_URL || "/api";

const buildApiUrl = (path: string) => new URL(`${API_URL}${path}`, window.location.origin);

export class ApiError extends Error {
  constructor(message: string, public readonly status: number, public readonly details?: unknown) {
    super(message);
    this.name = "ApiError";
  }
}

class ApiClient {
  async get<T>(path: string, schema: z.ZodType<T>, query?: Record<string, string>): Promise<T> {
    const url = buildApiUrl(path);
    Object.entries(query ?? {}).forEach(([key, value]) => url.searchParams.set(key, value));
    return this.request(url.toString(), { method: "GET" }, schema);
  }

  async post<TRequest, TResponse>(path: string, body: TRequest, schema: z.ZodType<TResponse>): Promise<TResponse> {
    return this.request(
      `${API_URL}${path}`,
      { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) },
      schema,
    );
  }

  private async request<T>(url: string, init: RequestInit, schema: z.ZodType<T>): Promise<T> {
    let response: Response;
    try {
      response = await fetch(url, init);
    } catch {
      throw new ApiError("The server could not be reached.", 0);
    }

    const payload: unknown = await response.json().catch(() => null);
    const envelope = z.object({ success: z.boolean(), message: z.string(), data: z.unknown() }).safeParse(payload);
    if (!response.ok || !envelope.success || !envelope.data.success) {
      throw new ApiError(envelope.success ? envelope.data.message : "The server returned an invalid response.", response.status, envelope.success ? envelope.data.data : undefined);
    }
    return schema.parse(envelope.data.data);
  }
}

export const apiClient = new ApiClient();
