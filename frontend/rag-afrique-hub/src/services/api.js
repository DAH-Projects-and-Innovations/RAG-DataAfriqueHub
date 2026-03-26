import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const apiService = {

  /** Récupère la liste des modèles disponibles depuis le backend (section models du YAML). */
  getModels: async () => {
    const response = await axios.get(`${API_BASE_URL}/models`);
    return response.data; // [{ id, label, provider, default }]
  },

  deleteFile: async (fileName) => {
    const encodedName = encodeURIComponent(fileName);
    const response = await axios.delete(`${API_BASE_URL}/ingest/${encodedName}`);
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
      signal: config.signal,
    });
    return response.data;
  },

  uploadFile: async (file) => {
    const formData = new FormData();
    formData.append("files", file);
    //  passer des paramètres au chunker via l'URL ou le body
    const response = await axios.post(`${API_BASE_URL}/ingest`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }

    );
    return response.data;
  },
};
