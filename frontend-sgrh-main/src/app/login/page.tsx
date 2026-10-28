"use client";

import { ArrowRight, Building2, Lock, User } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { login } from "@/lib/api-client";
import { storeSession } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const response = await login(username, password);
      storeSession(response.token, response.user);
      router.replace("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "No fue posible iniciar sesion.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="login-page">
      <section className="card login-card">
        <div style={{ display: "grid", justifyItems: "center", gap: 8, marginBottom: 22 }}>
          <div className="brand-mark" style={{ width: 48, height: 48 }}>
            <Building2 size={24} />
          </div>
          <h1 className="page-title" style={{ fontSize: 24 }}>SGRH</h1>
          <p className="muted" style={{ margin: 0 }}>Ingresa al sistema interno de gestion humana</p>
        </div>
        <form className="section" onSubmit={submit}>
          <label className="field">
            <span className="label">Usuario</span>
            <div style={{ position: "relative" }}>
              <User size={17} style={{ left: 10, position: "absolute", top: 10, color: "#64748b" }} />
              <input className="input" style={{ paddingLeft: 34 }} value={username} onChange={(e) => setUsername(e.target.value)} required autoComplete="username" />
            </div>
          </label>
          <label className="field">
            <span className="label">Contrasena</span>
            <div style={{ position: "relative" }}>
              <Lock size={17} style={{ left: 10, position: "absolute", top: 10, color: "#64748b" }} />
              <input className="input" style={{ paddingLeft: 34 }} value={password} onChange={(e) => setPassword(e.target.value)} required type="password" autoComplete="current-password" />
            </div>
          </label>
          {error ? <div className="alert error">{error}</div> : null}
          <button className="button primary" disabled={busy} type="submit" style={{ width: "100%" }}>
            {busy ? "Validando..." : "Iniciar sesion"}
            <ArrowRight size={16} />
          </button>
        </form>
      </section>
    </main>
  );
}
