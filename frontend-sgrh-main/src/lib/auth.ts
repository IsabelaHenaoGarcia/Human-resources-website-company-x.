import type { User } from "./types";

const TOKEN_KEY = "sgrh.token";
const USER_KEY = "sgrh.user";

export function getStoredToken() {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function getStoredUser(): User | null {
  if (typeof window === "undefined") return null;
  const raw = window.localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as User;
  } catch {
    clearSession();
    return null;
  }
}

export function storeSession(token: string, user: User) {
  window.localStorage.setItem(TOKEN_KEY, token);
  window.localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function clearSession() {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(TOKEN_KEY);
  window.localStorage.removeItem(USER_KEY);
}

export function hasPermission(user: User | null, permission: string) {
  if (!user) return false;
  return user.permissions.includes("*") || user.permissions.includes(permission);
}

export function hasAnyPermission(user: User | null, permissions: string[]) {
  if (!permissions.length) return true;
  return permissions.some((permission) => hasPermission(user, permission));
}
