import { defineStore } from 'pinia';

export const useSessionStore = defineStore('sessionStore', {
    state: () => ({
        sessionId: '' as string,
    }),
    actions: {
        setSessionId(id: string) {
            this.sessionId = id;
        },
        getSessionId() {
            return this.sessionId;
        },
    },
});
