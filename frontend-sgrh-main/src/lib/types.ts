export type PaginatedResponse<T> = {
  items: T[];
  page: number;
  page_size: number;
  total: number;
};

export type User = {
  id: number;
  username: string;
  full_name?: string | null;
  roles: string[];
  permissions: string[];
};

export type LoginResponse = {
  user: User;
  token: string;
  token_type: "bearer";
};

export type CatalogItem = {
  id: number;
  code: string;
  name: string;
  active?: boolean;
};

export type Employee = {
  id: number;
  document_type_id: number;
  employee_status_id: number;
  full_name: string;
  document_number: string;
  birth_date?: string | null;
  email?: string | null;
  phone?: string | null;
  address?: string | null;
  position: string;
  hire_date: string;
  base_salary: string;
  eps_entity?: string | null;
  pension_entity?: string | null;
  has_beneficiaries: boolean;
  beneficiary_notes?: string | null;
  induction_completed: boolean;
  latest_evaluation_status?: string | null;
  latest_evaluation_date?: string | null;
  user_id?: number | null;
  created_at: string;
  updated_at: string;
};

export type Candidate = {
  id: number;
  document_type_id: number;
  candidate_status_id: number;
  full_name: string;
  document_number: string;
  email?: string | null;
  phone?: string | null;
  position_applied?: string | null;
  interview_result_summary?: string | null;
  references_verified: boolean;
  background_verified: boolean;
  occupational_exam_date?: string | null;
  occupational_exam_result?: string | null;
  occupational_exam_observations?: string | null;
  created_at: string;
  updated_at: string;
};

export type Contract = {
  id: number;
  employee_id: number;
  contract_type_id: number;
  contract_status_id: number;
  position: string;
  base_salary: string;
  start_date: string;
  end_date?: string | null;
  created_at: string;
};

export type Affiliation = {
  id: number;
  employee_id: number;
  affiliation_type_id: number;
  affiliation_status_id: number;
  entity: string;
  registration_date: string;
  observations?: string | null;
  created_at: string;
};

export type PayrollPeriod = {
  id: number;
  name: string;
  start_date: string;
  end_date: string;
  status_id: number;
  approved_by_id?: number | null;
  approved_at?: string | null;
  approval_comment?: string | null;
  created_at: string;
};

export type PayrollSettlement = {
  id: number;
  employee_id: number;
  payroll_period_id: number;
  status_id: number;
  base_salary: string;
  earnings_total: string;
  deductions_total: string;
  net_pay: string;
  approved_by_id?: number | null;
  approved_at?: string | null;
  approval_comment?: string | null;
  created_at: string;
};

export type Offboarding = {
  id: number;
  employee_id: number;
  contract_id: number;
  reason_id: number;
  status_id: number;
  withdrawal_date: string;
  observations?: string | null;
  exit_exam_completed: boolean;
  equipment_returned: boolean;
  uniforms_returned: boolean;
  checklist_observations?: string | null;
};

export type ContractSettlement = {
  id: number;
  offboarding_id: number;
  status_id: number;
  vacation: string;
  bonus: string;
  severance: string;
  severance_interest: string;
  deductions: string;
  total: string;
  observations?: string | null;
  approved_by_id?: number | null;
  approved_at?: string | null;
  approval_comment?: string | null;
};

export type TrainingActivity = {
  id: number;
  type_id: number;
  status_id: number;
  name: string;
  scheduled_date: string;
  description?: string | null;
};

export type Evaluation = {
  id: number;
  employee_id: number;
  status_id: number;
  evaluation_type: string;
  evaluation_date: string;
  score?: string | null;
  observations?: string | null;
};

export type Certificate = {
  id: number;
  employee_id: number;
  certificate_type_id: number;
  status_id: number;
  document_id?: number | null;
  observation?: string | null;
};

export type DocumentRecord = {
  id: number;
  original_filename: string;
  stored_filename: string;
  storage_path: string;
  mime_type?: string | null;
  file_size: number;
  generated: boolean;
  file_type_id: number;
  created_at: string;
};

export type AuditRecord = {
  id: number;
  user_id?: number | null;
  entity: string;
  record_id?: number | null;
  action: string;
  event_date: string;
  detail?: string | null;
};

export type AdminUser = User;
