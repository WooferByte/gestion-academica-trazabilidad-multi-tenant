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
            id: "comisiones",
            label: "Comisiones",
            icon: "groups",
            path: "/academico",
            permission: "estructura:gestionar",
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
