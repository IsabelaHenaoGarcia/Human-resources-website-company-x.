"use client";

import { ClipboardList, FileText, Plus } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMemo, useState } from "react";
import { DataTable } from "@/components/DataTable";
import { EntityForm } from "@/components/EntityForm";
import { FileList, FileUploader } from "@/components/FileTools";
import { PageHeader } from "@/components/PageHeader";
import { ErrorState } from "@/components/States";
import { StatusBadge } from "@/components/StatusBadge";
import { ChecklistSection } from "@/components/WorkflowPanels";
import { apiRequest } from "@/lib/api-client";
import { catalogName, catalogs, defaultId } from "@/lib/catalogs";
import { cleanPayload, type FieldConfig, type FormValues } from "@/lib/forms";
import { formatDate, formatDateTime, formatMoney } from "@/lib/format";
import type { Candidate, Contract, DocumentRecord, PaginatedResponse } from "@/lib/types";
import { loadingText, useApiData } from "./hooks";

const candidateFields: FieldConfig[] = [
  { name: "full_name", label: "Nombre completo", required: true },
  { name: "document_type_id", label: "Tipo documento", type: "select", options: catalogs.documentTypes, required: true },
  { name: "document_number", label: "Numero documento", required: true },
  { name: "candidate_status_id", label: "Estado", type: "select", options: catalogs.candidateStatuses, required: true },
  { name: "position_applied", label: "Cargo aspirado" },
  { name: "email", label: "Correo", type: "email" },
  { name: "phone", label: "Telefono" },
  { name: "interview_result_summary", label: "Resumen entrevista", type: "textarea", full: true },
];

export function CandidatesListPage() {
  const [q, setQ] = useState("");
  const query = useMemo(() => ({ q, page: 1, page_size: 20 }), [q]);
  const { data, loading, error } = useApiData<PaginatedResponse<Candidate>>("/recruitment/candidates", { items: [], page: 1, page_size: 20, total: 0 }, query);

  return (
    <>
      <PageHeader
        eyebrow="Seleccion"
        title="Candidatos"
        description="Seguimiento del embudo de seleccion, verificaciones, pruebas, entrevistas y examen ocupacional."
        actions={<Link className="button primary" href="/recruitment/candidates/new"><Plus size={16} /> Nuevo candidato</Link>}
      />
      <div className="card toolbar">
        <input className="input" style={{ maxWidth: 360 }} placeholder="Buscar por nombre o documento" value={q} onChange={(e) => setQ(e.target.value)} />
        <Link className="button" href="/recruitment/contracts"><FileText size={16} /> Contratos</Link>
      </div>
      {error ? <ErrorState message={error} /> : loadingText(loading)}
      {!loading && !error ? (
        <div className="card">
          <DataTable
            data={data.items}
            columns={[
              { header: "Candidato", cell: (row) => <Link href={`/recruitment/candidates/${row.id}`}><strong>{row.full_name}</strong><div className="muted">{row.position_applied || "Cargo no definido"}</div></Link> },
              { header: "Documento", cell: (row) => <span className="tabular">{catalogName(catalogs.documentTypes, row.document_type_id)} {row.document_number}</span> },
              { header: "Estado", cell: (row) => <StatusBadge items={catalogs.candidateStatuses} id={row.candidate_status_id} /> },
              { header: "Referencias", cell: (row) => <StatusBadge label={row.references_verified ? "Verificadas" : "Pendientes"} /> },
              { header: "Creado", cell: (row) => formatDate(row.created_at) },
            ]}
          />
        </div>
      ) : null}
    </>
  );
}

