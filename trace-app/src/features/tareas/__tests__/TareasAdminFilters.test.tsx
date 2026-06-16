import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { TareasAdminFilters } from "@/features/tareas/components/TareasAdminFilters";

describe("TareasAdminFilters", () => {
  it("renders all filter inputs", () => {
    const filters = { asignado_a: "", asignado_por: "", materia_id: "", estado: "", search: "" };
    const onChange = vi.fn();

    render(<TareasAdminFilters filters={filters} onChange={onChange} />);

    expect(screen.getByPlaceholderText("ID de usuario")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Título o descripción...")).toBeInTheDocument();
  });

  it("calls onChange when search input changes", () => {
    const filters = { asignado_a: "", asignado_por: "", materia_id: "", estado: "", search: "" };
    const onChange = vi.fn();

    render(<TareasAdminFilters filters={filters} onChange={onChange} />);

    fireEvent.change(screen.getByPlaceholderText("Título o descripción..."), {
      target: { value: "álgebra" },
    });

    expect(onChange).toHaveBeenCalledWith(
      expect.objectContaining({ search: "álgebra" }),
    );
  });
});
