"use client";

import { Download, FilePlus2, Plus, RefreshCcw, Save } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { DataTable } from "@/components/DataTable";
import { EntityForm } from "@/components/EntityForm";
import { PageHeader } from "@/components/PageHeader";
import { ErrorState } from "@/components/States";
import { StatusBadge } from "@/components/StatusBadge";
import { ApprovalPanel, ChecklistSection } from "@/components/WorkflowPanels";
import { apiRequest, downloadDocument } from "@/lib/api-client";
import { catalogName, catalogs, defaultId } from "@/lib/catalogs";
import { cleanPayload, type FormValues } from "@/lib/forms";
import { formatDate, formatDateTime, formatMoney } from "@/lib/format";
import type {
  AdminUser,
  Affiliation,
  AuditRecord,
  Certificate,
  ContractSettlement,
  Evaluation,
  Offboarding,
  PaginatedResponse,
  PayrollPeriod,
  PayrollSettlement,
  TrainingActivity,
} from "@/lib/types";
import { loadingText, useApiData } from "./hooks";

export function AffiliationsPage() {
  const { data, loading, error, reload } = useApiData<Affiliation[]>("/affiliations", []);
  return (
    <>
      <PageHeader eyebrow="Seguridad social" title="Afiliaciones" description="Seguimiento interno de EPS, ARL, pension y caja de compensacion." actions={<Link className="button primary" href="/affiliations/new"><Plus size={16} /> Nueva afiliacion</Link>} />
      {error ? <ErrorState message={error} /> : loadingText(loading)}
      {!loading && !error ? (
        <div className="card">
          <DataTable
            data={data}
            columns={[
              { header: "Empleado", cell: (row) => `Empleado ${row.employee_id}` },
              { header: "Tipo", cell: (row) => catalogName(catalogs.affiliationTypes, row.affiliation_type_id) },
              { header: "Entidad", cell: (row) => row.entity },
              { header: "Estado", cell: (row) => <StatusBadge items={catalogs.affiliationStatuses} id={row.affiliation_status_id} /> },
              { header: "Registro", cell: (row) => formatDate(row.registration_date) },
              { header: "Acciones", cell: () => <button className="button" type="button" onClick={() => void reload()}><RefreshCcw size={14} /> Refrescar</button> },
            ]}
          />
        </div>
      ) : null}
    </>
  );
}

export function AffiliationNewPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  async function submit(values: FormValues) {
    setError(null);
    try {
      await apiRequest<Affiliation>("/affiliations", {
        method: "POST",
        body: JSON.stringify({
          empleado_id: Number(values.empleado_id),
          tipo_afiliacion_id: Number(values.tipo_afiliacion_id),
          entidad: values.entidad,
          fecha_registro: values.fecha_registro,
          estado_afiliacion_id: Number(values.estado_afiliacion_id),
          observaciones: values.observaciones || null,
        }),
      });
      router.push("/affiliations");
    } catch (err) {
      setError(err instanceof Error ? err.message : "No fue posible crear la afiliacion.");
    }
  }
  return (
    <>
      <PageHeader eyebrow="Seguridad social" title="Nueva afiliacion" description="Registra el tramite manual y su estado operativo." />
      {error ? <ErrorState message={error} /> : null}
      <div className="card" style={{ padding: 20 }}>
        <EntityForm
          fields={[
            { name: "empleado_id", label: "ID empleado", type: "number", required: true },
            { name: "tipo_afiliacion_id", label: "Tipo afiliacion", type: "select", options: catalogs.affiliationTypes, required: true },
            { name: "entidad", label: "Entidad", required: true },
            { name: "fecha_registro", label: "Fecha registro", type: "date", required: true },
            { name: "estado_afiliacion_id", label: "Estado", type: "select", options: catalogs.affiliationStatuses, required: true },
            { name: "observaciones", label: "Observaciones", type: "textarea", full: true },
          ]}
          defaults={{ fecha_registro: new Date().toISOString().slice(0, 10), estado_afiliacion_id: defaultId(catalogs.affiliationStatuses, "pending") }}
          submitLabel="Crear afiliacion"
          onCancel={() => router.back()}
          onSubmit={submit}
        />
      </div>
    </>
  );
}

