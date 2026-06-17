import api from "@/api/client";
import type {
  SalarioBase,
  SalarioBaseCreateDTO,
  CategoriaPlus,
  CategoriaPlusCreateDTO,
  CategoriaPlusUpdateDTO,
} from "../types/grilla";

export function getBases() {
  return api.get<SalarioBase[]>("/grilla-salarial/bases");
}

export function createBase(data: SalarioBaseCreateDTO) {
  return api.post<SalarioBase>("/grilla-salarial/bases", data);
}

export function getCategoriasPlus() {
  return api.get<{ items: CategoriaPlus[]; total: number }>("/admin/categorias-plus");
}

export function createCategoriaPlus(data: CategoriaPlusCreateDTO) {
  return api.post<CategoriaPlus>("/admin/categorias-plus", data);
}

export function updateCategoriaPlus(id: string, data: CategoriaPlusUpdateDTO) {
  return api.put<CategoriaPlus>(`/admin/categorias-plus/${id}`, data);
}

export function deleteCategoriaPlus(id: string) {
  return api.delete<void>(`/admin/categorias-plus/${id}`);
}

export function toggleCategoriaPlus(id: string) {
  return api.patch<CategoriaPlus>(`/admin/categorias-plus/${id}/toggle`);
}
