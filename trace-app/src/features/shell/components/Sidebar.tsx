import { useState, useEffect, useRef } from "react";
import { NavLink, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";
import { useAuth } from "@/features/auth/hooks/useAuth";
import { getMenuItems } from "@/features/shell/services/menu.service";
import { Dialog } from "@/components/ui/Dialog";
import { Button } from "@/components/ui/Button";
import type { MenuItem } from "@/features/shell/types/shell.types";

const SIDEBAR_STATE_KEY = "trace_sidebar_collapsed";

export function Sidebar() {
  const { permissions, logout } = useAuth();
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(() => {
    return localStorage.getItem(SIDEBAR_STATE_KEY) === "true";
  });
  const [showLogoutDialog, setShowLogoutDialog] = useState(false);
  const [expandedMenus, setExpandedMenus] = useState<Record<string, boolean>>({});

  const isFirstRender = useRef(true);

  const menuSections = getMenuItems(permissions);

  useEffect(() => {
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }
    localStorage.setItem(SIDEBAR_STATE_KEY, String(collapsed));
  }, [collapsed]);

  useEffect(() => {
    const next: Record<string, boolean> = {};
    for (const section of menuSections) {
      for (const item of section.items) {
        if (item.children && location.pathname.startsWith(item.path)) {
          next[item.id] = true;
        }
      }
    }
    setExpandedMenus((prev) => ({ ...prev, ...next }));
  }, []);

  const toggleCollapse = () => setCollapsed((prev) => !prev);

  const toggleMenu = (id: string) => {
    setExpandedMenus((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const handleLogout = async () => {
    setShowLogoutDialog(false);
    await logout();
  };

  const isActive = (path: string) => {
    if (path === "/dashboard") {
      return location.pathname === "/dashboard";
    }
    return location.pathname.startsWith(path);
  };

  return (
    <>
      <aside
        className={cn(
          "flex flex-col border-r border-outline-variant bg-white transition-all duration-200",
          collapsed ? "w-sidebar-collapsed" : "w-sidebar-width",
        )}
      >
        {/* Logo */}
        <div
          className={cn(
            "flex items-center border-b border-outline-variant px-md",
            collapsed ? "h-16 justify-center" : "h-16 gap-sm px-lg",
          )}
        >
          <div className="flex h-8 w-8 items-center justify-center rounded bg-primary text-on-primary font-headline-sm text-headline-sm">
            T
          </div>
          {!collapsed && (
            <div className="flex flex-col">
              <span className="font-body-md text-body-md font-semibold text-on-surface">
                Activia Trace
              </span>
              <span className="font-label-sm text-label-sm text-secondary">
                Academic Orchestrator
              </span>
            </div>
          )}
        </div>

        {/* Nav items */}
        <nav className="flex-1 overflow-y-auto custom-scrollbar px-sm py-md">
          {menuSections.map((section) => (
            <div key={section.id} className="flex flex-col gap-xs">
              {!collapsed && section.label && (
                <span className="px-sm py-xs font-label-sm text-label-sm text-secondary uppercase tracking-wider">
                  {section.label}
                </span>
              )}
              {section.items.map((item) => (
                <div key={item.id}>
                  {item.children && item.children.length > 0 ? (
                    <>
                      <button
                        onClick={() => toggleMenu(item.id)}
                        className={cn(
                          "flex w-full items-center gap-sm rounded transition-colors",
                          collapsed ? "justify-center px-sm py-sm" : "px-sm py-sm",
                          isActive(item.path)
                            ? "bg-secondary-container text-on-secondary-container"
                            : "text-secondary hover:bg-surface-container hover:text-on-surface",
                        )}
                        title={collapsed ? item.label : undefined}
                      >
                        <span className="material-symbols-outlined text-[20px]">
                          {item.icon}
                        </span>
                        {!collapsed && (
                          <>
                            <span className="flex-1 text-left font-body-md text-body-md">
                              {item.label}
                            </span>
                            <span className="material-symbols-outlined text-[16px] transition-transform duration-200">
                              {expandedMenus[item.id] ? "expand_less" : "expand_more"}
                            </span>
                          </>
                        )}
                      </button>
                      {!collapsed && expandedMenus[item.id] && (
                        <div className="ml-md flex flex-col border-l border-outline-variant pl-sm">
                          {item.children.map((child) => (
                            <NavItem
                              key={child.id}
                              item={child}
                              collapsed={false}
                              isActive={location.pathname === child.path}
                              nested
                            />
                          ))}
                        </div>
                      )}
                    </>
                  ) : (
                    <NavItem
                      item={item}
                      collapsed={collapsed}
                      isActive={isActive(item.path)}
                    />
                  )}
                </div>
              ))}
            </div>
          ))}
        </nav>

        {/* Bottom section */}
        <div className="border-t border-outline-variant px-sm py-md">
          <button
            onClick={toggleCollapse}
            className={cn(
              "flex w-full items-center gap-sm rounded px-sm py-sm font-body-md text-body-md text-secondary hover:bg-surface-container hover:text-on-surface transition-colors",
              collapsed && "justify-center",
            )}
            title={collapsed ? "Expandir menú" : "Colapsar menú"}
          >
            <span className="material-symbols-outlined text-[20px]">
              {collapsed ? "menu_open" : "menu"}
            </span>
            {!collapsed && <span>Menú</span>}
          </button>

          <button
            onClick={() => setShowLogoutDialog(true)}
            className={cn(
              "flex w-full items-center gap-sm rounded px-sm py-sm font-body-md text-body-md text-error hover:bg-error-container transition-colors",
              collapsed && "justify-center",
            )}
            title="Cerrar Sesión"
          >
            <span className="material-symbols-outlined text-[20px]">
              logout
            </span>
            {!collapsed && <span>Cerrar Sesión</span>}
          </button>
        </div>
      </aside>

      <Dialog
        open={showLogoutDialog}
        onClose={() => setShowLogoutDialog(false)}
        title="Cerrar Sesión"
        footer={
          <>
            <Button variant="ghost" onClick={() => setShowLogoutDialog(false)}>
              Cancelar
            </Button>
            <Button variant="danger" onClick={handleLogout}>
              Cerrar Sesión
            </Button>
          </>
        }
      >
        <p className="font-body-md text-body-md text-on-surface">
          ¿Estás seguro de que deseas cerrar sesión?
        </p>
      </Dialog>
    </>
  );
}

type NavItemProps = {
  item: MenuItem;
  collapsed: boolean;
  isActive: boolean;
  nested?: boolean;
};

function NavItem({ item, collapsed, isActive, nested }: NavItemProps) {
  return (
    <NavLink
      to={item.path}
      className={cn(
        "flex items-center gap-sm rounded transition-colors",
        collapsed ? "justify-center px-sm py-sm" : "px-sm py-sm",
        nested ? "ml-xs" : "",
        isActive
          ? "bg-secondary-container text-on-secondary-container"
          : "text-secondary hover:bg-surface-container hover:text-on-surface",
      )}
      title={collapsed ? item.label : undefined}
    >
      <span className="material-symbols-outlined text-[20px]">
        {item.icon}
      </span>
      {!collapsed && (
        <span className="font-body-md text-body-md">{item.label}</span>
      )}
    </NavLink>
  );
}
