import { Outlet } from "react-router-dom";
import { Sidebar } from "@/features/shell/components/Sidebar";
import { Topbar } from "@/features/shell/components/Topbar";
import { ImpersonationBanner } from "@/features/shell/components/ImpersonationBanner";

export function AppLayout() {
  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Topbar />
        <ImpersonationBanner impersonatedName={undefined} />
        <main className="flex-1 overflow-y-auto bg-background">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
