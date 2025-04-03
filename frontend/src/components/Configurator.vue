<template>
    <div>
        <h1>Configuration de produit</h1>

        <div>
            <label>Motorisation :</label>
            <select v-model="selectedMotor" @change="onOptionChange('motor', selectedMotor)">
                <option value="">-- Choisir --</option>
                <option v-for="option in motorOptions" :key="option" :value="option">
                    {{ option }}
                </option>
            </select>
        </div>

        <div>
            <label>Batterie :</label>
            <select v-model="selectedBattery" @change="onOptionChange('battery', selectedBattery)">
                <option value="">-- Choisir --</option>
                <option v-for="option in batteryOptions" :key="option" :value="option">
                    {{ option }}
                </option>
            </select>
        </div>

        <div>
            <label>Transmission :</label>
            <select
                v-model="selectedTransmission"
                @change="onOptionChange('transmission', selectedTransmission)"
            >
                <option value="">-- Choisir --</option>
                <option v-for="option in transmissionOptions" :key="option" :value="option">
                    {{ option }}
                </option>
            </select>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { getAvailableOptions } from '../api/api';

const motorOptions = ref<string[]>([]);
const batteryOptions = ref<string[]>([]);
const transmissionOptions = ref<string[]>([]);
const selectedMotor = ref('');
const selectedBattery = ref('');
const selectedTransmission = ref('');

async function fetchOptions() {
    const config = {
        motor: selectedMotor.value,
        battery: selectedBattery.value,
        transmission: selectedTransmission.value,
    };
    try {
        const data = await getAvailableOptions(config);
        motorOptions.value = data.motor;
        batteryOptions.value = data.battery;
        transmissionOptions.value = data.transmission;
    } catch (error) {
        console.error('Erreur lors de la récupération des options', error);
    }
}

onMounted(fetchOptions);

function onOptionChange(optionType: string, value: string) {
    console.log(`Changement dans ${optionType} => ${value}`);
    fetchOptions();
}
</script>