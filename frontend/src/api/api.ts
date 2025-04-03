import axios from 'axios'

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

export async function getAvailableOptions(config: any) {
  //config = { motor: 'electrique', battery: '', transmission: '' }
  //const response = await apiClient.post('/config/check', config)
  return { motor: ['electrique'], battery: ['test'], transmission: ['test'] }
  //return response.data
}

export default apiClient
