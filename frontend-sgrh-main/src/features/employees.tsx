"use client";

import { Edit, FileText, Plus } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMemo, useState } from "react";
import { DataTable } from "@/components/DataTable";
import { EntityForm } from "@/components/EntityForm";
import { FileList, FileUploader } from "@/components/FileTools";
import { PageHeader } from "@/components/PageHeader";
import { ErrorState } from "@/components/States";
import { StatusBadge } from "@/components/StatusBadge";
import { ChecklistSection, TimelinePanel } from "@/components/WorkflowPanels";
import { apiRequest } from "@/lib/api-client";
import { catalogName, catalogs, defaultId } from "@/lib/catalogs";
import { cleanPayload, type FieldConfig, type FormValues } from "@/lib/forms";
import { formatDate, formatMoney } from "@/lib/format";
import type { DocumentRecord, Employee, PaginatedResponse } from "@/lib/types";
import { loadingText, useApiData } from "./hooks";

const employeeFields: FieldConfig[] = [
  { name: "full_name", label: "Nombre completo", required: true },
  { name: "document_type_id", label: "Tipo documento", type: "select", options: catalogs.documentTypes, required: true },
  { name: "document_number", label: "Numero documento", required: true },
  { name: "employee_status_id", label: "Estado", type: "select", options: catalogs.employeeStatuses, required: true },
  { name: "position", label: "Cargo", required: true },
  { name: "hire_date", label: "Fecha ingreso", type: "date", required: true },
  { name: "base_salary", label: "Salario base", type: "number", required: true, step: "1000" },
  { name: "email", label: "Correo", type: "email" },
  { name: "phone", label: "Telefono" },
  { name: "birth_date", label: "Fecha nacimiento", type: "date" },
  { name: "address", label: "Direccion", full: true },
  { name: "eps_entity", label: "EPS" },
  { name: "pension_entity", label: "Pension" },
  { name: "has_beneficiaries", label: "Tiene beneficiarios", type: "checkbox" },
  { name: "beneficiary_notes", label: "Notas beneficiarios", type: "textarea", full: true },
  { name: "induction_completed", label: "Induccion completada", type: "checkbox" },
  { name: "latest_evaluation_status", label: "Ultima evaluacion" },
  { name: "latest_evaluation_date", label: "Fecha ultima evaluacion", type: "date" },
];

function employeeDefaults(employee?: Employee) {
  return {
    employee_status_id: defaultId(catalogs.employeeStatuses, "active"),
    document_type_id: defaultId(catalogs.documentTypes, "cc"),
    hire_date: new Date().toISOString().slice(0, 10),
    base_salary: 0,
    has_beneficiaries: false,
    induction_completed: false,
    ...employee,
  };
}

function employeePayload(values: FormValues) {
  return cleanPayload(
    values,
    ["document_type_id", "employee_status_id", "base_salary", "user_id"],
    ["has_beneficiaries", "induction_completed"],
  );
}

export function EmployeesListPage() {
  const [q, setQ] = useState("");
  const query = useMemo(() => ({ q, page: 1, page_size: 20 }), [q]);
  const { data, loading, error } = useApiData<PaginatedResponse<Employee>>("/employees", { items: [], page: 1, page_size: 20, total: 0 }, query);

  return (
    <>
      <PageHeader
        eyebrow="Expedientes"
        title="Directorio de empleados"
        description="Consulta, crea y mantiene los registros maestros del personal activo e historico."
        actions={<Link className="button primary" href="/employees/new"><Plus size={16} /> Nuevo empleado</Link>}
      />
      <div className="card toolbar">
        <input className="input" style={{ maxWidth: 360 }} placeholder="Buscar por nombre o documento" value={q} onChange={(e) => setQ(e.target.value)} />
        <span className="muted">{data.total} registros</span>
      </div>
      {error ? <ErrorState message={error} /> : loadingText(loading)}
      {!loading && !error ? (
        <div className="card">
          <DataTable
            data={data.items}
            columns={[
              { header: "Empleado", cell: (row) => <Link href={`/employees/${row.id}`}><strong>{row.full_name}</strong><div className="muted">{row.position}</div></Link> },
              { header: "Documento", cell: (row) => <span className="tabular">{catalogName(catalogs.documentTypes, row.document_type_id)} {row.document_number}</span> },
              { header: "Estado", cell: (row) => <StatusBadge items={catalogs.employeeStatuses} id={row.employee_status_id} /> },
              { header: "Ingreso", cell: (row) => formatDate(row.hire_date) },
              { header: "Salario", cell: (row) => <span className="tabular">{formatMoney(row.base_salary)}</span> },
              { header: "Acciones", cell: (row) => <div className="actions"><Link className="button" href={`/employees/${row.id}/edit`}><Edit size={14} /> Editar</Link><Link className="button" href={`/employees/${row.id}/documents`}><FileText size={14} /> Docs</Link></div> },
            ]}
          />
        </div>
      ) : null}
    </>
  );
}

