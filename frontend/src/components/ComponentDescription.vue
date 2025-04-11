<script setup lang="ts">
import { computed } from 'vue';
import type { Component } from '../types';

const props = defineProps<{
	componentType: string;
	component: Component;
}>();

const excludedKeys = ['id', 'name', 'price'];

const filteredEntries = computed(() => {
	return Object.entries(props.component).filter(([key]) => !excludedKeys.includes(key));
});
</script>

<template>
	<div class="flex flex-wrap items-start text-sm space-x-1">
		<div v-for="[key, value] in filteredEntries" :key="key" class="flex gap-2">
			<span class="font-extrabold capitalize">{{ key }}:</span>
			<span>{{ value }}</span>
		</div>
	</div>
</template>
