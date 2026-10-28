"use client";

import { Download, FileUp, Paperclip } from "lucide-react";
import { useState } from "react";
import { apiRequest, downloadDocument, uploadDocument } from "@/lib/api-client";
import { catalogs } from "@/lib/catalogs";
import { fileSize, formatDateTime } from "@/lib/format";
import type { DocumentRecord } from "@/lib/types";

type LinkTarget = "employees" | "candidates" | "contracts" | "affiliations" | "offboarding";

export function FileUploader({
  target,
  targetId,
  onUploaded,
}: {
  target?: LinkTarget;
  targetId?: number;
  onUploaded?: (document: DocumentRecord) => void;
}) {
  const [supportTypeId, setSupportTypeId] = useState(catalogs.supportDocumentTypes[0].id);
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  async function submit() {
    if (!file) return;
    setBusy(true);
    setMessage(null);
    try {
      const document = await uploadDocument(file);
      if (target && targetId) {
        await apiRequest(`/${target}/${targetId}/documents`, {
          method: "POST",
          body: JSON.stringify({
            document_id: document.id,
            support_document_type_id: supportTypeId,
            observation: "Cargado desde frontend SGRH",
          }),
        });
      }
      setMessage("Documento cargado y vinculado correctamente.");
      onUploaded?.(document);
      setFile(null);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "No fue posible cargar el documento.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="section">
      <div className="dropzone">
        <FileUp size={28} color="#545f72" />
        <strong>Selecciona un soporte</strong>
        <span className="muted">PDF, JPG, JPEG o PNG. Maximo 10 MB.</span>
        <input
          className="input"
          type="file"
          accept=".pdf,.jpg,.jpeg,.png"
          onChange={(event) => setFile(event.target.files?.[0] ?? null)}
        />
      </div>
      <div className="grid-2">
        <label className="field">
          <span className="label">Tipo de soporte</span>
          <select className="select" value={supportTypeId} onChange={(event) => setSupportTypeId(Number(event.target.value))}>
            {catalogs.supportDocumentTypes.map((item) => (
              <option key={item.id} value={item.id}>
                {item.name}
              </option>
            ))}
          </select>
        </label>
        <div className="field">
          <span className="label">Archivo</span>
          <div className="alert">{file ? `${file.name} (${fileSize(file.size)})` : "Sin archivo seleccionado"}</div>
        </div>
      </div>
      {message ? <div className="alert">{message}</div> : null}
      <div className="form-actions">
        <button className="button primary" disabled={!file || busy} type="button" onClick={submit}>
          {busy ? "Cargando..." : "Cargar documento"}
        </button>
      </div>
    </div>
  );
}

export function FileList({ documents }: { documents: DocumentRecord[] }) {
  if (!documents.length) {
    return <div className="alert muted">El backend no expone listado de documentos vinculados; aqui se muestran los cargados en esta sesion.</div>;
  }

  return (
    <div className="section">
      {documents.map((document) => (
        <div className="check-row" key={document.id}>
          <div className="actions">
            <Paperclip size={18} color="#545f72" />
            <div>
              <strong>{document.original_filename}</strong>
              <div className="muted">{fileSize(document.file_size)} - {formatDateTime(document.created_at)}</div>
            </div>
          </div>
          <button
            className="button"
            type="button"
            onClick={() => void downloadDocument(document.id, document.original_filename)}
          >
            <Download size={16} />
            Descargar
          </button>
        </div>
      ))}
    </div>
  );
}
