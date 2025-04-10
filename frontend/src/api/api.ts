import axios from 'axios';
import type { Component } from '../types';
import { useSessionStore } from '../stores/sessionStore';

const baseURL = 'http://localhost:8080';

export async function getComponents(component: string, page: number): Promise<any> {
    try {
        const response = await axios.get(`${baseURL}/api/${component}`, {
            params: { page },
            withCredentials: true,
        });
        console.log("Réponse de getComponent :", response.data);

        return response.data;
    } catch (error) {
        console.error('Erreur lors de la récupération des composants :', error);
        throw error;
    }
}

export async function postComponents(componentType: string, component: Component): Promise<any> {
    try {
        const response = await axios.post(
            `${baseURL}/api/${componentType}`,
            component,
            {
                withCredentials: true,
                headers: {
                    'Content-Type': 'application/json',
                },
            }
        );

        console.log("Réponse de postComponent :", response.data);
        return response.data;
    } catch (error) {
        console.error('Erreur lors de l\'envoi des composants :', error);
        throw error;
    }
}

export async function deleteComponent(componentType: string): Promise<any> {
    try {
        const response = await axios.delete(
            `${baseURL}/api/${componentType}`,
            {
                withCredentials: true,
            }
        );
        console.log("Réponse de deleteComponent :", response.data);
        return response.data;
    } catch (error) {
        console.error('Erreur lors de l\'envoi des composants :', error);
        throw error;
    }
}

export async function getConfig(): Promise<any> {
    try {
        const response = await axios.get(`${baseURL}/api/config`, {
            withCredentials: true,
        });
		const sessionStore = useSessionStore();
		sessionStore.setSessionId(response.data.sessionId);
        console.log("Réponse de getConfig :", response.data);
        return response.data;
    } catch (error) {
        console.error('Erreur lors de la récupération des composants :', error);
        throw error;
    }
}
