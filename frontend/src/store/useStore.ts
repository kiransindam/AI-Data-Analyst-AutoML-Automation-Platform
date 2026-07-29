// frontend/src/store/useStore.ts
import { create } from 'zustand';

interface User {
  id: string;
  email: string;
  username: string;
  role: string;
}

interface Dataset {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  row_count: number;
  col_count: number;
  status: string;
  created_at: string;
}

interface Project {
  id: string;
  name: string;
  status: string;
  results?: any;
}

interface AppState {
  // Auth
  user: User | null;
  isAuthenticated: boolean;
  setUser: (user: User | null) => void;
  logout: () => void;

  // Data
  datasets: Dataset[];
  currentDataset: Dataset | null;
  projects: Project[];
  currentProject: Project | null;

  // Actions
  setDatasets: (datasets: Dataset[]) => void;
  setCurrentDataset: (dataset: Dataset | null) => void;
  setProjects: (projects: Project[]) => void;
  setCurrentProject: (project: Project | null) => void;

  // UI
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
  sidebarOpen: boolean;
  toggleSidebar: () => void;
}

export const useStore = create<AppState>((set) => ({
  user: null,
  isAuthenticated: false,
  setUser: (user) => set({ user, isAuthenticated: !!user }),
  logout: () => {
    localStorage.clear();
    set({ user: null, isAuthenticated: false });
  },

  datasets: [],
  currentDataset: null,
  projects: [],
  currentProject: null,

  setDatasets: (datasets) => set({ datasets }),
  setCurrentDataset: (dataset) => set({ currentDataset: dataset }),
  setProjects: (projects) => set({ projects }),
  setCurrentProject: (project) => set({ currentProject: project }),

  isLoading: false,
  setIsLoading: (loading) => set({ isLoading: loading }),
  sidebarOpen: true,
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
}));
