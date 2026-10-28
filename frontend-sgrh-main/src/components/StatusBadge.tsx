import { catalogCode, catalogName } from "@/lib/catalogs";
import type { CatalogItem } from "@/lib/types";

const successCodes = new Set(["active", "approved", "completed", "hired", "generated", "delivered", "closed", "paid"]);
const warningCodes = new Set(["draft", "pending", "in_process", "in_progress", "in_review", "scheduled", "reviewed", "requested"]);
const dangerCodes = new Set(["inactive", "retired", "rejected", "cancelled"]);

export function StatusBadge({ items, id, label }: { items?: CatalogItem[]; id?: number | null; label?: string }) {
  const code = items ? catalogCode(items, id) : "neutral";
  const text = label ?? (items ? catalogName(items, id) : "Sin estado");
  let tone = "neutral";
  if (successCodes.has(code)) tone = "success";
  if (warningCodes.has(code)) tone = "warning";
  if (dangerCodes.has(code)) tone = "danger";
  if (code === "on_leave") tone = "info";
  return <span className={`badge ${tone}`}>{text}</span>;
}
