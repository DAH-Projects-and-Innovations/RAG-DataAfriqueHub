import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// En-tête d'authentification optionnel (défini via VITE_API_KEY dans .env)
const authHeaders = () => {
  const key = import.meta.env.VITE_API_KEY;
  return key ? { 'X-API-Key': key } : {};
};

export const apiService = {

  /** Récupère la liste des modèles disponibles depuis le backend (section models du YAML). */
  getModels: async () => {
    const response = await axios.get(`${API_BASE_URL}/models`, {
      headers: authHeaders(),
    });
    return response.data; // [{ id, label, provider, default }]
  },

  deleteFile: async (fileName) => {
    const encodedName = encodeURIComponent(fileName);
    const response = await axios.delete(`${API_BASE_URL}/ingest/${encodedName}`, {
      headers: authHeaders(),
    });
    return response.data;
  },

  askQuestion: async (text, history, config) => {
    const payload = {
      question: text,
      chat_history: history,
      top_k: 5,
      rerank_top_k: config.useReranker ? 3 : null,
      llm_params: {
        // config.modelId contient l'id technique (ex: "gpt-4o-mini")
        model: config.modelId || config.model,
        temperature: 0.7,
      },
    };

    const response = await axios.post(`${API_BASE_URL}/query`, payload, {
      headers: authHeaders(),
    });
    return response.data;
  },

  uploadFile: async (file) => {
    const formData = new FormData();
    formData.append("files", file);
    const response = await axios.post(`${API_BASE_URL}/ingest`, formData, {
      headers: authHeaders(),
    });
    return response.data;
  },
};
