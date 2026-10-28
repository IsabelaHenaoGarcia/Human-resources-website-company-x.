import { OffboardingDetailPage } from "@/features/operations";

export default async function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <OffboardingDetailPage offboardingId={id} />;
}
