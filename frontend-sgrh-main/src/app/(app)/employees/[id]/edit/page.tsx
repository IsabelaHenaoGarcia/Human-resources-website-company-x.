import { EmployeeFormPage } from "@/features/employees";

export default async function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <EmployeeFormPage employeeId={id} />;
}
