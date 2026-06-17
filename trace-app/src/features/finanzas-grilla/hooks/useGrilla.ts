import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { showToast } from "@/components/ui/Toast";
import {
  getBases,
  createBase,
  getCategoriasPlus,
  createCategoriaPlus,
  updateCategoriaPlus,
  deleteCategoriaPlus,
  toggleCategoriaPlus,
} from "../services/grilla.service";
import type { SalarioBaseCreateDTO, CategoriaPlusCreateDTO, CategoriaPlusUpdateDTO } from "../types/grilla";

export function useBases() {
  return useQuery({
    queryKey: ["grilla", "bases"],
    queryFn: () => getBases().then((r) => r.data),
    staleTime: 60 * 1000,
  });
}

export function useCrearBase() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: SalarioBaseCreateDTO) => createBase(data).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["grilla", "bases"] });
      showToast("Base salarial creada correctamente", "success");
    },
    onError: () => {
      showToast("Error al crear la base salarial", "error");
    },
  });
}

export function useCategoriasPlus() {
  return useQuery({
    queryKey: ["grilla", "categorias-plus"],
    queryFn: () => getCategoriasPlus().then((r) => r.data.items),
    staleTime: 60 * 1000,
  });
}

export function useCrearCategoriaPlus() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: CategoriaPlusCreateDTO) => createCategoriaPlus(data).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["grilla", "categorias-plus"] });
      showToast("Categoría Plus creada correctamente", "success");
    },
    onError: () => {
      showToast("Error al crear la categoría Plus", "error");
    },
  });
}

export function useActualizarCategoriaPlus() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: CategoriaPlusUpdateDTO }) =>
      updateCategoriaPlus(id, data).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["grilla", "categorias-plus"] });
      showToast("Categoría Plus actualizada correctamente", "success");
    },
    onError: () => {
      showToast("Error al actualizar la categoría Plus", "error");
    },
  });
}

export function useEliminarCategoriaPlus() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteCategoriaPlus(id).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["grilla", "categorias-plus"] });
      showToast("Categoría Plus eliminada correctamente", "success");
    },
    onError: () => {
      showToast("Error al eliminar la categoría Plus", "error");
    },
  });
}

export function useToggleCategoriaPlus() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => toggleCategoriaPlus(id).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["grilla", "categorias-plus"] });
      showToast("Estado actualizado correctamente", "success");
    },
    onError: () => {
      showToast("Error al cambiar el estado", "error");
    },
  });
}
