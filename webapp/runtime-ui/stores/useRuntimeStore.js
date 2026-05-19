import { create } from 'zustand';

export const useRuntimeStore = create((set) => ({
  agents: [],
  activeGraphs: [],
  logs: [],
  systemMetrics: { cpu: 0, memory: 0 },
  
  setAgents: (agents) => set({ agents }),
  addLog: (log) => set((state) => ({ logs: [...state.logs.slice(-99), log] })),
  updateMetrics: (metrics) => set({ systemMetrics: metrics })
}));
