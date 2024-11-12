import { MainNav } from "@/components/main-nav";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-background">
      <MainNav />
      <main className="container mx-auto p-4 md:p-8">{children}</main>
    </div>
  );
}