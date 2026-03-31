"""
LLM-based Query Rewriter - Génère des variantes de requêtes pour améliorer la couverture
"""

from typing import List, Optional
from src.core.interfaces import IQueryRewriter, ILLM


class LLMQueryRewriter(IQueryRewriter):
    """
    Réécriture de requêtes en utilisant un LLM.
    Génère plusieurs variantes d'une requête pour améliorer la récupération.
    """
    
    def __init__(
        self,
        llm: ILLM,
        num_variations: int = 3,
        temperature: float = 0.8,
        **kwargs
    ):
        """
        Initialise le query rewriter LLM.
        
        Args:
            llm: Instance LLM pour générer les variantes
            num_variations: Nombre de variantes à générer
            temperature: Température pour la génération
            **kwargs: Paramètres additionnels
        """
        self.llm = llm
        self.num_variations = num_variations
        self.temperature = temperature
    
    def rewrite(self, query: str, **kwargs) -> List[str]:
        """
        Réécrit une requête en générant des variantes.
        
        Args:
            query: Requête originale
            **kwargs: Paramètres additionnels
            
        Returns:
            Liste contenant la requête originale + variantes
        """
        # Toujours inclure la requête originale
        results = [query]
        
        # Générer des variantes seulement si num_variations > 0
        if self.num_variations <= 0:
            return results
        
        prompt = self._create_rewrite_prompt(query)
        
        try:
            # Générer les variantes à travers le LLM
            response = self.llm.generate(
                prompt=prompt,
                temperature=self.temperature,
                max_tokens=500
            )
            
            # Parser la réponse pour extraire les variantes
            variations = self._parse_variations(response)
            
            # Limiter au nombre demandé de variantes
            variations = variations[:self.num_variations]
            results.extend(variations)
            
        except Exception as e:
            # En cas d'erreur, retourner juste la requête originale
            print(f"⚠️ Erreur lors de la génération de variantes: {e}")
            return results
        
        return results
    
    def _create_rewrite_prompt(self, query: str) -> str:
        """
        Crée le prompt pour générer des variantes de requête.
        
        Args:
            query: Requête originale
            
        Returns:
            Prompt pour le LLM
        """
        prompt = f"""Tu es un expert en reformulation de requêtes de recherche.
Génère {self.num_variations} variantes différentes de la requête suivante.
Les variantes doivent:
- Capturer le même sens et intention
- Utiliser des mots-clés alternatifs
- Être formulées différemment

Requête originale: "{query}"

Génère les variantes en les numérotant (1., 2., 3., etc.).
Réponds UNIQUEMENT avec les variantes numérotées, sans explications."""
        
        return prompt
    
    def _parse_variations(self, response: str) -> List[str]:
        """
        Parse la réponse du LLM pour extraire les variantes.
        
        Args:
            response: Réponse du LLM
            
        Returns:
            Liste des variantes extraites
        """
        variations = []
        lines = response.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            # Ignorer les lignes vides
            if not line:
                continue
            
            # Enlever la numérotation (1., 2., etc.)
            if line[0].isdigit() and '.' in line[:3]:
                line = line.split('.', 1)[1].strip()
            
            if line:
                variations.append(line)
        
        return variations
