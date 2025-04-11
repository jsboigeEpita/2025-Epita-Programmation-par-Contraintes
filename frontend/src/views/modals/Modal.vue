<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import { images } from '../../assets/index';
import { getComponents, getConfig, postComponents } from '../../api/api';
import type {
    SelectedComponents,
    Component,
    Case,
    Powersupply,
    Videocard,
    CpuCooler,
    Storage,
    Motherboard,
    Cpu,
    Ram,
} from '../../types';
import ComponentDescription from '../../components/ComponentDescription.vue';

const props = defineProps<{
    isOpen: boolean;
    componentType: string;
    selectedComponents: SelectedComponents;
}>();

const emit = defineEmits(['update:isOpen']);

const internalDialog = ref(props.isOpen);
const components = ref<Component[]>([]);
const searchTerm = ref<string>('');

const filteredComponents = computed(() => {
    if (!searchTerm.value.trim()) {
        return components.value;
    }
    return components.value.filter((comp) =>
        comp.name.toLowerCase().includes(searchTerm.value.toLowerCase())
    );
});

const closeModal = async (component: Component) => {
    if (props.componentType === 'powersupply') {
        props.selectedComponents.powersupply = component as Powersupply;
        await postComponents('powersupply', component);
    } else if (props.componentType === 'case') {
        props.selectedComponents.case = component as Case;
        await postComponents('case', component);
    } else if (props.componentType === 'videocard') {
        props.selectedComponents.videocard = component as Videocard;
        await postComponents('videocard', component);
    } else if (props.componentType === 'cpu-cooler') {
        props.selectedComponents.cpuCooler = component as CpuCooler;
        await postComponents('cpu-cooler', component);
    } else if (props.componentType === 'storage') {
        props.selectedComponents.storage = component as Storage;
        await postComponents('storage', component);
    } else if (props.componentType === 'motherboard') {
        props.selectedComponents.motherboard = component as Motherboard;
        await postComponents('motherboard', component);
    } else if (props.componentType === 'cpu') {
        props.selectedComponents.cpu = component as Cpu;
        await postComponents('cpu', component);
    } else if (props.componentType === 'ram') {
        props.selectedComponents.ram = component as Ram;
        await postComponents('ram', component);
    }
    internalDialog.value = false;
};
watch(
    () => props.isOpen,
    (newVal) => {
        internalDialog.value = newVal;
    }
);

watch(
    () => internalDialog.value,
    (newVal) => {
        emit('update:isOpen', newVal);
    }
);

watch(
    () => props.componentType,
    async (newVal) => {
        internalDialog.value = true;
        components.value = [];
        getComponents(newVal, 1).then((res) => {
            components.value = res.slice(0, 500);
        });
		await getConfig();
    }
);
</script>

<template>
    <v-dialog v-model="internalDialog" max-width="800">
        <template v-slot:default="{ isActive }">
            <v-card class="bg-[var(--color-background-secondary-dark)]">
                <v-card-title class="text-[var(--color-text-dark)] mb-[-20px]">
                    <div class="flex items-center justify-between w-full">
                        <div class="w-[33%] flex items-center justify-start">
                            <v-btn
                                icon
                                class="text-[var(--color-text-dark)] bg-[var(--color-background)] text-white"
                                @click="isActive.value = false"
                            >
                                <v-icon>mdi-close</v-icon>
                            </v-btn>
                        </div>

                        <div class="w-[33%] flex flex-col items-center justify-center">
                            <div class="flex items-center justify-center space-x-2">
                                <img
                                    v-if="props.componentType === 'case'"
                                    :src="images.Case"
                                    alt="Case"
                                    class="w-10"
                                />
                                <img
                                    v-if="props.componentType === 'powersupply'"
                                    :src="images.Alim"
                                    alt="Alim"
                                    class="w-10"
                                />
                                <img
                                    v-if="props.componentType === 'videocard'"
                                    :src="images.Graphics"
                                    alt="Graphics"
                                    class="w-10"
                                />
                                <img
                                    v-if="props.componentType === 'cpu-cooler'"
                                    :src="images.Ventirad"
                                    alt="Ventirad"
                                    class="w-10"
                                />
                                <img
                                    v-if="props.componentType === 'storage'"
                                    :src="images.Disque"
                                    alt="Disque"
                                    class="w-10"
                                />
                                <img
                                    v-if="props.componentType === 'motherboard'"
                                    :src="images.Motherboard"
                                    alt="Motherboard"
                                    class="w-10"
                                />
                                <img
                                    v-if="props.componentType === 'cpu'"
                                    :src="images.Processeur"
                                    alt="Processeur"
                                    class="w-10"
                                />
                                <img
                                    v-if="props.componentType === 'ram'"
                                    :src="images.Ram"
                                    alt="Ram"
                                    class="w-10"
                                />
                                <span
                                    class="text-2xl font-bold text-[var(--color-text-dark)] capitalize"
                                >
                                    {{ props.componentType }}
                                </span>
                            </div>
                        </div>

                        <div class="w-[33%] flex justify-end">
                            <v-text-field
                                v-model="searchTerm"
                                label="Rechercher"
                                variant="outlined"
                                density="compact"
                                hide-details
                                class="w-[180px] text-sm"
                            />
                        </div>
                    </div>
                </v-card-title>

                <v-card-text class="text-[var(--color-text-dark)]">
                    <div
                        class="flex flex-col w-full"
                        v-for="component in filteredComponents"
                        :key="component.id"
                    >
                        <button
                            v-if="component.price"
                            @click="closeModal(component)"
                            class="px-4 pt-1 flex flex-col w-full h-[80px] border-b-2 hover:bg-[green] hover:border-opacity-50"
                        >
                            <div class="flex w-full justify-between">
                                <span>{{ component.name }}</span>
                                <span>{{ component.price }}</span>
                            </div>
                            <ComponentDescription
                                :componentType="props.componentType"
                                :component="component"
                            />
                        </button>
                    </div>
                </v-card-text>
            </v-card>
        </template>
    </v-dialog>
</template>

<style>
.v-text-field input {
    background-color: var(--color-background-secondary-dark) !important;
}
</style>
