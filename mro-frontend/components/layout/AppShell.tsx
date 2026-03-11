import { Header } from "@/components/layout/Header";
import { Sidebar } from "@/components/layout/Sidebar";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-dvh bg-background">
      <Header />
      <Sidebar />
      <main className="ml-64 pt-14 h-dvh flex flex-col">
        {children}
      </main>
    </div>
  );
}
