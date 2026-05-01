import { useState, useEffect, useRef, useCallback } from "react";

type FilterConfig = readonly string[];

function readFromUrl(keys: FilterConfig): Record<string, string> {
  if (typeof window === "undefined") {
    return Object.fromEntries(keys.map((k) => [k, ""]));
  }
  const params = new URLSearchParams(window.location.search);
  return Object.fromEntries(keys.map((k) => [k, params.get(k) ?? ""]));
}

function useUrlFilters(keys: FilterConfig): {
  values: Record<string, string>;
  set: (key: string, value: string) => void;
  clear: () => void;
  hasFilters: boolean;
} {
  const [state, setState] = useState(() => readFromUrl(keys));
  const isInitial = useRef(true);

  useEffect(() => {
    if (isInitial.current) {
      isInitial.current = false;
      return;
    }
    const params = new URLSearchParams();
    for (const key of keys) {
      if (state[key]) params.set(key, state[key]);
    }
    const search = params.toString();
    const url = search
      ? `${window.location.pathname}?${search}`
      : window.location.pathname;
    history.replaceState(null, "", url);
  }, [state, keys]);

  const set = useCallback(
    (key: string, value: string) => {
      setState((prev) => ({ ...prev, [key]: value }));
    },
    [],
  );

  const clear = useCallback(() => {
    setState(Object.fromEntries(keys.map((k) => [k, ""])));
  }, [keys]);

  const hasFilters = keys.some((k) => !!state[k]);

  return { values: state, set, clear, hasFilters };
}

export { useUrlFilters };