export function PayrollPeriodsPage() {
  const { data, loading, error } = useApiData<PayrollPeriod[]>("/payroll/periods", []);
  const [formError, setFormError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);

  async function create(values: FormValues) {
    setFormError(null);
    try {
      await apiRequest<PayrollPeriod>("/payroll/periods", {
        method: "POST",
        body: JSON.stringify(cleanPayload(values, ["status_id"])),
      });
      window.location.reload();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : "No fue posible crear el periodo.");
    }
  }

  return (
    <>
      <PageHeader eyebrow="Nomina" title="Periodos de nomina" description="Lista de periodos, liquidacion, revision y aprobacion gerencial." actions={<button className="button primary" type="button" onClick={() => setShowForm((v) => !v)}><Plus size={16} /> Nuevo periodo</button>} />
      {showForm ? (
        <div className="card" style={{ padding: 18, marginBottom: 16 }}>
          {formError ? <ErrorState message={formError} /> : null}
          <EntityForm
            fields={[
              { name: "name", label: "Nombre", required: true },
              { name: "start_date", label: "Inicio", type: "date", required: true },
              { name: "end_date", label: "Fin", type: "date", required: true },
              { name: "status_id", label: "Estado", type: "select", options: catalogs.payrollPeriodStatuses, required: true },
            ]}
            defaults={{ status_id: defaultId(catalogs.payrollPeriodStatuses, "draft") }}
            submitLabel="Crear periodo"
            onSubmit={create}
          />
        </div>
      ) : null}
      {error ? <ErrorState message={error} /> : loadingText(loading)}
      {!loading && !error ? (
        <div className="card">
          <DataTable
            data={data}
            columns={[
              { header: "Periodo", cell: (row) => <Link href={`/payroll/periods/${row.id}`}><strong>{row.name}</strong></Link> },
              { header: "Rango", cell: (row) => `${formatDate(row.start_date)} - ${formatDate(row.end_date)}` },
              { header: "Estado", cell: (row) => <StatusBadge items={catalogs.payrollPeriodStatuses} id={row.status_id} /> },
              { header: "Aprobacion", cell: (row) => row.approved_at ? formatDateTime(row.approved_at) : "Pendiente" },
            ]}
          />
        </div>
      ) : null}
    </>
  );
}

