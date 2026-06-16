import { useState } from "react";
import ProgramasListPage from "./ProgramasListPage";
import FechasAcademicasPage from "./FechasAcademicasPage";

type Tab = "programas" | "fechas";

export default function SetupCuatrimestrePage() {
  const [tab, setTab] = useState<Tab>("programas");

  return (
    <div className="space-y-lg p-lg">
      <h1 className="font-headline-md text-headline-md text-on-surface">
        Setup de Cuatrimestre
      </h1>

      <div className="flex items-center gap-2 border-b border-border">
        <button
          type="button"
          onClick={() => setTab("programas")}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            tab === "programas"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-on-surface"
          }`}
        >
          Programas de Materia
        </button>
        <button
          type="button"
          onClick={() => setTab("fechas")}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            tab === "fechas"
              ? "border-primary text-primary"
              : "border-transparent text-muted-foreground hover:text-on-surface"
          }`}
        >
          Fechas Académicas
        </button>
      </div>

      {tab === "programas" ? <ProgramasListPage /> : <FechasAcademicasPage />}
    </div>
  );
}
