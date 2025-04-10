<script setup lang="ts">
import type { Component } from '../types';

const props = defineProps<{
    component: Component | null;
}>();

</script>

<template>
    <div class="p-2 rounded text-lg flex justify-between" v-if="component">
        <span>{{ component.name }}</span>
        <span>{{ component.price }} </span>
    </div>
</template>