export function PayrollPeriodDetailPage({ periodId }: { periodId: string }) {
  const { data: periods } = useApiData<PayrollPeriod[]>("/payroll/periods", []);
  const { data: settlements, reload } = useApiData<PayrollSettlement[]>("/payroll/settlements", []);
  const period = periods.find((item) => item.id === Number(periodId));
  const filtered = settlements.filter((item) => item.payroll_period_id === Number(periodId));
  const [error, setError] = useState<string | null>(null);

  async function action(path: string, payload?: Record<string, unknown>) {
    setError(null);
    try {
      await apiRequest(path, { method: "POST", body: payload ? JSON.stringify(payload) : undefined });
      await reload();
    } catch (err) {
      setError(err instanceof Error ? err.message : "No fue posible ejecutar la accion.");
    }
  }

  async function report() {
    try {
      const doc = await apiRequest<{ id: number; original_filename: string }>(`/payroll/periods/${periodId}/general-report`);
      await downloadDocument(doc.id, doc.original_filename);
    } catch (err) {
      setError(err instanceof Error ? err.message : "No fue posible descargar el reporte.");
    }
  }

  return (
    <>
      <PageHeader eyebrow="Nomina" title={period?.name ?? `Periodo ${periodId}`} description="Gestiona novedades, liquidacion, aprobacion y exportes." actions={<Link className="button" href="/payroll/periods">Volver</Link>} />
      {error ? <ErrorState message={error} /> : null}
      <div className="grid-2">
        <div className="section">
          {period ? <ApprovalPanel status={<StatusBadge items={catalogs.payrollPeriodStatuses} id={period.status_id} />} approvedBy={period.approved_by_id} approvedAt={period.approved_at} comment={period.approval_comment} /> : null}
          <div className="card" style={{ padding: 18 }}>
            <h3 style={{ marginTop: 0 }}>Acciones del periodo</h3>
            <div className="actions">
              <button className="button primary" type="button" onClick={() => void action(`/payroll/periods/${periodId}/settle`)}><Save size={16} /> Liquidar</button>
              <button className="button" type="button" onClick={() => void action(`/payroll/periods/${periodId}/review`, { aprobado_por_gerencia: true, observacion: "Aprobado desde frontend SGRH" })}>Aprobar</button>
              <button className="button" type="button" onClick={() => void action(`/payroll/periods/${periodId}/contributions`)}>Generar aportes</button>
              <button className="button" type="button" onClick={() => void action(`/payroll/periods/${periodId}/contributions/export`)}><Download size={16} /> Exportar aportes</button>
              <button className="button" type="button" onClick={() => void report()}><Download size={16} /> Reporte general</button>
            </div>
          </div>
          <div className="card" style={{ padding: 18 }}>
            <h3 style={{ marginTop: 0 }}>Nueva novedad</h3>
            <EntityForm
              fields={[
                { name: "empleado_id", label: "ID empleado", type: "number", required: true },
                { name: "tipo_novedad_codigo", label: "Tipo novedad", type: "select", options: catalogs.payrollNoveltyTypes, required: true },
                { name: "fecha_aplicacion", label: "Fecha aplicacion", type: "date", required: true },
                { name: "valor", label: "Valor", type: "number", step: "1000" },
                { name: "cantidad_horas", label: "Horas", type: "number", step: "0.5" },
                { name: "observaciones", label: "Observaciones", type: "textarea", full: true },
              ]}
              defaults={{ fecha_aplicacion: new Date().toISOString().slice(0, 10), valor: 0 }}
              submitLabel="Agregar novedad"
              onSubmit={(values) => action(`/payroll/periods/${periodId}/novelties`, { ...values, empleado_id: Number(values.empleado_id), valor: Number(values.valor || 0), cantidad_horas: values.cantidad_horas ? Number(values.cantidad_horas) : null, tipo_novedad_codigo: catalogs.payrollNoveltyTypes.find((item) => item.id === Number(values.tipo_novedad_codigo))?.code })}
            />
          </div>
        </div>
        <div className="card">
          <DataTable
            data={filtered}
            emptyTitle="Sin liquidaciones"
            columns={[
              { header: "Liquidacion", cell: (row) => <Link href={`/payroll/settlements/${row.id}`}><strong>LIQ-{row.id}</strong></Link> },
              { header: "Empleado", cell: (row) => `Empleado ${row.employee_id}` },
              { header: "Estado", cell: (row) => <StatusBadge items={catalogs.payrollSettlementStatuses} id={row.status_id} /> },
              { header: "Neto", cell: (row) => formatMoney(row.net_pay) },
            ]}
          />
        </div>
      </div>
    </>
  );
}

export function PayrollSettlementPage({ settlementId }: { settlementId: string }) {
  const { data: settlement, loading, error } = useApiData<PayrollSettlement | null>(`/payroll/settlements/${settlementId}`, null);
  const [actionError, setActionError] = useState<string | null>(null);
  async function paySlip() {
    try {
      const doc = await apiRequest<{ id: number; original_filename: string }>(`/payroll/settlements/${settlementId}/pay-slip`, { method: "POST" });
      await downloadDocument(doc.id, doc.original_filename);
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "No fue posible generar el desprendible.");
    }
  }
  return (
    <>
      <PageHeader eyebrow="Nomina" title={`Liquidacion ${settlementId}`} description="Detalle de valores calculados y generacion de desprendible PDF." actions={<button className="button primary" type="button" onClick={() => void paySlip()}><FilePlus2 size={16} /> Generar desprendible</button>} />
      {error ? <ErrorState message={error} /> : loadingText(loading)}
      {actionError ? <ErrorState message={actionError} /> : null}
      {settlement ? (
        <div className="grid-2">
          <div className="card" style={{ padding: 18 }}>
            <StatusBadge items={catalogs.payrollSettlementStatuses} id={settlement.status_id} />
            <div className="detail-list" style={{ marginTop: 16 }}>
              <div className="detail-item"><span>Empleado</span><strong>{settlement.employee_id}</strong></div>
              <div className="detail-item"><span>Periodo</span><strong>{settlement.payroll_period_id}</strong></div>
              <div className="detail-item"><span>Base</span><strong>{formatMoney(settlement.base_salary)}</strong></div>
              <div className="detail-item"><span>Devengos</span><strong>{formatMoney(settlement.earnings_total)}</strong></div>
              <div className="detail-item"><span>Deducciones</span><strong>{formatMoney(settlement.deductions_total)}</strong></div>
              <div className="detail-item"><span>Neto</span><strong>{formatMoney(settlement.net_pay)}</strong></div>
            </div>
          </div>
          <ApprovalPanel status={<StatusBadge items={catalogs.payrollSettlementStatuses} id={settlement.status_id} />} approvedBy={settlement.approved_by_id} approvedAt={settlement.approved_at} comment={settlement.approval_comment} />
        </div>
      ) : null}
    </>
  );
}

