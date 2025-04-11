import { defineStore } from 'pinia';

export const useSchedulingStore = defineStore('scheduling', {
  state: () => ({
    summary: null,
    lastSchedulingTime: null
  }),
  actions: {
    setSummary(summary) {
      this.summary = summary;
      this.lastSchedulingTime = new Date().toISOString();
    },
    clearSummary() {
      this.summary = null;
    }
  }
});