export interface MenuItem {
  id: string;
  label: string;
  icon: string;
  path: string;
  permission?: string;
  children?: MenuItem[];
}

export interface NavSection {
  id: string;
  label?: string;
  items: MenuItem[];
}
