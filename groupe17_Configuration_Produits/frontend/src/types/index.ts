export type SelectedComponentsResponse = {
	id: string,
	price: number,
	sessionId: string,
	cpu: Cpu | null,
	cpuCooler: CpuCooler | null,
	motherboard: Motherboard | null,
	pcCase: Case | null,
	powerConsumption: number,
	memory: Ram | null,
	powerSupply: Powersupply | null,
	storageDevice: Storage | null,
	videoCard: Videocard | null,
}

export type SelectedComponents = {
	case: Case | null,
	motherboard: Motherboard | null,
	cpu: Cpu | null,
	cpuCooler: CpuCooler | null,
	ram: Ram | null,
	videocard: Videocard | null,
	powersupply: Powersupply | null,
	storage: Storage | null,
}

export type Component = Case | Motherboard | Cpu | CpuCooler | Ram | Videocard | Powersupply | Storage;

export interface Case {
	id: string,
	name: string,
	price: string,
	color : string,
	dimensions: string,
	externalVolume: string,
	internalBays: string,
	powerSupply: string,
	sidePanel: string,
	type: string,
}

export interface Motherboard {
	id: string,
	name: string,
	price: string,
	color : string,
	formFactor: string,
	maxMemory: string,
	memorySlots: string,
	powerConsumption: number,
	socketCpu: string,
}

export interface Cpu {
	id: string,
	name: string,
	price: string,
	coreCount: string,
	integratedGraphics: string,
	microarchitecture: string,
	performanceCoreBoostClock: string,
	performanceCoreClock: string,
	powerConsumption: number,
	tdp: string,
}

export interface CpuCooler {
	id: string,
	name: string,
	price: string,
	color : string,
	powerConsumption: number,
	fanRpm: string,
	noiseLevel: string,
	radiatorSize: string,
}

export interface Ram {
	id: string,
	name: string,
	price: string,
	color : string,
	cl: string,
	costGB: string,
	fwl: string,
	powerConsumption: number,
	modules: string,
	speed: string,
}

export interface Videocard {
	id: string,
	name: string,
	price: string,
	color : string,
	powerConsumption: number,
	boostClock: string,
	chipset: string,
	coreClock: string,
	length: string,
	memory: string,
}

export interface Powersupply {
	id: string,
	name: string,
	price: string,
	color : string,
	efficiencyRating: string,
	modular: string,
	type: string,
	wattage: string,
}

export interface Storage {
	id: string,
	name: string,
	price: string,
	capacity: string,
	formFactor: string,
	interfaceType: string,
	manufacturer: string,
	readSpeed: string,
	writeSpeed: string,
	StorageType: string,
}