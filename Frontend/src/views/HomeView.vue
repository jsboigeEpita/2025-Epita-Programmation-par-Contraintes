<template>
    <div class="min-h-screen flex flex-col items-center relative">
        <span class="text-2xl font-bold mt-10">Bienvenue sur le Configurateur</span>

        <div class="flex-1 flex items-center justify-center">
            <router-link to="/config">
                <v-btn>Configurateur</v-btn>
            </router-link>
        </div>
    </div>
</template>

<script setup lang="ts"></script>
