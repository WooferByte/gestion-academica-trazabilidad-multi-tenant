import { useState } from "react";
import { PageHeader } from "@/features/admin-estructura/shared/PageHeader";
import { BasesSalarialesTab } from "../components/BasesSalarialesTab";
import { CategoriasPlusTab } from "../components/CategoriasPlusTab";

const TABS = [
  { id: "bases", label: "Bases Salariales" },
  { id: "categorias", label: "Categorías Plus" },
];

export default function FinanzasGrillaPage() {
  const [activeTab, setActiveTab] = useState("bases");

  return (
    <div className="space-y-lg p-lg">
      <PageHeader title="Grilla Salarial" />

      <div className="border-b border-gray-200">
        <nav className="flex gap-4">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.id
                  ? "border-blue-600 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      <div className="mt-lg">
        {activeTab === "bases" && <BasesSalarialesTab />}
        {activeTab === "categorias" && <CategoriasPlusTab />}
      </div>
    </div>
  );
}
