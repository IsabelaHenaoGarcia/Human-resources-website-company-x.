import type { CatalogItem } from "./types";

export type FieldType = "text" | "email" | "number" | "date" | "textarea" | "select" | "checkbox" | "password";

export type FieldConfig = {
  name: string;
  label: string;
  type?: FieldType;
  required?: boolean;
  placeholder?: string;
  options?: CatalogItem[];
  full?: boolean;
  min?: number;
  step?: string;
};

export type FormValues = Record<string, string | boolean>;

export function initialValues(fields: FieldConfig[], defaults?: Record<string, unknown>): FormValues {
  return fields.reduce<FormValues>((acc, field) => {
    const value = defaults?.[field.name];
    if (field.type === "checkbox") {
      acc[field.name] = Boolean(value);
    } else if (value === undefined || value === null) {
      acc[field.name] = field.type === "select" ? String(field.options?.[0]?.id ?? "") : "";
    } else {
      acc[field.name] = String(value);
    }
    return acc;
  }, {});
}

export function cleanPayload(values: FormValues, numberFields: string[] = [], booleanFields: string[] = []) {
  const payload: Record<string, string | number | boolean | null> = {};
  for (const [key, value] of Object.entries(values)) {
    if (booleanFields.includes(key)) {
      payload[key] = Boolean(value);
    } else if (numberFields.includes(key)) {
      payload[key] = value === "" ? 0 : Number(value);
    } else {
      payload[key] = value === "" ? null : String(value);
    }
  }
  return payload;
}
