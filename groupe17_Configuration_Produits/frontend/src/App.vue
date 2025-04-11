<script setup lang="ts">
import { onMounted } from 'vue';
import { useSessionStore } from './stores/sessionStore';
import { ensureSessionId } from './plugins/cookie';

onMounted(() => {
    const sessionStore = useSessionStore();
    sessionStore.setSessionId(ensureSessionId());
});
</script>

<template>
    <v-app class="ms-app">
        <v-main class="ms-app-main">
            <router-view />
        </v-main>
    </v-app>
    <!-- <nav>
        <router-link to="/">Accueil</router-link>
        <router-link to="/config">Configurateur</router-link>
    </nav> -->
</template>

<style lang="scss" scoped>
.ms-app {
    background-color: var(--color-background-dark);
    overflow-x: hidden;

    &-main {
        position: relative;
        display: flex;
        flex-direction: column;
    }
}
</style>
