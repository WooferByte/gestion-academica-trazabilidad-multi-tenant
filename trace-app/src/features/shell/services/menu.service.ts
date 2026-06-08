import type { MenuItem, NavSection } from "@/features/shell/types/shell.types";

const ALL_MENU_ITEMS: NavSection[] = [
  {
    id: "main",
    items: [
      {
        id: "dashboard",
        label: "Panel General",
        icon: "dashboard",
        path: "/dashboard",
      },
      {
        id: "academico",
        label: "Académico",
        icon: "school",
        path: "/academico",
        permission: "estructura:gestionar",
        children: [
          {
            id: "materias",
            label: "Materias",
            icon: "menu_book",
            path: "/academico/materias",
            permission: "estructura:gestionar",
          },
          {
            id: "calificaciones",
            label: "Calificaciones",
            icon: "assignment",
            path: "/academico/calificaciones",
            permission: "calificaciones:importar",
          },
          {
            id: "coloquios",
            label: "Coloquios",
            icon: "quiz",
            path: "/academico/coloquios",
            permission: "coloquios:gestionar",
          },
        ],
      },
      {
        id: "analisis",
        label: "Análisis",
        icon: "monitoring",
        path: "/analisis",
        permission: "atrasados:ver",
        children: [
          {
            id: "atrasados",
            label: "Atrasados",
            icon: "warning",
            path: "/analisis/atrasados",
            permission: "atrasados:ver",
          },
          {
            id: "reportes",
            label: "Reportes",
            icon: "summarize",
            path: "/analisis/reportes",
            permission: "atrasados:ver",
          },
        ],
      },
      {
        id: "comunicacion",
        label: "Comunicación",
        icon: "mail",
        path: "/comunicacion",
        permission: "comunicacion:enviar",
        children: [
          {
            id: "enviar",
            label: "Enviar",
            icon: "send",
            path: "/comunicacion/enviar",
            permission: "comunicacion:enviar",
          },
          {
            id: "aprobacion",
            label: "Aprobaciones",
            icon: "fact_check",
            path: "/comunicacion/aprobacion",
            permission: "comunicacion:aprobar",
          },
        ],
      },
      {
        id: "equipos",
        label: "Equipos Docentes",
        icon: "badge",
        path: "/equipos",
        permission: "equipos:asignar",
      },
      {
        id: "encuentros",
        label: "Encuentros",
        icon: "calendar_month",
        path: "/encuentros",
        permission: "encuentros:gestionar",
      },
      {
        id: "liquidaciones",
        label: "Liquidaciones",
        icon: "payments",
        path: "/liquidaciones",
        permission: "liquidaciones:ver",
      },
    ],
  },
];

function hasAccess(item: MenuItem, permissions: string[]): boolean {
  // Si tiene hijos, mostrar si ALGUN hijo es accesible
  if (item.children && item.children.length > 0) {
    return item.children.some((child) => hasAccess(child, permissions));
  }
  // Si no requiere permiso, mostrar siempre
  if (!item.permission) return true;
  return permissions.includes(item.permission);
}

export function getMenuItems(permissions: string[]): NavSection[] {
  function filterItems(items: NavSection[]): NavSection[] {
    return items
      .map((section) => ({
        ...section,
        items: section.items.filter((item) => hasAccess(item, permissions)),
      }))
      .filter((section) => section.items.length > 0);
  }

  return filterItems(ALL_MENU_ITEMS);
}

export function hasMenuItemPermission(
  permissions: string[],
  itemPermission?: string,
): boolean {
  if (!itemPermission) return true;
  return permissions.includes(itemPermission);
}
