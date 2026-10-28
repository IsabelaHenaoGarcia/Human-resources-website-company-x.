import { AlertTriangle, Inbox } from "lucide-react";

export function EmptyState({ title, description }: { title: string; description?: string }) {
  return (
    <div className="card" style={{ padding: 28, textAlign: "center" }}>
      <Inbox size={28} color="#64748b" />
      <h3 style={{ margin: "10px 0 4px" }}>{title}</h3>
      {description ? <p className="muted" style={{ margin: 0 }}>{description}</p> : null}
    </div>
  );
}

export function ErrorState({ message }: { message: string }) {
  return (
    <div className="alert error">
      <div className="actions">
        <AlertTriangle size={18} />
        <strong>{message}</strong>
      </div>
    </div>
  );
}
