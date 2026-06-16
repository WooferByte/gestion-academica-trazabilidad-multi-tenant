import { useMemo, useState } from "react";
import { FechaCard } from "./FechaCard";
import type { FechaAcademicaResponse } from "@/api/types";

interface FechasCalendarProps {
  items: FechaAcademicaResponse[];
  onEdit?: (item: FechaAcademicaResponse) => void;
}

export function FechasCalendar({ items, onEdit }: FechasCalendarProps) {
  const hoy = new Date();
  const [currentMonth, setCurrentMonth] = useState(hoy.getMonth());
  const [currentYear, setCurrentYear] = useState(hoy.getFullYear());

  const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
  const firstDayOfWeek = new Date(currentYear, currentMonth, 1).getDay();

  const fechasPorDia = useMemo(() => {
    const map = new Map<number, FechaAcademicaResponse[]>();
    items.forEach((f) => {
      const d = new Date(f.fecha);
      if (d.getMonth() === currentMonth && d.getFullYear() === currentYear) {
        const day = d.getDate();
        if (!map.has(day)) map.set(day, []);
        map.get(day)!.push(f);
      }
    });
    return map;
  }, [items, currentMonth, currentYear]);

  const weeks: number[][] = [];
  let week: number[] = [];
  for (let i = 0; i < firstDayOfWeek; i++) week.push(0);
  for (let day = 1; day <= daysInMonth; day++) {
    week.push(day);
    if (week.length === 7) {
      weeks.push(week);
      week = [];
    }
  }
  if (week.length > 0) weeks.push(week);

  const monthNames = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
  ];

  const prevMonth = () => {
    if (currentMonth === 0) { setCurrentMonth(11); setCurrentYear((y) => y - 1); }
    else setCurrentMonth((m) => m - 1);
  };
  const nextMonth = () => {
    if (currentMonth === 11) { setCurrentMonth(0); setCurrentYear((y) => y + 1); }
    else setCurrentMonth((m) => m + 1);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <button
          type="button"
          onClick={prevMonth}
          className="px-3 py-1 text-sm rounded-md border border-border hover:bg-accent"
        >
          &larr;
        </button>
        <h3 className="font-medium">
          {monthNames[currentMonth]} {currentYear}
        </h3>
        <button
          type="button"
          onClick={nextMonth}
          className="px-3 py-1 text-sm rounded-md border border-border hover:bg-accent"
        >
          &rarr;
        </button>
      </div>

      <div className="grid grid-cols-7 gap-1">
        {["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"].map((d) => (
          <div key={d} className="text-center text-xs font-medium text-muted-foreground py-2">
            {d}
          </div>
        ))}
        {weeks.flat().map((day, i) => (
          <div
            key={i}
            className={`min-h-[80px] p-1 rounded-md border border-border ${
              day === 0 ? "bg-muted/30" : ""
            }`}
          >
            {day > 0 && (
              <>
                <span className="text-xs text-muted-foreground block mb-1">{day}</span>
                <div className="space-y-1">
                  {fechasPorDia.get(day)?.map((f) => (
                    <FechaCard
                      key={f.id}
                      fecha={f}
                      onClick={() => onEdit?.(f)}
                    />
                  ))}
                </div>
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