export function EmployeeFormPage({ employeeId }: { employeeId?: string }) {
  const router = useRouter();
  const isEdit = Boolean(employeeId);
  const { data: employee, loading, error } = useApiData<Employee | null>(employeeId ? `/employees/${employeeId}` : "/employees/0", null, undefined, isEdit);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(values: FormValues) {
    setBusy(true);
    setSubmitError(null);
    try {
      const payload = employeePayload(values);
      const saved = await apiRequest<Employee>(isEdit ? `/employees/${employeeId}` : "/employees", {
        method: isEdit ? "PUT" : "POST",
        body: JSON.stringify(payload),
      });
      router.push(`/employees/${saved.id}`);
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : "No fue posible guardar el empleado.");
    } finally {
      setBusy(false);
    }
  }

  const ready = !isEdit || employee;
  return (
    <>
      <PageHeader
        eyebrow="Expedientes"
        title={isEdit ? "Editar empleado" : "Nuevo empleado"}
        description="Los datos se validan de forma definitiva en el backend; aqui se capturan los campos operativos principales."
      />
      {isEdit && error ? <ErrorState message={error} /> : null}
      {isEdit ? loadingText(loading) : null}
      {submitError ? <ErrorState message={submitError} /> : null}
      {ready ? (
        <div className="card" style={{ padding: 20 }}>
          <EntityForm
            fields={employeeFields}
            defaults={employeeDefaults(employee ?? undefined)}
            submitLabel={isEdit ? "Guardar cambios" : "Crear empleado"}
            busy={busy}
            onCancel={() => router.back()}
            onSubmit={submit}
          />
        </div>
      ) : null}
    </>
  );
}

export function EmployeeDetailPage({ employeeId }: { employeeId: string }) {
  const { data: employee, loading, error } = useApiData<Employee | null>(`/employees/${employeeId}`, null);

  return (
    <>
      <PageHeader
        eyebrow="Perfil"
        title={employee?.full_name ?? "Empleado"}
        description="Vista consolidada del expediente laboral, afiliaciones, documentos y trazabilidad basica."
        actions={<><Link className="button" href="/employees">Volver</Link><Link className="button primary" href={`/employees/${employeeId}/edit`}><Edit size={16} /> Editar</Link></>}
      />
      {error ? <ErrorState message={error} /> : loadingText(loading)}
      {employee ? (
        <div className="grid-2">
          <div className="card" style={{ padding: 18 }}>
            <div className="actions" style={{ justifyContent: "space-between" }}>
              <h2 style={{ margin: 0 }}>{employee.position}</h2>
              <StatusBadge items={catalogs.employeeStatuses} id={employee.employee_status_id} />
            </div>
            <div className="detail-list" style={{ marginTop: 16 }}>
              <div className="detail-item"><span>Documento</span><strong>{catalogName(catalogs.documentTypes, employee.document_type_id)} {employee.document_number}</strong></div>
              <div className="detail-item"><span>Ingreso</span><strong>{formatDate(employee.hire_date)}</strong></div>
              <div className="detail-item"><span>Correo</span><strong>{employee.email || "No registrado"}</strong></div>
              <div className="detail-item"><span>Telefono</span><strong>{employee.phone || "No registrado"}</strong></div>
              <div className="detail-item"><span>Salario base</span><strong>{formatMoney(employee.base_salary)}</strong></div>
              <div className="detail-item"><span>EPS / Pension</span><strong>{employee.eps_entity || "EPS N/D"} / {employee.pension_entity || "Pension N/D"}</strong></div>
            </div>
          </div>
          <div className="section">
            <div className="card" style={{ padding: 18 }}>
              <h3 style={{ marginTop: 0 }}>Checklist operativo</h3>
              <ChecklistSection
                items={[
                  { label: "Induccion completada", done: employee.induction_completed },
                  { label: "Afiliacion EPS registrada", done: Boolean(employee.eps_entity) },
                  { label: "Afiliacion pension registrada", done: Boolean(employee.pension_entity) },
                  { label: "Beneficiarios revisados", done: !employee.has_beneficiaries || Boolean(employee.beneficiary_notes) },
                ]}
              />
            </div>
            <div className="card" style={{ padding: 18 }}>
              <h3 style={{ marginTop: 0 }}>Linea de tiempo</h3>
              <TimelinePanel items={[{ title: "Empleado creado", date: employee.created_at }, { title: "Ultima actualizacion", date: employee.updated_at }]} />
            </div>
          </div>
        </div>
      ) : null}
    </>
  );
}

export function EmployeeDocumentsPage({ employeeId }: { employeeId: string }) {
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  return (
    <>
      <PageHeader
        eyebrow="Expediente digital"
        title="Documentos del empleado"
        description="Carga y vincula soportes al expediente del empleado. El backend mantiene el control de descarga por RBAC."
        actions={<Link className="button" href={`/employees/${employeeId}`}>Volver al perfil</Link>}
      />
      <div className="grid-2">
        <div className="card" style={{ padding: 18 }}>
          <h2 style={{ marginTop: 0 }}>Carga de soporte</h2>
          <FileUploader target="employees" targetId={Number(employeeId)} onUploaded={(document) => setDocuments((current) => [document, ...current])} />
        </div>
        <div className="card" style={{ padding: 18 }}>
          <h2 style={{ marginTop: 0 }}>Archivos recientes</h2>
          <FileList documents={documents} />
        </div>
      </div>
    </>
  );
}