export function CandidateFormPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(values: FormValues) {
    setBusy(true);
    setError(null);
    try {
      const candidate = await apiRequest<Candidate>("/recruitment/candidates", {
        method: "POST",
        body: JSON.stringify(cleanPayload(values, ["document_type_id", "candidate_status_id"])),
      });
      router.push(`/recruitment/candidates/${candidate.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "No fue posible crear el candidato.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <PageHeader eyebrow="Seleccion" title="Nuevo candidato" description="Registra la informacion base para iniciar seguimiento de seleccion." />
      {error ? <ErrorState message={error} /> : null}
      <div className="card" style={{ padding: 20 }}>
        <EntityForm
          fields={candidateFields}
          defaults={{ document_type_id: 1, candidate_status_id: defaultId(catalogs.candidateStatuses, "draft") }}
          submitLabel="Crear candidato"
          busy={busy}
          onCancel={() => router.back()}
          onSubmit={submit}
        />
      </div>
    </>
  );
}

export function CandidateDetailPage({ candidateId }: { candidateId: string }) {
  const { data: candidate, loading, error, setData } = useApiData<Candidate | null>(`/recruitment/candidates/${candidateId}`, null);
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [actionError, setActionError] = useState<string | null>(null);

  async function submitAction(path: string, payload: Record<string, unknown>) {
    setActionError(null);
    try {
      const updated = await apiRequest<Candidate | { id: number }>(path, { method: "POST", body: JSON.stringify(payload) });
      if ("full_name" in updated) setData(updated);
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "No fue posible registrar la accion.");
    }
  }

  return (
    <>
      <PageHeader
        eyebrow="Seleccion"
        title={candidate?.full_name ?? "Candidato"}
        description="Control de verificaciones, pruebas, entrevista, examen ocupacional y soportes documentales."
        actions={<Link className="button" href="/recruitment/candidates">Volver</Link>}
      />
      {error ? <ErrorState message={error} /> : loadingText(loading)}
      {actionError ? <ErrorState message={actionError} /> : null}
      {candidate ? (
        <div className="grid-2">
          <div className="section">
            <div className="card" style={{ padding: 18 }}>
              <div className="actions" style={{ justifyContent: "space-between" }}>
                <h2 style={{ margin: 0 }}>{candidate.position_applied || "Cargo no definido"}</h2>
                <StatusBadge items={catalogs.candidateStatuses} id={candidate.candidate_status_id} />
              </div>
              <div className="detail-list" style={{ marginTop: 16 }}>
                <div className="detail-item"><span>Documento</span><strong>{catalogName(catalogs.documentTypes, candidate.document_type_id)} {candidate.document_number}</strong></div>
                <div className="detail-item"><span>Correo</span><strong>{candidate.email || "No registrado"}</strong></div>
                <div className="detail-item"><span>Telefono</span><strong>{candidate.phone || "No registrado"}</strong></div>
                <div className="detail-item"><span>Examen ocupacional</span><strong>{candidate.occupational_exam_result || "Pendiente"}</strong></div>
              </div>
            </div>
            <div className="card" style={{ padding: 18 }}>
              <h3 style={{ marginTop: 0 }}>Checklist de seleccion</h3>
              <ChecklistSection
                items={[
                  { label: "Referencias verificadas", done: candidate.references_verified },
                  { label: "Antecedentes verificados", done: candidate.background_verified },
                  { label: "Entrevista registrada", done: Boolean(candidate.interview_result_summary) },
                  { label: "Examen ocupacional", done: Boolean(candidate.occupational_exam_result), detail: candidate.occupational_exam_date ? formatDate(candidate.occupational_exam_date) : undefined },
                ]}
              />
            </div>
            <div className="card" style={{ padding: 18 }}>
              <h3 style={{ marginTop: 0 }}>Documentos</h3>
              <FileUploader target="candidates" targetId={Number(candidateId)} onUploaded={(document) => setDocuments((current) => [document, ...current])} />
              <FileList documents={documents} />
            </div>
          </div>
          <div className="section">
            <div className="card" style={{ padding: 18 }}>
              <h3 style={{ marginTop: 0 }}>Registrar verificaciones</h3>
              <div className="form-actions" style={{ justifyContent: "flex-start" }}>
                <button className="button primary" type="button" onClick={() => void submitAction(`/recruitment/candidates/${candidateId}/verifications`, { referencias_verificadas: true, antecedentes_verificados: true, observaciones: "Validado desde SGRH" })}>
                  <ClipboardList size={16} /> Marcar verificadas
                </button>
              </div>
            </div>
            <div className="card" style={{ padding: 18 }}>
              <EntityForm
                fields={[
                  { name: "tipo_prueba", label: "Tipo de prueba", required: true },
                  { name: "resultado", label: "Resultado", required: true },
                  { name: "observaciones", label: "Observaciones", type: "textarea", full: true },
                ]}
                submitLabel="Registrar prueba"
                onSubmit={(values) => submitAction(`/recruitment/candidates/${candidateId}/tests`, values)}
              />
            </div>
            <div className="card" style={{ padding: 18 }}>
              <EntityForm
                fields={[
                  { name: "fecha", label: "Fecha examen", type: "date", required: true },
                  { name: "resultado", label: "Resultado", required: true },
                  { name: "observaciones", label: "Observaciones", type: "textarea", full: true },
                ]}
                submitLabel="Registrar examen"
                onSubmit={(values) => submitAction(`/recruitment/candidates/${candidateId}/occupational-exam`, values)}
              />
            </div>
            <div className="card" style={{ padding: 18 }}>
              <EntityForm
                fields={[
                  { name: "fecha_hora", label: "Fecha y hora", type: "text", placeholder: "2026-05-18T09:00:00", required: true },
                  { name: "entrevistador", label: "Entrevistador", required: true },
                  { name: "estado_entrevista_id", label: "Estado", type: "select", options: catalogs.interviewStatuses, required: true },
                  { name: "resultado", label: "Resultado" },
                  { name: "observaciones", label: "Observaciones", type: "textarea", full: true },
                ]}
                defaults={{ estado_entrevista_id: defaultId(catalogs.interviewStatuses, "scheduled") }}
                submitLabel="Crear entrevista"
                onSubmit={(values) => submitAction("/recruitment/interviews", { ...values, candidato_id: Number(candidateId), estado_entrevista_id: Number(values.estado_entrevista_id) })}
              />
            </div>
          </div>
        </div>
      ) : null}
    </>
  );
}

export function ContractsPage() {
  const { data, loading, error } = useApiData<Contract[]>("/recruitment/contracts", []);

  return (
    <>
      <PageHeader eyebrow="Contratacion" title="Contratos" description="Contratos registrados desde el proceso de vinculacion." actions={<Link className="button" href="/recruitment/candidates">Candidatos</Link>} />
      {error ? <ErrorState message={error} /> : loadingText(loading)}
      {!loading && !error ? (
        <div className="card">
          <DataTable
            data={data}
            columns={[
              { header: "Contrato", cell: (row) => <strong>CTR-{row.id}</strong> },
              { header: "Empleado", cell: (row) => `Empleado ${row.employee_id}` },
              { header: "Tipo", cell: (row) => catalogName(catalogs.contractTypes, row.contract_type_id) },
              { header: "Estado", cell: (row) => <StatusBadge items={catalogs.contractStatuses} id={row.contract_status_id} /> },
              { header: "Cargo", cell: (row) => row.position },
              { header: "Salario", cell: (row) => formatMoney(row.base_salary) },
              { header: "Inicio", cell: (row) => formatDate(row.start_date) },
              { header: "Creado", cell: (row) => formatDateTime(row.created_at) },
            ]}
          />
        </div>
      ) : null}
    </>
  );
}
