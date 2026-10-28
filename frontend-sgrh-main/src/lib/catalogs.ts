import type { CatalogItem } from "./types";

export const catalogs = {
  documentTypes: [
    { id: 1, code: "cc", name: "Cedula de ciudadania" },
    { id: 2, code: "ce", name: "Cedula de extranjeria" },
    { id: 3, code: "passport", name: "Pasaporte" },
  ],
  fileTypes: [
    { id: 1, code: "pdf", name: "PDF" },
    { id: 2, code: "jpg", name: "JPG" },
    { id: 3, code: "jpeg", name: "JPEG" },
    { id: 4, code: "png", name: "PNG" },
    { id: 5, code: "csv", name: "CSV" },
  ],
  supportDocumentTypes: [
    { id: 1, code: "cv", name: "Hoja de vida" },
    { id: 2, code: "id_copy", name: "Copia de documento" },
    { id: 3, code: "military_booklet", name: "Libreta militar" },
    { id: 4, code: "education_certificate", name: "Certificado academico" },
    { id: 5, code: "training_certificate", name: "Certificado de capacitacion" },
    { id: 6, code: "work_experience_letter", name: "Carta laboral" },
    { id: 7, code: "eps_certificate", name: "Certificado EPS" },
    { id: 8, code: "pension_certificate", name: "Certificado pension" },
    { id: 9, code: "beneficiary_support", name: "Soporte beneficiario" },
    { id: 10, code: "occupational_exam_result", name: "Examen ocupacional" },
    { id: 11, code: "contract", name: "Contrato" },
    { id: 12, code: "affiliation_proof", name: "Soporte de afiliacion" },
    { id: 13, code: "payroll_report_export", name: "Reporte de nomina" },
    { id: 14, code: "pay_slip", name: "Desprendible de pago" },
    { id: 15, code: "contract_settlement", name: "Liquidacion de contrato" },
    { id: 16, code: "withdrawal_letter", name: "Carta de retiro" },
    { id: 17, code: "employment_certificate", name: "Certificado laboral" },
    { id: 18, code: "induction_record", name: "Registro de induccion" },
    { id: 19, code: "training_attendance_evidence", name: "Evidencia de asistencia" },
  ],
  employeeStatuses: [
    { id: 1, code: "active", name: "Activo" },
    { id: 2, code: "inactive", name: "Inactivo" },
    { id: 3, code: "on_leave", name: "En licencia" },
    { id: 4, code: "retired", name: "Retirado" },
  ],
  candidateStatuses: [
    { id: 1, code: "draft", name: "Borrador" },
    { id: 2, code: "in_process", name: "En proceso" },
    { id: 3, code: "approved", name: "Aprobado" },
    { id: 4, code: "rejected", name: "Rechazado" },
    { id: 5, code: "hired", name: "Contratado" },
  ],
  contractStatuses: [
    { id: 1, code: "draft", name: "Borrador" },
    { id: 2, code: "active", name: "Activo" },
    { id: 3, code: "finished", name: "Finalizado" },
    { id: 4, code: "cancelled", name: "Cancelado" },
  ],
  contractTypes: [
    { id: 1, code: "fixed_term", name: "Termino fijo" },
    { id: 2, code: "indefinite", name: "Indefinido" },
    { id: 3, code: "temporary_agency", name: "Temporal" },
  ],
  affiliationTypes: [
    { id: 1, code: "eps", name: "EPS" },
    { id: 2, code: "arl", name: "ARL" },
    { id: 3, code: "pension", name: "Pension" },
    { id: 4, code: "compensation_fund", name: "Caja de compensacion" },
  ],
  affiliationStatuses: [
    { id: 1, code: "pending", name: "Pendiente" },
    { id: 2, code: "in_progress", name: "En tramite" },
    { id: 3, code: "completed", name: "Completada" },
    { id: 4, code: "rejected", name: "Rechazada" },
  ],
  payrollPeriodStatuses: [
    { id: 1, code: "draft", name: "Borrador" },
    { id: 2, code: "in_review", name: "En revision" },
    { id: 3, code: "approved", name: "Aprobada" },
    { id: 4, code: "closed", name: "Cerrada" },
  ],
  payrollSettlementStatuses: [
    { id: 1, code: "generated", name: "Generada" },
    { id: 2, code: "reviewed", name: "Revisada" },
    { id: 3, code: "approved", name: "Aprobada" },
  ],
  payrollNoveltyTypes: [
    { id: 1, code: "commission", name: "Comision" },
    { id: 2, code: "bonus", name: "Bono" },
    { id: 3, code: "mobility_allowance", name: "Auxilio de movilidad" },
    { id: 4, code: "overtime", name: "Horas extra" },
    { id: 5, code: "night_surcharge", name: "Recargo nocturno" },
    { id: 6, code: "incapacity", name: "Incapacidad" },
    { id: 7, code: "employee_fund_deduction", name: "Deduccion fondo empleados" },
    { id: 8, code: "authorized_deduction", name: "Deduccion autorizada" },
  ],
  offboardingStatuses: [
    { id: 1, code: "draft", name: "Borrador" },
    { id: 2, code: "in_process", name: "En proceso" },
    { id: 3, code: "completed", name: "Completado" },
  ],
  withdrawalReasons: [
    { id: 1, code: "resignation", name: "Renuncia" },
    { id: 2, code: "termination", name: "Terminacion" },
    { id: 3, code: "fixed_term_non_renewal", name: "No renovacion termino fijo" },
  ],
  settlementStatuses: [
    { id: 1, code: "generated", name: "Generada" },
    { id: 2, code: "reviewed", name: "Revisada" },
    { id: 3, code: "approved", name: "Aprobada" },
    { id: 4, code: "paid", name: "Pagada" },
  ],
  trainingTypes: [
    { id: 1, code: "induction", name: "Induccion" },
    { id: 2, code: "training", name: "Capacitacion" },
    { id: 3, code: "reinduction", name: "Reinduccion" },
  ],
  trainingStatuses: [
    { id: 1, code: "scheduled", name: "Programada" },
    { id: 2, code: "completed", name: "Completada" },
    { id: 3, code: "cancelled", name: "Cancelada" },
  ],
  evaluationStatuses: [
    { id: 1, code: "scheduled", name: "Programada" },
    { id: 2, code: "completed", name: "Completada" },
    { id: 3, code: "closed", name: "Cerrada" },
  ],
  improvementPlanStatuses: [
    { id: 1, code: "open", name: "Abierto" },
    { id: 2, code: "in_progress", name: "En progreso" },
    { id: 3, code: "closed", name: "Cerrado" },
  ],
  interviewStatuses: [
    { id: 1, code: "scheduled", name: "Programada" },
    { id: 2, code: "completed", name: "Completada" },
    { id: 3, code: "cancelled", name: "Cancelada" },
  ],
  certificateTypes: [
    { id: 1, code: "employment", name: "Certificado laboral" },
    { id: 2, code: "salary", name: "Certificado salarial" },
  ],
  certificateStatuses: [
    { id: 1, code: "requested", name: "Solicitado" },
    { id: 2, code: "generated", name: "Generado" },
    { id: 3, code: "delivered", name: "Entregado" },
  ],
  roles: [
    { id: 1, code: "ADMIN", name: "Administrador" },
    { id: 2, code: "RRHH", name: "Recursos humanos" },
    { id: 3, code: "CONTABILIDAD", name: "Contabilidad" },
    { id: 4, code: "GERENCIA", name: "Gerencia" },
  ],
} satisfies Record<string, CatalogItem[]>;

export function catalogName(items: CatalogItem[], id?: number | null) {
  if (id == null) return "Sin definir";
  return items.find((item) => item.id === id)?.name ?? `ID ${id}`;
}

export function catalogCode(items: CatalogItem[], id?: number | null) {
  if (id == null) return "unknown";
  return items.find((item) => item.id === id)?.code ?? "unknown";
}

export function defaultId(items: CatalogItem[], code: string) {
  return items.find((item) => item.code === code)?.id ?? items[0]?.id ?? 1;
}
