import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export const apiService = {
  // Correspond à RAGPipeline.query()

  deleteFile: async (fileName) => {
    // Encode le nom du fichier pour gérer les espaces/caractères spéciaux
    const encodedName = encodeURIComponent(fileName);
    const response = await axios.delete(`${API_BASE_URL}/ingest/${encodedName}`);
    return response.data;
  },

  askQuestion: async (text, history, config) => {
    // On crée une correspondance (mapping) entre le nom affiché et l'ID attendu par le backend
     const modelMapping = {
      "Gemini 1.5 Flash": "gemini-1.5-flash",
      "GPT-4o-mini": "gpt-4o-mini",
      "Ollama-Llama3": "ollama-llama3",
      "Mistral-7B": "mistral-7b"
    };
    // structure le payload selon les besoins de l'orchestrateur
    const payload = {
      question: text,
      // passe l'historique pour le Query Rewriting 
      chat_history: history, 
      top_k: 5,
      rerank_top_k: config.useReranker ? 3 : null,
      // Paramètres dynamiques pour l'orchestrateur
      llm_params: {
        // On prend la valeur mappée, ou la valeur brute si non trouvée (pour éviter les erreurs si un nouveau modèle est ajouté sans mise à jour du mapping)
        model: modelMapping[config.model] || config.model,
        temperature: 0.7
      }
    };

    const response = await axios.post(`${API_BASE_URL}/query`, payload);
    return response.data; // Retourne l'objet RAGResponse converti en JSON
  },

  // Correspond à RAGPipeline.ingest()
  uploadFile: async (file) => {
    const formData = new FormData();
    formData.append("files", file);
    //  passer des paramètres au chunker via l'URL ou le body
    const response = await axios.post(`${API_BASE_URL}/ingest`, formData,
      // Optionnel : configurer les en-têtes si nécessaire (axios gère généralement le multipart automatiquement)
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    );
    return response.data;
  }
};


// une simulation de l'API pour le développement frontend sans backend opérationnel. À remplacer par les appels réels à FastAPI une fois que le backend est prêt.
/*export const apiService = {
  uploadFile: async (file) => {
    // Simule une attente réseau de 1.5s
    await new Promise(resolve => setTimeout(resolve, 1500));
    return { status: "success" };
  },

  askQuestion: async (text, history, config) => {
    // Simule une attente de réflexion de l'IA de 2s
    await new Promise(resolve => setTimeout(resolve, 2000));
    return {
      answer: "Ceci est une réponse générée par le simulateur. Votre question était : " + text,
      sources: [
        { metadata: { filename: "doc_test.pdf" }, score: 0.85 }
      ]
    };
  }
};*/