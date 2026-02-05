import React, { useState } from 'react';
import { Send, Upload, Database, ChevronLeft, ChevronRight, Menu, X } from 'lucide-react';
import LogoAfriqueHub from './assets/logo-afrique-hub.jpeg';
// Importe du service API ici
import { apiService } from './services/api'; 

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState(null);

  // 1. NOUVEAU : Déclaration des états pour la configuration
  const [selectedModel, setSelectedModel] = useState('Gemini 1.5 Flash');
  const [rerankEnabled, setRerankEnabled] = useState(true);

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    const currentInput = input;
    setInput('');
    setIsTyping(true);

    try {
      // Utilisation des états selectedModel et rerankEnabled pour l'appel API
      const data = await apiService.askQuestion(currentInput, messages, {
        model: selectedModel,
        useReranker: rerankEnabled
      });

      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: data.answer, 
        sources: data.sources 
      }]);
    } catch (error) {
      console.error("Erreur de connexion au RAG:", error);
      setError("Une erreur est survenue lors de la connexion à l'assistant. Veuillez réessayer.");
      // on fait disparaitre le message d'erreur après 5 secondes
      setTimeout(() => setError(null), 5000);
    } finally {
      setIsTyping(false);
    }
  };

  // 2. Crée la fonction pour gérer l'upload
  const handleFileUpload = async (event) => {
    const files = Array.from(event.target.files);
    if (files.length === 0) return;

    setIsUploading(true);
    try {
      for (const file of files) {
        // Appel API pour chaque fichier
        await apiService.uploadFile(file);
        // Mise à jour de la liste locale pour l'affichage
        setUploadedFiles(prev => [...prev, { name: file.name, size: file.size }]);
      }
      alert("Documents indexés avec succès !");
    } catch (error) {
      console.error("Erreur d'upload:", error);
      alert("Erreur lors de l'indexation du document.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="flex h-screen bg-slate-50 text-slate-900 overflow-hidden relative">
      
      <button 
        onClick={() => setIsSidebarOpen(!isSidebarOpen)}
        className={`fixed top-4 z-50 p-2 bg-blue-600 text-white rounded-full shadow-lg transition-all duration-300 hover:bg-blue-700
          ${isSidebarOpen ? 'left-72.5' : 'left-4'}`}
      >
        {isSidebarOpen ? <ChevronLeft size={20} /> : <ChevronRight size={20} />}
      </button>

      <aside className={`
        fixed inset-y-0 left-0 z-40 w-80 bg-white border-r border-slate-200 p-6 transform transition-transform duration-300 ease-in-out
        ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:relative lg:translate-x-0 ${!isSidebarOpen && 'lg:hidden'}
      `}>
        <div className="flex items-center gap-2 font-bold text-xl text-blue-600 mb-10">
          <img src={LogoAfriqueHub} alt="Logo" className="w-10 h-10 object-contain" />
          <span>RAG Data Afrique Hub</span>
        </div>

        <div className="space-y-8">
          
         {/* <div>
            <h3 className="text-xs font-bold uppercase text-slate-400 mb-3 tracking-wider">Documents</h3>
            <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-slate-200 rounded-2xl cursor-pointer hover:border-blue-400 hover:bg-blue-50 transition-all">
              <Upload className="text-slate-400 mb-2" size={24} />
              <span className="text-[11px] text-slate-500 font-medium">Glisser vos fichiers ici</span>
              <input type="file" className="hidden" />
            </label>
          </div> */}

          <div>
            <h3 className="text-xs font-bold uppercase text-slate-400 mb-3 tracking-wider">Documents</h3>
            <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-slate-200 rounded-2xl cursor-pointer hover:border-blue-400 hover:bg-blue-50 transition-all">
              <Upload className={`${isUploading ? 'animate-bounce' : ''} text-slate-400 mb-2`} size={24} />
              <span className="text-[11px] text-slate-500 font-medium">
                {isUploading ? "Indexation en cours..." : "Glisser vos fichiers ici"}
              </span>
              {/* Ajout du onChange et de l'attribut multiple */}
              <input type="file" className="hidden" multiple onChange={handleFileUpload} disabled={isUploading} />
            </label>

            {/* 4. Liste des fichiers affichée sous la zone d'upload */}
            <div className="mt-4 space-y-2 max-h-40 overflow-y-auto">
              {uploadedFiles.map((f, i) => (
                <div key={i} className="flex items-center gap-2 p-2 bg-slate-50 rounded-lg border border-slate-100 text-[11px] text-slate-600">
                  <Database size={14} className="text-blue-500" />
                  <span className="truncate flex-1">{f.name}</span>
                  <span className="text-[9px] opacity-50">{(f.size / 1024).toFixed(0)} KB</span>
                </div>
              ))}
            </div>
          </div>
          
          {/* 2. NOUVEAU : Liaison du Select et de la Checkbox avec les états */}
          <div>
            <h3 className="text-xs font-bold uppercase text-slate-400 mb-3 tracking-wider">Sélecteur de modèle :</h3>
            <select 
              className="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 outline-none"
              value={selectedModel} // Liaison
              onChange={(e) => setSelectedModel(e.target.value)} 
            >
              <option value="Gemini 1.5 Flash">Gemini 1.5 Flash</option>
              <option value="GPT-4o-mini">GPT-4o-mini</option>
              <option value="Ollama-Llama3">Llama 3 (Local/Gratuit)</option>
              <option value="Mistral-7B">Mistral 7B (Local/Gratuit)</option>
            </select>
            
            <div className="mt-4 flex items-center gap-3 p-3 bg-slate-50 rounded-xl border border-slate-100">
              <input 
                type="checkbox" 
                id="rerank" 
                className="w-4 h-4 text-blue-600" 
                checked={rerankEnabled} // Liaison
                onChange={(e) => setRerankEnabled(e.target.checked)} 
              />
              <label htmlFor="rerank" className="text-sm font-medium text-slate-600 cursor-pointer">
                Re-ranking activé
              </label>
            </div>
          </div>
        </div>
      </aside>

      <main className="flex-1 flex flex-col min-w-0 bg-white lg:bg-slate-50">
        <header className="h-16 bg-white border-b border-slate-200 flex items-center px-16 lg:px-8 shadow-sm">
          <h1 className="font-semibold text-slate-700 truncate">Assistant pour répondre à vos questions</h1>
        </header>

          {/* Affichage d'une bannière d'erreur si une erreur est présente */}
        {error && (
          <div className="mx-8 mt-4 p-3 bg-red-100 border border-red-200 text-red-700 rounded-lg flex items-center justify-between animate-in fade-in slide-in-from-top-2">
            <span className="text-sm font-medium">{error}</span>
            <button onClick={() => setError(null)} className="text-red-500 hover:text-red-700 transition">
              <X size={16} />
            </button>
          </div>
        )}

        <section className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6">
          {messages.length === 0 && (
            <div className="h-full flex flex-col items-center justify-center text-center opacity-40">
              <Database size={48} className="mb-4 text-blue-600" />
              <p className="text-lg">Posez vos questions, nous cherchons dans vos documents</p>
            </div>
          )}
          
          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[85%] md:max-w-2xl p-4 rounded-2xl shadow-sm leading-relaxed
                ${m.role === 'user' ? 'bg-blue-600 text-white' : 'bg-white border border-slate-200'}`}>
                {m.content}
                
                {m.sources && (
                  <div className="mt-3 pt-3 border-t border-slate-100 flex flex-wrap gap-2">
                    <span className="text-[10px] font-bold uppercase opacity-60 italic">Source :</span>
                    {m.sources.map((source, idx) => (
                      <div key={idx} className="flex items-center gap-1 bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full font-bold">
                        <span className="text-[10px]">
                          {typeof source === 'object' ? (source.metadata?.filename || "Document") : source}
                        </span>
                        {/* Affichage du score si disponible (Architecture Tâche 1) */}
                        {source.score && (
                          <span className="text-[9px] bg-blue-200 px-1 rounded text-blue-800">
                            {Math.round(source.score * 100)}%
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          {isTyping && (
            <div className="flex justify-start">
              <div className="bg-white border border-slate-200 p-4 rounded-2xl text-slate-400 text-sm flex items-center gap-2">
                <div className="flex gap-1">
                  <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce"></span>
                  <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:0.2s]"></span>
                  <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:0.4s]"></span>
                </div>
                L'assistant analyse les documents...
              </div>
            </div>
          )}
        </section>

        <footer className="p-4 md:p-6 bg-white border-t border-slate-200">
          <div className="max-w-4xl mx-auto flex gap-2 items-center bg-slate-100 p-2 rounded-2xl border border-slate-200 focus-within:ring-2 focus-within:ring-blue-400 transition-all">
            <textarea 
              className="flex-1 p-2 md:p-3 bg-transparent outline-none text-sm md:text-base resize-none max-h-40"
              placeholder="Posez votre question..."
              rows="1"
              value={input}
              onChange={(e) => {
                setInput(e.target.value);
                // Ajuste la hauteur automatiquement
                e.target.style.height = 'auto';
                e.target.style.height = `${e.target.scrollHeight}px`;
              }}
              onKeyDown={(e) =>{
                if(e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage();
                  e.target.style.height = 'auto'; // Réinitialise la hauteur après envoi
                }
              }}
            />
            <button 
              onClick={handleSendMessage}
              className="p-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-transform active:scale-95"
            >
              <Send size={18} />
            </button>
          </div>
        </footer>
      </main>

      {isSidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/20 z-30 lg:hidden" 
          onClick={() => setIsSidebarOpen(false)}
        />
      )}
    </div>
  );
}

export default App;