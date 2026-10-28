"use client";

import Link from "next/link";
import { PageHeader } from "@/components/PageHeader";
import { StatusBadge } from "@/components/StatusBadge";
import { DataTable } from "@/components/DataTable";
import { catalogs } from "@/lib/catalogs";
import { formatDate, formatMoney } from "@/lib/format";
import type { Employee, PayrollPeriod, PaginatedResponse } from "@/lib/types";
import { useApiData } from "./hooks";

export function DashboardPage() {
  const employees = useApiData<PaginatedResponse<Employee>>("/employees", { items: [], total: 0, page: 1, page_size: 5 }, { page: 1, page_size: 5 });
  const periods = useApiData<PayrollPeriod[]>("/payroll/periods", []);
  const activeEmployees = employees.data.items.filter((employee) => employee.employee_status_id === 1).length;
  const openPeriods = periods.data.filter((period) => period.status_id !== 4).length;

  return (
    <>
      <PageHeader
        eyebrow="Operacion"
        title="Dashboard"
        description="Resumen de trabajo para recursos humanos, contabilidad y gerencia."
        actions={<Link className="button primary" href="/employees/new">Crear empleado</Link>}
      />
      <div className="grid-3" style={{ marginBottom: 18 }}>
        <div className="card stat"><div className="stat-label">Empleados consultados</div><div className="stat-value">{employees.data.total}</div></div>
        <div className="card stat"><div className="stat-label">Activos en pagina</div><div className="stat-value">{activeEmployees}</div></div>
        <div className="card stat"><div className="stat-label">Periodos abiertos</div><div className="stat-value">{openPeriods}</div></div>
      </div>
      <div className="grid-2">
        <div className="card">
          <div className="toolbar"><strong>Empleados recientes</strong><Link className="button" href="/employees">Ver directorio</Link></div>
          <DataTable
            data={employees.data.items}
            columns={[
              { header: "Empleado", cell: (row) => <Link href={`/employees/${row.id}`}><strong>{row.full_name}</strong><div className="muted">{row.position}</div></Link> },
              { header: "Estado", cell: (row) => <StatusBadge items={catalogs.employeeStatuses} id={row.employee_status_id} /> },
              { header: "Ingreso", cell: (row) => formatDate(row.hire_date) },
            ]}
          />
        </div>
        <div className="card">
          <div className="toolbar"><strong>Periodos de nomina</strong><Link className="button" href="/payroll/periods">Ver nomina</Link></div>
          <DataTable
            data={periods.data.slice(0, 5)}
            columns={[
              { header: "Periodo", cell: (row) => <Link href={`/payroll/periods/${row.id}`}><strong>{row.name}</strong></Link> },
              { header: "Estado", cell: (row) => <StatusBadge items={catalogs.payrollPeriodStatuses} id={row.status_id} /> },
              { header: "Rango", cell: (row) => `${formatDate(row.start_date)} - ${formatDate(row.end_date)}` },
            ]}
          />
        </div>
      </div>
      <div className="card" style={{ padding: 18, marginTop: 18 }}>
        <strong>Alertas operativas</strong>
        <div className="grid-3" style={{ marginTop: 12 }}>
          <div className="alert">Documentos obligatorios pendientes deben revisarse en cada expediente digital.</div>
          <div className="alert">Las liquidaciones de nomina requieren aprobacion antes del pago.</div>
          <div className="alert">Total base visible: {formatMoney(employees.data.items.reduce((sum, item) => sum + Number(item.base_salary ?? 0), 0))}</div>
        </div>
      </div>
    </>
  );
}
