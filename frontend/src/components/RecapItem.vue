<script setup lang="ts">
import type { Component } from '../types';

defineProps<{
    component: Component | null;
}>();

</script>

<template>
    <div class="p-2 rounded text-lg flex justify-between" v-if="props.component">
        <span>{{ props.component.name }}</span>
        <span>{{ props.component.price }} </span>
    </div>
</template>
