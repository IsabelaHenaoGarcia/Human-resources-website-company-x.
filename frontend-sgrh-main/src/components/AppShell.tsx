"use client";

import {
  BadgeCheck,
  BarChart3,
  BookOpen,
  BriefcaseBusiness,
  ClipboardCheck,
  FileBadge,
  FileClock,
  FileText,
  Gauge,
  LogOut,
  Menu,
  Receipt,
  Search,
  Settings,
  ShieldCheck,
  Users,
  WalletCards,
} from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { clearSession, getStoredUser, hasAnyPermission } from "@/lib/auth";
import { logout } from "@/lib/api-client";
import type { User } from "@/lib/types";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: Gauge, permissions: ["employees:read", "reports:read", "payroll:read"] },
  { href: "/employees", label: "Empleados", icon: BadgeCheck, permissions: ["employees:read"] },
  { href: "/recruitment/candidates", label: "Reclutamiento", icon: Users, permissions: ["recruitment:read"] },
  { href: "/affiliations", label: "Afiliaciones", icon: ClipboardCheck, permissions: ["affiliations:read"] },
  { href: "/payroll/periods", label: "Nomina", icon: WalletCards, permissions: ["payroll:read"] },
  { href: "/offboarding", label: "Retiros", icon: FileClock, permissions: ["offboarding:read"] },
  { href: "/training/activities", label: "Capacitacion", icon: BookOpen, permissions: ["training:read"] },
  { href: "/evaluations", label: "Evaluaciones", icon: BarChart3, permissions: ["evaluations:read"] },
  { href: "/certificates", label: "Certificados", icon: FileBadge, permissions: ["certificates:read"] },
  { href: "/reports", label: "Reportes", icon: FileText, permissions: ["reports:read"] },
  { href: "/audit", label: "Auditoria", icon: ShieldCheck, permissions: ["audit:read"] },
  { href: "/admin/users", label: "Usuarios", icon: Settings, permissions: ["admin:users"] },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const storedUser = getStoredUser();
    if (!storedUser) {
      router.replace("/login");
      return;
    }
    setUser(storedUser);
    setReady(true);
  }, [router]);

  const visibleItems = useMemo(() => navItems.filter((item) => hasAnyPermission(user, item.permissions)), [user]);

  async function handleLogout() {
    await logout();
    clearSession();
    router.replace("/login");
  }

  if (!ready) {
    return (
      <div className="login-page">
        <div className="card login-card">Validando sesion...</div>
      </div>
    );
  }

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            <BriefcaseBusiness size={18} />
          </div>
          <div>
            <div className="brand-title">SGRH</div>
            <div className="brand-caption">Gestion humana interna</div>
          </div>
        </div>
        <nav className="nav-section" aria-label="Navegacion principal">
          {visibleItems.map((item) => {
            const Icon = item.icon;
            const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
            return (
              <Link className={`nav-link ${active ? "active" : ""}`} href={item.href} key={item.href}>
                <Icon size={18} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
        <div className="nav-section" style={{ marginTop: "auto", borderTop: "1px solid #e2e8f0" }}>
          <button className="nav-link" type="button" onClick={handleLogout}>
            <LogOut size={18} />
            <span>Cerrar sesion</span>
          </button>
        </div>
      </aside>
      <div className="main">
        <header className="topbar">
          <div className="actions" style={{ minWidth: 0 }}>
            <button className="icon-button" type="button" aria-label="Menu">
              <Menu size={18} />
            </button>
            <div className="field" style={{ width: "min(420px, 42vw)" }}>
              <div style={{ position: "relative" }}>
                <Search size={17} style={{ left: 10, position: "absolute", top: 10, color: "#64748b" }} />
                <input className="input" style={{ paddingLeft: 34 }} placeholder="Buscar empleados, documentos o procesos" />
              </div>
            </div>
          </div>
          <div className="actions">
            <Receipt size={18} color="#64748b" />
            <span className="muted">{user?.full_name || user?.username}</span>
          </div>
        </header>
        <main className="content">{children}</main>
      </div>
    </div>
  );
}
