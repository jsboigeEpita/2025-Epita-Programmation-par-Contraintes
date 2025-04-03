<template>
    <div class="min-h-screen flex flex-col items-center relative">
        <span class="text-2xl font-bold mt-10 text-white">Configurateur</span>

        <div class="flex items-center mt-20 space-x-8">
            <img
                :src="isSelected('Case') ? CaseGreen : Case"
                alt="Case"
                class="w-32 cursor-pointer transition-opacity duration-300"
                :class="isSelected('Case') ? 'opacity-100' : 'opacity-20 hover:opacity-100'"
                @click="toggleComponent('Case')"
            />
            <img
                :src="isSelected('Alim') ? AlimGreen : Alim"
                alt="Alim"
                class="w-32 cursor-pointer transition-opacity duration-300"
                :class="isSelected('Alim') ? 'opacity-100' : 'opacity-20 hover:opacity-100'"
                @click="toggleComponent('Alim')"
            />
            <img
                :src="isSelected('Graphics') ? GraphicsGreen : Graphics"
                alt="Graphics"
                class="w-32 cursor-pointer transition-opacity duration-300"
                :class="isSelected('Graphics') ? 'opacity-100' : 'opacity-20 hover:opacity-100'"
                @click="toggleComponent('Graphics')"
            />
            <img
                :src="isSelected('Ventirad') ? VentiradGreen : Ventirad"
                alt="Ventirad"
                class="w-32 cursor-pointer transition-opacity duration-300"
                :class="isSelected('Ventirad') ? 'opacity-100' : 'opacity-20 hover:opacity-100'"
                @click="toggleComponent('Ventirad')"
            />
            <img
                :src="isSelected('Watercooling') ? WatercoolingGreen : Watercooling"
                alt="Watercooling"
                class="w-32 cursor-pointer transition-opacity duration-300"
                :class="isSelected('Watercooling') ? 'opacity-100' : 'opacity-20 hover:opacity-100'"
                @click="toggleComponent('Watercooling')"
            />
        </div>

        <div class="flex items-center mt-5 space-x-8">
			<img
                :src="isSelected('Watercooling') ? WatercoolingGreen : Disque"
                alt="Watercooling"
                class="w-32 cursor-pointer transition-opacity duration-300"
                :class="isSelected('Watercooling') ? 'opacity-100' : 'opacity-20 hover:opacity-100'"
                @click="toggleComponent('Watercooling')"
            />
			<img
                :src="isSelected('Watercooling') ? WatercoolingGreen : Motherboard"
                alt="Watercooling"
                class="w-32 cursor-pointer transition-opacity duration-300"
                :class="isSelected('Watercooling') ? 'opacity-100' : 'opacity-20 hover:opacity-100'"
                @click="toggleComponent('Watercooling')"
            />
			<img
                :src="isSelected('Watercooling') ? WatercoolingGreen : Processeur"
                alt="Watercooling"
                class="w-32 cursor-pointer transition-opacity duration-300"
                :class="isSelected('Watercooling') ? 'opacity-100' : 'opacity-20 hover:opacity-100'"
                @click="toggleComponent('Watercooling')"
            />
			<img
                :src="isSelected('Watercooling') ? WatercoolingGreen : Ram"
                alt="Watercooling"
                class="w-32 cursor-pointer transition-opacity duration-300"
                :class="isSelected('Watercooling') ? 'opacity-100' : 'opacity-20 hover:opacity-100'"
                @click="toggleComponent('Watercooling')"
            />
		</div>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

import Alim from '../assets/images/computer-white/Alim.png';
import Case from '../assets/images/computer-white/Case.png';
import Graphics from '../assets/images/computer-white/Graphics.png';
import Ventirad from '../assets/images/computer-white/Ventirad.png';
import Watercooling from '../assets/images/computer-white/Watercooling.png';
import Disque from '../assets/images/computer-white/Disque.png';
import Motherboard from '../assets/images/computer-white/Motherboard.png';
import Processeur from '../assets/images/computer-white/Processeur.png';
import Ram from '../assets/images/computer-white/Ram.png';


import AlimGreen from '../assets/images/computer-green/Alim.png';
import CaseGreen from '../assets/images/computer-green/Case.png';
import GraphicsGreen from '../assets/images/computer-green/Graphics.png';
import VentiradGreen from '../assets/images/computer-green/Ventirad.png';
import WatercoolingGreen from '../assets/images/computer-green/Watercooling.png';

const selectedComponents = ref<string[]>([]);

function isSelected(name: string): boolean {
    return selectedComponents.value.includes(name);
}

function toggleComponent(name: string) {
    if (isSelected(name)) {
        selectedComponents.value = selectedComponents.value.filter((item) => item !== name);
    } else {
        selectedComponents.value.push(name);
    }
}
</script>
