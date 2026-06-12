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
        permission: "atrasados:ver",
        children: [
          {
            id: "comisiones",
            label: "Comisiones",
            icon: "groups",
            path: "/academico",
            permission: "atrasados:ver",
          },
        ],
      },
    ],
  },
  {
    id: "coordinacion",
    label: "Coordinación",
    items: [
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
        id: "avisos",
        label: "Avisos",
        icon: "campaign",
        path: "/avisos",
        permission: "avisos:publicar",
      },
      {
        id: "tareas",
        label: "Tareas Internas",
        icon: "checklist",
        path: "/tareas",
        permission: "tareas:gestionar",
      },
      {
        id: "coloquios",
        label: "Coloquios",
        icon: "quiz",
        path: "/coloquios",
        permission: "coloquios:gestionar",
      },
    ],
  },
  {
    id: "admin",
    label: "Administración",
    items: [
      {
        id: "estructura",
        label: "Estructura Académica",
        icon: "account_tree",
        path: "/estructura",
        permission: "estructura:gestionar",
      },
      {
        id: "usuarios",
        label: "Usuarios",
        icon: "people",
        path: "/usuarios",
        permission: "usuarios:gestionar",
      },
      {
        id: "auditoria",
        label: "Auditoría",
        icon: "receipt_long",
        path: "/auditoria",
        permission: "auditoria:ver",
      },
    ],
  },
  {
    id: "finanzas",
    label: "Finanzas",
    items: [
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
