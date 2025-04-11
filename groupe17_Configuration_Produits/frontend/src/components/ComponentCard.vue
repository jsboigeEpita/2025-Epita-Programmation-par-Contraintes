<script setup lang="ts">
import { ref, watch } from 'vue';
import { images } from '../assets/index';
import Modal from '../views/modals/Modal.vue';
import type { Component, SelectedComponents, SelectedComponentsResponse } from '../types';
import { deleteComponent, getConfig } from '../api/api';
import ComponentDescription from './ComponentDescription.vue';

const props = defineProps<{
    componentType: string;
    component: Component | null;
    selectedComponents: SelectedComponents;
}>();

const isModalOpen = ref<boolean>(false);
const typeComponent = ref<string>('');
const confgPrice = ref<number>(0);
const selectedComponents = ref<SelectedComponents>(props.selectedComponents);

const emit = defineEmits(['selected-components']);

const deleteComponents = async (type: string) => {
    await deleteComponent(type);
    const config = <SelectedComponentsResponse>await getConfig();
    confgPrice.value = config.price;
    selectedComponents.value = {
        case: config.pcCase,
        powersupply: config.powerSupply,
        videocard: config.videoCard,
        cpuCooler: config.cpuCooler,
        storage: config.storageDevice,
        motherboard: config.motherboard,
        cpu: config.cpu,
        ram: config.memory,
    };
    emit('selected-components', selectedComponents.value);
};

const openModal = (type: string) => {
    isModalOpen.value = true;
    typeComponent.value = type;
};

watch(
    () => props.selectedComponents,
    (newVal) => {
        selectedComponents.value = newVal;
    },
    { immediate: true }
);
</script>

<template>
    <div class="flex flex-col w-full">
        <div
            class="flex items-center justify-between bg-[var(--color-background-secondary-dark)] text-white w-full px-2 pr-8 rounded-t-md rounded-bl-md border-2 border-[var(--color-background-secondary-dark)] hover:border-[green] hover:border-opacity-50"
            @click="openModal(props.componentType)"
        >
            <div class="flex items-center space-x-2">
                <img
                    v-if="props.componentType == 'case'"
                    :src="images.CaseGreen"
                    alt="Case"
                    class="w-20 opacity-50"
                />
                <img
                    v-else-if="props.componentType == 'powersupply'"
                    :src="images.AlimGreen"
                    alt="Powersupply"
                    class="w-20 opacity-50"
                />
                <img
                    v-else-if="props.componentType == 'videocard'"
                    :src="images.GraphicsGreen"
                    alt="VideoCard"
                    class="w-20 opacity-50"
                />
                <img
                    v-else-if="props.componentType == 'cpu-cooler'"
                    :src="images.VentiradGreen"
                    alt="CpuCooler"
                    class="w-20 opacity-50"
                />
                <img
                    v-else-if="props.componentType == 'storage'"
                    :src="images.DisqueGreen"
                    alt="Storage"
                    class="w-20 opacity-50"
                />
                <img
                    v-else-if="props.componentType == 'motherboard'"
                    :src="images.MotherboardGreen"
                    alt="Motherboard"
                    class="w-20 opacity-50"
                />
                <img
                    v-else-if="props.componentType == 'cpu'"
                    :src="images.ProcesseurGreen"
                    alt="Cpu"
                    class="w-20 opacity-50"
                />
                <img
                    v-else-if="props.componentType == 'ram'"
                    :src="images.RamGreen"
                    alt="Ram"
                    class="w-20 opacity-50"
                />

                <span v-if="props.componentType == 'case'" class="text-2xl font-bold text-white"
                    >BOITIER</span
                >
                <span
                    v-else-if="props.componentType == 'powersupply'"
                    class="text-2xl font-bold text-white"
                    >ALIMENTATION</span
                >
                <span
                    v-else-if="props.componentType == 'videocard'"
                    class="text-2xl font-bold text-white"
                    >CARTE GRAPHIQUE</span
                >
                <span
                    v-else-if="props.componentType == 'cpu-cooler'"
                    class="text-2xl font-bold text-white"
                    >VENTIRAD</span
                >
                <span
                    v-else-if="props.componentType == 'storage'"
                    class="text-2xl font-bold text-white"
                    >DISQUE DUR</span
                >
                <span
                    v-else-if="props.componentType == 'motherboard'"
                    class="text-2xl font-bold text-white"
                    >CARTE MERE</span
                >
                <span v-else-if="props.componentType == 'cpu'" class="text-2xl font-bold text-white"
                    >PROCESSEUR</span
                >
                <span v-else-if="props.componentType == 'ram'" class="text-2xl font-bold text-white"
                    >RAM</span
                >
            </div>
            <v-icon>mdi-plus</v-icon>
        </div>
        <div
            class="bg-[var(--color-primary)] h-auto p-2 px-4 ml-12 flex flex-col rounded-b-md"
            v-if="component"
        >
            <div class="flex items-center justify-between w-full">
                <span class="text-xl font-bold">{{ component.name }}</span>
                <div class="flex items-center gap-4">
                    <span class="text-lg">{{ component.price }}</span>
                    <v-btn
                        @click="deleteComponents(props.componentType)"
                        color="green-700"
                        width="40"
                        height="40"
                        variant="plain"
                        class="text-xl"
                    >
                        <v-icon>mdi-delete</v-icon>
                    </v-btn>
                </div>
            </div>

            <ComponentDescription
                :componentType="props.componentType"
                :component="props.component"
            />
        </div>
    </div>

    <Modal
        v-model:isOpen="isModalOpen"
        :componentType="typeComponent"
        :selected-components="selectedComponents"
    />
</template>
