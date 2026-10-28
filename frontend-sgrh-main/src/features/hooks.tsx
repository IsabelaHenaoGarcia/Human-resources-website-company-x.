"use client";

import { useCallback, useEffect, useState } from "react";
import { apiRequest } from "@/lib/api-client";

export function useApiData<T>(path: string, fallback: T, query?: Record<string, string | number | undefined>, enabled = true) {
  const [data, setData] = useState<T>(fallback);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const queryKey = JSON.stringify(query ?? {});

  const load = useCallback(async () => {
    if (!enabled) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      setData(await apiRequest<T>(path, { query: JSON.parse(queryKey) as Record<string, string | number | undefined> }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "No fue posible cargar la informacion.");
    } finally {
      setLoading(false);
    }
  }, [enabled, path, queryKey]);

  useEffect(() => {
    void load();
  }, [load]);

  return { data, setData, loading, error, reload: load };
}

export function loadingText(loading: boolean, label = "Cargando informacion...") {
  return loading ? <div className="card" style={{ padding: 18 }}>{label}</div> : null;
}
