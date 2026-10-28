"use client";

import { useMemo, useState } from "react";
import type { FieldConfig, FormValues } from "@/lib/forms";
import { initialValues } from "@/lib/forms";

export function EntityForm({
  fields,
  defaults,
  submitLabel = "Guardar",
  onSubmit,
  onCancel,
  busy,
}: {
  fields: FieldConfig[];
  defaults?: Record<string, unknown>;
  submitLabel?: string;
  onSubmit: (values: FormValues) => void | Promise<void>;
  onCancel?: () => void;
  busy?: boolean;
}) {
  const baseValues = useMemo(() => initialValues(fields, defaults), [fields, defaults]);
  const [values, setValues] = useState<FormValues>(baseValues);

  function setField(name: string, value: string | boolean) {
    setValues((current) => ({ ...current, [name]: value }));
  }

  return (
    <form
      className="section"
      onSubmit={(event) => {
        event.preventDefault();
        void onSubmit(values);
      }}
    >
      <div className="form-grid">
        {fields.map((field) => (
          <label className="field" key={field.name} style={field.full ? { gridColumn: "1 / -1" } : undefined}>
            <span className="label">{field.label}</span>
            {field.type === "textarea" ? (
              <textarea
                className="textarea"
                placeholder={field.placeholder}
                required={field.required}
                value={String(values[field.name] ?? "")}
                onChange={(event) => setField(field.name, event.target.value)}
              />
            ) : field.type === "select" ? (
              <select
                className="select"
                required={field.required}
                value={String(values[field.name] ?? "")}
                onChange={(event) => setField(field.name, event.target.value)}
              >
                {field.options?.map((option) => (
                  <option key={option.id} value={option.id}>
                    {option.name}
                  </option>
                ))}
              </select>
            ) : field.type === "checkbox" ? (
              <span className="actions" style={{ minHeight: 38 }}>
                <input
                  checked={Boolean(values[field.name])}
                  type="checkbox"
                  onChange={(event) => setField(field.name, event.target.checked)}
                />
                <span className="muted">Si</span>
              </span>
            ) : (
              <input
                className="input"
                min={field.min}
                placeholder={field.placeholder}
                required={field.required}
                step={field.step}
                type={field.type ?? "text"}
                value={String(values[field.name] ?? "")}
                onChange={(event) => setField(field.name, event.target.value)}
              />
            )}
          </label>
        ))}
      </div>
      <div className="form-actions">
        {onCancel ? (
          <button className="button" type="button" onClick={onCancel}>
            Cancelar
          </button>
        ) : null}
        <button className="button primary" disabled={busy} type="submit">
          {busy ? "Guardando..." : submitLabel}
        </button>
      </div>
    </form>
  );
}