export function OffboardingPage() {
  const { data, loading, error } = useApiData<Offboarding[]>("/offboarding", []);
  return (
    <>
      <PageHeader eyebrow="Retiros" title="Procesos de retiro" description="Control de retiro, checklist de salida y aprobacion de liquidacion final." actions={<Link className="button primary" href="/offboarding/new"><Plus size={16} /> Nuevo retiro</Link>} />
      {error ? <ErrorState message={error} /> : loadingText(loading)}
      {!loading && !error ? <div className="card"><DataTable data={data} columns={[
        { header: "Retiro", cell: (row) => <Link href={`/offboarding/${row.id}`}><strong>RET-{row.id}</strong></Link> },
        { header: "Empleado", cell: (row) => `Empleado ${row.employee_id}` },
        { header: "Estado", cell: (row) => <StatusBadge items={catalogs.offboardingStatuses} id={row.status_id} /> },
        { header: "Fecha retiro", cell: (row) => formatDate(row.withdrawal_date) },
        { header: "Checklist", cell: (row) => `${[row.exit_exam_completed, row.equipment_returned, row.uniforms_returned].filter(Boolean).length}/3` },
      ]} /></div> : null}
    </>
  );
}

export function OffboardingNewPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  async function submit(values: FormValues) {
    try {
      const saved = await apiRequest<Offboarding>("/offboarding", {
        method: "POST",
        body: JSON.stringify({
          empleado_id: Number(values.empleado_id),
          contrato_id: Number(values.contrato_id),
          fecha_retiro: values.fecha_retiro,
          motivo_retiro_id: Number(values.motivo_retiro_id),
          estado_retiro_id: Number(values.estado_retiro_id),
          observaciones: values.observaciones || null,
        }),
      });
      router.push(`/offboarding/${saved.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "No fue posible crear el retiro.");
    }
  }
  return (
    <>
      <PageHeader eyebrow="Retiros" title="Nuevo proceso de retiro" description="Inicia el retiro y asocia contrato, motivo y fecha." />
      {error ? <ErrorState message={error} /> : null}
      <div className="card" style={{ padding: 20 }}><EntityForm fields={[
        { name: "empleado_id", label: "ID empleado", type: "number", required: true },
        { name: "contrato_id", label: "ID contrato", type: "number", required: true },
        { name: "fecha_retiro", label: "Fecha retiro", type: "date", required: true },
        { name: "motivo_retiro_id", label: "Motivo", type: "select", options: catalogs.withdrawalReasons, required: true },
        { name: "estado_retiro_id", label: "Estado", type: "select", options: catalogs.offboardingStatuses, required: true },
        { name: "observaciones", label: "Observaciones", type: "textarea", full: true },
      ]} defaults={{ fecha_retiro: new Date().toISOString().slice(0, 10), estado_retiro_id: 1 }} submitLabel="Crear retiro" onSubmit={submit} /></div>
    </>
  );
}

export function OffboardingDetailPage({ offboardingId }: { offboardingId: string }) {
  const { data: rows, loading, error, reload } = useApiData<Offboarding[]>("/offboarding", []);
  const data = rows.find((row) => row.id === Number(offboardingId)) ?? null;
  const [actionError, setActionError] = useState<string | null>(null);
  async function action(path: string, payload: Record<string, unknown>) {
    setActionError(null);
    try {
      await apiRequest<ContractSettlement | Offboarding>(path, { method: "POST", body: JSON.stringify(payload) });
      await reload();
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "No fue posible registrar la accion.");
    }
  }
  return (
    <>
      <PageHeader eyebrow="Retiros" title={`Retiro ${offboardingId}`} description="Checklist de salida, liquidacion final y aprobacion contable." actions={<Link className="button" href="/offboarding">Volver</Link>} />
      {error ? <ErrorState message={error} /> : loadingText(loading)}
      {actionError ? <ErrorState message={actionError} /> : null}
      {data ? <div className="grid-2">
        <div className="card" style={{ padding: 18 }}>
          <StatusBadge items={catalogs.offboardingStatuses} id={data.status_id} />
          <div className="detail-list" style={{ marginTop: 16 }}>
            <div className="detail-item"><span>Empleado</span><strong>{data.employee_id}</strong></div>
            <div className="detail-item"><span>Contrato</span><strong>{data.contract_id}</strong></div>
            <div className="detail-item"><span>Fecha retiro</span><strong>{formatDate(data.withdrawal_date)}</strong></div>
            <div className="detail-item"><span>Motivo</span><strong>{catalogName(catalogs.withdrawalReasons, data.reason_id)}</strong></div>
          </div>
          <h3>Checklist de salida</h3>
          <ChecklistSection items={[
            { label: "Examen medico de retiro", done: data.exit_exam_completed },
            { label: "Implementos entregados", done: data.equipment_returned },
            { label: "Dotacion entregada", done: data.uniforms_returned },
          ]} />
          <button className="button primary" style={{ marginTop: 14 }} type="button" onClick={() => void action(`/offboarding/${offboardingId}/exit-checklist`, { examen_retiro_realizado: true, implementos_entregados: true, dotacion_entregada: true, observaciones: "Checklist completado desde SGRH" })}>Completar checklist</button>
        </div>
        <div className="card" style={{ padding: 18 }}>
          <h3 style={{ marginTop: 0 }}>Liquidacion final</h3>
          <EntityForm fields={[
            { name: "vacaciones", label: "Vacaciones", type: "number", step: "1000" },
            { name: "prima", label: "Prima", type: "number", step: "1000" },
            { name: "cesantias", label: "Cesantias", type: "number", step: "1000" },
            { name: "intereses_cesantias", label: "Intereses cesantias", type: "number", step: "1000" },
            { name: "deducciones", label: "Deducciones", type: "number", step: "1000" },
            { name: "estado_liquidacion_id", label: "Estado", type: "select", options: catalogs.settlementStatuses },
            { name: "observaciones", label: "Observaciones", type: "textarea", full: true },
          ]} defaults={{ vacaciones: 0, prima: 0, cesantias: 0, intereses_cesantias: 0, deducciones: 0, estado_liquidacion_id: 1 }} submitLabel="Generar liquidacion" onSubmit={(values) => action(`/offboarding/${offboardingId}/contract-settlement`, { ...values, vacaciones: Number(values.vacaciones || 0), prima: Number(values.prima || 0), cesantias: Number(values.cesantias || 0), intereses_cesantias: Number(values.intereses_cesantias || 0), deducciones: Number(values.deducciones || 0), estado_liquidacion_id: Number(values.estado_liquidacion_id) })} />
          <button className="button" type="button" onClick={() => void action(`/offboarding/${offboardingId}/contract-settlement/approve`, { aprobado_por: 1, observacion: "Aprobado desde SGRH" })}>Aprobar liquidacion</button>
        </div>
      </div> : null}
    </>
  );
}

export function TrainingActivitiesPage() {
  const { data, loading, error } = useApiData<TrainingActivity[]>("/training/activities", []);
  const [show, setShow] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  async function create(values: FormValues) {
    try {
      await apiRequest("/training/activities", { method: "POST", body: JSON.stringify({ ...values, type_id: Number(values.type_id), status_id: Number(values.status_id) }) });
      window.location.reload();
    } catch (err) {
      setFormError(err instanceof Error ? err.message : "No fue posible crear la actividad.");
    }
  }
  return (
    <>
      <PageHeader eyebrow="Capacitacion" title="Actividades" description="Inducciones, reinducciones, capacitaciones y evidencias de asistencia." actions={<button className="button primary" onClick={() => setShow((v) => !v)}><Plus size={16} /> Nueva actividad</button>} />
      {show ? <div className="card" style={{ padding: 18, marginBottom: 16 }}>{formError ? <ErrorState message={formError} /> : null}<EntityForm fields={[
        { name: "name", label: "Nombre", required: true },
        { name: "type_id", label: "Tipo", type: "select", options: catalogs.trainingTypes, required: true },
        { name: "status_id", label: "Estado", type: "select", options: catalogs.trainingStatuses, required: true },
        { name: "scheduled_date", label: "Fecha programada", type: "date", required: true },
        { name: "description", label: "Descripcion", type: "textarea", full: true },
      ]} defaults={{ scheduled_date: new Date().toISOString().slice(0, 10), type_id: 1, status_id: 1 }} submitLabel="Crear actividad" onSubmit={create} /></div> : null}
      {error ? <ErrorState message={error} /> : loadingText(loading)}
      {!loading && !error ? <div className="card"><DataTable data={data} columns={[
        { header: "Actividad", cell: (row) => <strong>{row.name}</strong> },
        { header: "Tipo", cell: (row) => catalogName(catalogs.trainingTypes, row.type_id) },
        { header: "Estado", cell: (row) => <StatusBadge items={catalogs.trainingStatuses} id={row.status_id} /> },
        { header: "Fecha", cell: (row) => formatDate(row.scheduled_date) },
      ]} /></div> : null}
    </>
  );
}

export function TrainingAnnualPlanPage() {
  return <ReadOnlyReportPage title="Plan anual de capacitacion" endpoint="/training/annual-plan" description="Listado de planes anuales registrados en el backend." />;
}

export function EvaluationsPage() {
  const { data, loading, error } = useApiData<Evaluation[]>("/evaluations", []);
  const [show, setShow] = useState(false);
  async function create(values: FormValues) {
    await apiRequest("/evaluations", { method: "POST", body: JSON.stringify({ ...values, empleado_id: Number(values.empleado_id), estado_evaluacion_id: Number(values.estado_evaluacion_id), puntaje: values.puntaje ? Number(values.puntaje) : null }) });
    window.location.reload();
  }
  return (
    <>
      <PageHeader eyebrow="Desempeno" title="Evaluaciones" description="Evaluaciones de periodo de prueba, anuales y planes de mejora." actions={<button className="button primary" onClick={() => setShow((v) => !v)}><Plus size={16} /> Nueva evaluacion</button>} />
      {show ? <div className="card" style={{ padding: 18, marginBottom: 16 }}><EntityForm fields={[
        { name: "empleado_id", label: "ID empleado", type: "number", required: true },
        { name: "estado_evaluacion_id", label: "Estado", type: "select", options: catalogs.evaluationStatuses, required: true },
        { name: "tipo_evaluacion", label: "Tipo evaluacion", required: true },
        { name: "fecha_evaluacion", label: "Fecha", type: "date", required: true },
        { name: "puntaje", label: "Puntaje", type: "number", step: "0.1" },
        { name: "observaciones", label: "Observaciones", type: "textarea", full: true },
      ]} defaults={{ estado_evaluacion_id: 1, fecha_evaluacion: new Date().toISOString().slice(0, 10) }} submitLabel="Crear evaluacion" onSubmit={create} /></div> : null}
      {error ? <ErrorState message={error} /> : loadingText(loading)}
      {!loading && !error ? <div className="card"><DataTable data={data} columns={[
        { header: "Empleado", cell: (row) => `Empleado ${row.employee_id}` },
        { header: "Tipo", cell: (row) => row.evaluation_type },
        { header: "Estado", cell: (row) => <StatusBadge items={catalogs.evaluationStatuses} id={row.status_id} /> },
        { header: "Fecha", cell: (row) => formatDate(row.evaluation_date) },
        { header: "Puntaje", cell: (row) => row.score ?? "N/D" },
      ]} /></div> : null}
    </>
  );
}

export function CertificatesPage() {
  const { data, loading, error } = useApiData<Certificate[]>("/certificates", []);
  const [show, setShow] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  async function create(values: FormValues) {
    await apiRequest("/certificates", { method: "POST", body: JSON.stringify({ empleado_id: Number(values.empleado_id), tipo_certificacion_id: Number(values.tipo_certificacion_id), estado_certificacion_id: Number(values.estado_certificacion_id), observacion: values.observacion || null }) });
    window.location.reload();
  }
  async function generate(id: number) {
    try {
      const doc = await apiRequest<{ id: number; original_filename: string }>(`/certificates/${id}/generate`, { method: "POST" });
      await downloadDocument(doc.id, doc.original_filename);
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "No fue posible generar el certificado.");
    }
  }
  return (
    <>
      <PageHeader eyebrow="Certificados" title="Solicitudes de certificacion" description="Generacion y descarga de certificados laborales y salariales." actions={<button className="button primary" onClick={() => setShow((v) => !v)}><Plus size={16} /> Nueva solicitud</button>} />
      {actionError ? <ErrorState message={actionError} /> : null}
      {show ? <div className="card" style={{ padding: 18, marginBottom: 16 }}><EntityForm fields={[
        { name: "empleado_id", label: "ID empleado", type: "number", required: true },
        { name: "tipo_certificacion_id", label: "Tipo", type: "select", options: catalogs.certificateTypes, required: true },
        { name: "estado_certificacion_id", label: "Estado", type: "select", options: catalogs.certificateStatuses, required: true },
        { name: "observacion", label: "Observacion", type: "textarea", full: true },
      ]} defaults={{ tipo_certificacion_id: 1, estado_certificacion_id: 1 }} submitLabel="Crear solicitud" onSubmit={create} /></div> : null}
      {error ? <ErrorState message={error} /> : loadingText(loading)}
      {!loading && !error ? <div className="card"><DataTable data={data} columns={[
        { header: "Solicitud", cell: (row) => <strong>CERT-{row.id}</strong> },
        { header: "Empleado", cell: (row) => `Empleado ${row.employee_id}` },
        { header: "Tipo", cell: (row) => catalogName(catalogs.certificateTypes, row.certificate_type_id) },
        { header: "Estado", cell: (row) => <StatusBadge items={catalogs.certificateStatuses} id={row.status_id} /> },
        { header: "Acciones", cell: (row) => <button className="button" onClick={() => void generate(row.id)}><Download size={14} /> Generar/descargar</button> },
      ]} /></div> : null}
    </>
  );
}

export function ReportsPage() {
  const modules = ["employees", "recruitment", "affiliations", "payroll", "offboarding", "training", "evaluations", "certificates"];
  return (
    <>
      <PageHeader eyebrow="Reportes" title="Reportes operativos" description="Consultas agregadas por modulo para gerencia y administracion." />
      <div className="grid-2">
        {modules.map((module) => <ReportCard module={module} key={module} />)}
      </div>
    </>
  );
}

function ReportCard({ module }: { module: string }) {
  const { data, loading, error } = useApiData<Record<string, unknown>>(`/reports/${module}`, {});
  return (
    <div className="card" style={{ padding: 16 }}>
      <h3 style={{ marginTop: 0, textTransform: "capitalize" }}>{module}</h3>
      {loading ? "Cargando..." : null}
      {error ? <span className="muted">{error}</span> : null}
      {!loading && !error ? <pre className="alert" style={{ whiteSpace: "pre-wrap" }}>{JSON.stringify(data, null, 2)}</pre> : null}
    </div>
  );
}

export function AuditPage() {
  const [page, setPage] = useState(1);
  const [action, setAction] = useState("");
  const [entity, setEntity] = useState("");
  const pageSize = 20;
  const query = { page, page_size: pageSize, action, entity };
  const { data, loading, error, reload } = useApiData<PaginatedResponse<AuditRecord>>(
    "/audit",
    { items: [], total: 0, page: 1, page_size: pageSize },
    query,
  );
  const pageCount = Math.max(1, Math.ceil(data.total / data.page_size));

  function updateFilter(setter: (value: string) => void, value: string) {
    setter(value);
    setPage(1);
  }

  return (
    <>
      <PageHeader
        eyebrow="Trazabilidad"
        title="Auditoria"
        description="Eventos criticos registrados por el backend."
        actions={<button className="button" type="button" onClick={() => void reload()}><RefreshCcw size={16} /> Refrescar</button>}
      />
      <div className="card" style={{ padding: 18, marginBottom: 16 }}>
        <div className="grid-2">
          <label className="field">
            <span className="label">Accion</span>
            <input className="input" value={action} placeholder="login, create, update..." onChange={(event) => updateFilter(setAction, event.target.value)} />
          </label>
          <label className="field">
            <span className="label">Entidad</span>
            <input className="input" value={entity} placeholder="usuario, empleado, candidato..." onChange={(event) => updateFilter(setEntity, event.target.value)} />
          </label>
        </div>
        <div className="actions" style={{ marginTop: 12 }}>
          <span className="muted">{data.total} eventos encontrados</span>
          {(action || entity) ? (
            <button className="button" type="button" onClick={() => { setAction(""); setEntity(""); setPage(1); }}>
              Limpiar filtros
            </button>
          ) : null}
        </div>
      </div>
      {error ? <ErrorState message={error} /> : loadingText(loading)}
      {!loading && !error ? (
        <>
          <div className="card">
            <DataTable
              data={data.items}
              emptyTitle="Sin eventos de auditoria"
              emptyDescription="No hay registros para los filtros seleccionados."
              columns={[
                { header: "Fecha", cell: (row) => formatDateTime(row.event_date) },
                { header: "Usuario", cell: (row) => row.user_id ? `Usuario ${row.user_id}` : "Sistema" },
                { header: "Accion", cell: (row) => <strong>{row.action}</strong> },
                { header: "Entidad", cell: (row) => `${row.entity}${row.record_id ? ` #${row.record_id}` : ""}` },
                { header: "Detalle", cell: (row) => row.detail || "Sin detalle" },
              ]}
            />
          </div>
          <div className="actions" style={{ justifyContent: "space-between", marginTop: 16 }}>
            <button className="button" type="button" disabled={page <= 1} onClick={() => setPage((value) => Math.max(1, value - 1))}>Anterior</button>
            <span className="muted">Pagina {data.page} de {pageCount}</span>
            <button className="button" type="button" disabled={page >= pageCount} onClick={() => setPage((value) => Math.min(pageCount, value + 1))}>Siguiente</button>
          </div>
        </>
      ) : null}
    </>
  );
}

export function AdminUsersPage() {
  const { data, loading, error } = useApiData<AdminUser[]>("/admin/users", []);
  const [show, setShow] = useState(false);
  async function create(values: FormValues) {
    const roleCode = catalogs.roles.find((role) => role.id === Number(values.role_code))?.code ?? "RRHH";
    await apiRequest("/admin/users", { method: "POST", body: JSON.stringify({ username: values.username, password: values.password, full_name: values.full_name || null, active: true, role_codes: [roleCode] }) });
    window.location.reload();
  }
  return (
    <>
      <PageHeader eyebrow="Administracion" title="Usuarios" description="Gestion basica de usuarios internos y roles RBAC." actions={<button className="button primary" onClick={() => setShow((v) => !v)}><Plus size={16} /> Nuevo usuario</button>} />
      {show ? <div className="card" style={{ padding: 18, marginBottom: 16 }}><EntityForm fields={[
        { name: "username", label: "Usuario", required: true },
        { name: "password", label: "Contrasena", type: "password", required: true },
        { name: "full_name", label: "Nombre completo" },
        { name: "role_code", label: "Rol", type: "select", options: catalogs.roles, required: true },
      ]} defaults={{ role_code: 1 }} submitLabel="Crear usuario" onSubmit={create} /></div> : null}
      {error ? <ErrorState message={error} /> : loadingText(loading)}
      {!loading && !error ? <div className="card"><DataTable data={data} columns={[
        { header: "Usuario", cell: (row) => <strong>{row.username}</strong> },
        { header: "Nombre", cell: (row) => row.full_name || "Sin nombre" },
        { header: "Roles", cell: (row) => row.roles.join(", ") || "Sin roles" },
        { header: "Permisos", cell: (row) => row.permissions.length },
      ]} /></div> : null}
    </>
  );
}

function ReadOnlyReportPage({ title, endpoint, description }: { title: string; endpoint: string; description: string }) {
  const { data, loading, error } = useApiData<unknown[]>(endpoint, []);
  return (
    <>
      <PageHeader title={title} description={description} />
      {error ? <ErrorState message={error} /> : loadingText(loading)}
      {!loading && !error ? <pre className="card" style={{ padding: 18, whiteSpace: "pre-wrap" }}>{JSON.stringify(data, null, 2)}</pre> : null}
    </>
  );
}
