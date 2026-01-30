import axios from 'axios';

const API_BASE_URL = "http://localhost:8000"; // URL de FastAPI

export const apiService = {
  // Correspond à RAGPipeline.query()
  askQuestion: async (text, history, config) => {
    // On structure le payload selon les besoins de l'orchestrateur
    const payload = {
      query_text: text,
      // passe l'historique pour le Query Rewriting 
      chat_history: history, 
      top_k: 5,
      rerank_top_k: config.useReranker ? 3 : null,
      // Paramètres dynamiques pour l'orchestrateur
      llm_params: {
        model: config.model === 'Gemini' ? 'gemini-1.5-flash' : 'gpt-4o-mini',
        temperature: 0.7
      }
    };

    const response = await axios.post(`${API_BASE_URL}/query`, payload);
    return response.data; // Retourne l'objet RAGResponse converti en JSON
  },

  // Correspond à RAGPipeline.ingest()
  uploadFile: async (file) => {
    const formData = new FormData();
    formData.append("file", file);
    //  passer des paramètres au chunker via l'URL ou le body
    const response = await axios.post(`${API_BASE_URL}/ingest`, formData);
    return response.data;
  }
};