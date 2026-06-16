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
        children: [
          {
            id: "mis-equipos",
            label: "Mis Equipos",
            icon: "badge",
            path: "/equipos",
            permission: "atrasados:ver",
          },
          {
            id: "gestion-asignaciones",
            label: "Gestión de Asignaciones",
            icon: "manage_accounts",
            path: "/equipos/asignaciones",
            permission: "equipos:asignar",
          },
          {
            id: "asignacion-masiva",
            label: "Asignación Masiva",
            icon: "group_add",
            path: "/equipos/asignacion-masiva",
            permission: "equipos:asignar",
          },
          {
            id: "clonar-equipo",
            label: "Clonar Equipo",
            icon: "content_copy",
            path: "/equipos/clonar",
            permission: "equipos:asignar",
          },
          {
            id: "vigencia",
            label: "Vigencia",
            icon: "schedule",
            path: "/equipos/vigencia",
            permission: "equipos:asignar",
          },
        ],
      },
      {
        id: "encuentros",
        label: "Encuentros",
        icon: "calendar_month",
        path: "/encuentros",
        permission: "encuentros:gestionar",
        children: [
          {
            id: "slots",
            label: "Slots",
            icon: "calendar_month",
            path: "/encuentros",
            permission: "encuentros:gestionar",
          },
          {
            id: "guardias",
            label: "Guardias",
            icon: "security",
            path: "/encuentros/guardias",
            permission: "encuentros:gestionar",
          },
        ],
      },
      {
        id: "avisos",
        label: "Avisos",
        icon: "campaign",
        path: "/avisos",
        permission: "avisos:publicar",
        children: [
          {
            id: "gestion-avisos",
            label: "Gestión de Avisos",
            icon: "campaign",
            path: "/avisos",
            permission: "avisos:publicar",
          },
          {
            id: "avisos-activos",
            label: "Avisos Activos",
            icon: "notifications",
            path: "/avisos/activos",
          },
        ],
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
        permission: "coloquios:reservar",
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
        id: "setup-cuatrimestre",
        label: "Setup Cuatrimestre",
        icon: "calendar_month",
        path: "/setup-cuatrimestre",
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

function filterMenuItem(item: MenuItem, permissions: string[]): MenuItem | null {
  // Si tiene hijos, filtrar hijos recursivamente
  if (item.children && item.children.length > 0) {
    const filteredChildren = item.children
      .map((child) => filterMenuItem(child, permissions))
      .filter((c): c is MenuItem => c !== null);
    if (filteredChildren.length === 0) return null;
    return { ...item, children: filteredChildren };
  }
  // Si no tiene hijos, verificar permiso directo
  if (!item.permission) return item;
  if (permissions.includes(item.permission)) return item;
  return null;
}

export function getMenuItems(permissions: string[]): NavSection[] {
  return ALL_MENU_ITEMS
    .map((section) => ({
      ...section,
      items: section.items
        .map((item) => filterMenuItem(item, permissions))
        .filter((item): item is MenuItem => item !== null),
    }))
    .filter((section) => section.items.length > 0);
}

export function hasMenuItemPermission(
  permissions: string[],
  itemPermission?: string,
): boolean {
  if (!itemPermission) return true;
  return permissions.includes(itemPermission);
}
