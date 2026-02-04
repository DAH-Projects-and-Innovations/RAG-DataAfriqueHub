import React, { useState } from 'react';
import { Send, Upload, Database, ChevronLeft, ChevronRight, Menu, X } from 'lucide-react';
import LogoAfriqueHub from './assets/logo-afrique-hub.jpeg';
// Importe du service API ici
import { apiService } from './services/api'; 

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  // 1. NOUVEAU : Déclaration des états pour la configuration
  const [selectedModel, setSelectedModel] = useState('Gemini 1.5 Flash');
  const [rerankEnabled, setRerankEnabled] = useState(true);

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    const currentInput = input;
    setInput('');

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
          <div>
            <h3 className="text-xs font-bold uppercase text-slate-400 mb-3 tracking-wider">Documents</h3>
            <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-slate-200 rounded-2xl cursor-pointer hover:border-blue-400 hover:bg-blue-50 transition-all">
              <Upload className="text-slate-400 mb-2" size={24} />
              <span className="text-[11px] text-slate-500 font-medium">Glisser vos fichiers ici</span>
              <input type="file" className="hidden" />
            </label>
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
        </section>

        <footer className="p-4 md:p-6 bg-white border-t border-slate-200">
          <div className="max-w-4xl mx-auto flex gap-2 items-center bg-slate-100 p-2 rounded-2xl border border-slate-200 focus-within:ring-2 focus-within:ring-blue-400 transition-all">
            <input 
              className="flex-1 p-2 md:p-3 bg-transparent outline-none text-sm md:text-base"
              placeholder="Posez votre question..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
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