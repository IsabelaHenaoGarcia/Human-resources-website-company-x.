import { CheckCircle2, Clock, ShieldCheck } from "lucide-react";
import { formatDateTime } from "@/lib/format";

export function ChecklistSection({ items }: { items: { label: string; done: boolean; detail?: string }[] }) {
  return (
    <div className="checklist">
      {items.map((item) => (
        <div className="check-row" key={item.label}>
          <div>
            <strong>{item.label}</strong>
            {item.detail ? <div className="muted">{item.detail}</div> : null}
          </div>
          <span className={`badge ${item.done ? "success" : "warning"}`}>{item.done ? "Listo" : "Pendiente"}</span>
        </div>
      ))}
    </div>
  );
}

export function ApprovalPanel({
  status,
  approvedBy,
  approvedAt,
  comment,
}: {
  status: React.ReactNode;
  approvedBy?: number | null;
  approvedAt?: string | null;
  comment?: string | null;
}) {
  return (
    <div className="card" style={{ padding: 16 }}>
      <div className="actions" style={{ justifyContent: "space-between" }}>
        <div className="actions">
          <ShieldCheck size={20} color="#545f72" />
          <strong>Panel de aprobacion</strong>
        </div>
        {status}
      </div>
      <div className="detail-list" style={{ marginTop: 14 }}>
        <div className="detail-item">
          <span>Aprobador</span>
          <strong>{approvedBy ? `Usuario ${approvedBy}` : "Pendiente"}</strong>
        </div>
        <div className="detail-item">
          <span>Fecha</span>
          <strong>{formatDateTime(approvedAt)}</strong>
        </div>
        <div className="detail-item" style={{ gridColumn: "1 / -1" }}>
          <span>Observacion</span>
          <strong>{comment || "Sin observacion registrada"}</strong>
        </div>
      </div>
    </div>
  );
}

export function TimelinePanel({ items }: { items: { title: string; date?: string | null; detail?: string }[] }) {
  return (
    <div className="timeline">
      {items.map((item) => (
        <div className="timeline-item" key={item.title}>
          <div className="timeline-dot" />
          <div>
            <strong>{item.title}</strong>
            <div className="muted">
              <Clock size={13} style={{ verticalAlign: "-2px" }} /> {formatDateTime(item.date)} {item.detail ? `- ${item.detail}` : ""}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

export function ConfirmDialog({
  title,
  description,
  confirmLabel = "Confirmar",
  onConfirm,
}: {
  title: string;
  description?: string;
  confirmLabel?: string;
  onConfirm: () => void;
}) {
  return (
    <div className="alert">
      <div className="actions" style={{ justifyContent: "space-between" }}>
        <div>
          <strong>{title}</strong>
          {description ? <div className="muted">{description}</div> : null}
        </div>
        <button className="button danger" type="button" onClick={onConfirm}>
          <CheckCircle2 size={16} />
          {confirmLabel}
        </button>
      </div>
    </div>
  );
}
