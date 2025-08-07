#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Chargeur d'embeddings pré-calculés pour le moteur de recherche sémantique
Charge les fichiers .npy, index FAISS et métadonnées sans les recalculer
"""

import os
import json
import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer, CrossEncoder
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)

class EmbeddingLoader:
    """Chargeur d'embeddings pré-calculés"""
    
    def __init__(self, embeddings_dir="embeddings"):
        """
        Initialise le chargeur d'embeddings
        
        Args:
            embeddings_dir: Répertoire contenant les embeddings pré-calculés
        """
        self.embeddings_dir = embeddings_dir
        self.engines = {}
        self.metadata = {}
        
        # Charger le modèle Sentence Transformers pour les nouvelles requêtes
        logger.info("Chargement du modèle Sentence Transformers pour les requêtes...")
        self.embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    
    def load_language_engine(self, language: str, index_type: str = "flat") -> Optional[Dict]:
        """
        Charge un moteur pour une langue spécifique
        
        Args:
            language: Code de langue (fr, en)
            index_type: Type d'index FAISS à charger
            
        Returns:
            dict: Moteur chargé avec index et métadonnées
        """
        lang_dir = os.path.join(self.embeddings_dir, language)
        
        if not os.path.exists(lang_dir):
            logger.warning(f"Répertoire d'embeddings non trouvé pour {language}: {lang_dir}")
            return None
        
        try:
            # Charger les métadonnées
            metadata_path = os.path.join(lang_dir, "metadata.pkl")
            if not os.path.exists(metadata_path):
                logger.error(f"Fichier de métadonnées non trouvé: {metadata_path}")
                return None
            
            with open(metadata_path, 'rb') as f:
                metadata = pickle.load(f)
            
            # Charger l'index FAISS
            index_path = os.path.join(lang_dir, f"faiss_index_{index_type}.idx")
            if not os.path.exists(index_path):
                logger.error(f"Index FAISS non trouvé: {index_path}")
                return None
            
            index = faiss.read_index(index_path)
            
            # Créer le moteur
            engine = {
                'index': index,
                'metadata': metadata,
                'questions': metadata['data_info']['questions'],
                'reponses': metadata['data_info']['reponses'],
                'commentaires': metadata['data_info']['commentaires'],
                'entreprises': metadata['data_info']['entreprises'],
                'annees': metadata['data_info']['annees'],
                'embedding_model': self.embedding_model
            }
            
            logger.info(f"✅ Moteur {language} chargé: {len(engine['questions'])} questions")
            return engine
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement du moteur {language}: {e}")
            return None
    
    def load_all_engines(self, languages: List[str] = None, index_type: str = "flat") -> Dict:
        """
        Charge tous les moteurs pour les langues spécifiées
        
        Args:
            languages: Liste des langues à charger (par défaut: fr, en)
            index_type: Type d'index FAISS
            
        Returns:
            dict: Dictionnaire des moteurs chargés
        """
        if languages is None:
            languages = ["fr", "en"]
        
        engines = {}
        
        for lang in languages:
            engine = self.load_language_engine(lang, index_type)
            if engine:
                engines[lang] = engine
                self.metadata[lang] = engine['metadata']
        
        logger.info(f"🎉 {len(engines)} moteurs chargés: {list(engines.keys())}")
        return engines
    
    def search(self, engine: Dict, query: str, top_k: int = 5, year_weighted: bool = False) -> List[Dict]:
        """
        Effectue une recherche dans un moteur chargé
        
        Args:
            engine: Moteur chargé
            query: Requête de recherche
            top_k: Nombre de résultats à retourner
            year_weighted: Si True, applique une pondération temporelle
            
        Returns:
            list: Liste des résultats
        """
        # Encoder la requête
        query_embedding = self.embedding_model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(query_embedding)
        
        # Recherche dans l'index
        distances, indices = engine['index'].search(query_embedding, top_k)
        indices = indices[0]
        distances = distances[0]
        
        results = []
        
        # Préparation du scoring pondéré par l'année
        if year_weighted:
            valid_years = []
            for y in engine['annees']:
                try:
                    valid_years.append(int(y))
                except ValueError:
                    continue
            
            if valid_years:
                y_min = min(valid_years)
                y_max = max(valid_years)
                gamma = 0.5  # Coefficient de pondération
            else:
                y_min = y_max = None
        else:
            y_min = y_max = None
        
        for idx, score in zip(indices, distances):
            base_score = float(score)
            
            if year_weighted and y_min is not None and y_max is not None and y_max != y_min:
                try:
                    current_year = int(engine['annees'][idx])
                except ValueError:
                    current_year = y_min
                weight = 1 + gamma * (current_year - y_min) / (y_max - y_min)
                final_score = base_score * weight
            else:
                final_score = base_score
            
            result = {
                "entreprise": engine['entreprises'][idx] if idx < len(engine['entreprises']) else "",
                "question": engine['questions'][idx],
                "reponse": engine['reponses'][idx] if idx < len(engine['reponses']) else "",
                "commentaire": engine['commentaires'][idx] if idx < len(engine['commentaires']) else "",
                "annee": engine['annees'][idx] if idx < len(engine['annees']) else "",
                "score": final_score
            }
            results.append(result)
        
        return results
    
    def get_engine_info(self, language: str) -> Optional[Dict]:
        """
        Récupère les informations d'un moteur
        
        Args:
            language: Code de langue
            
        Returns:
            dict: Informations du moteur
        """
        if language not in self.metadata:
            return None
        
        metadata = self.metadata[language]
        return {
            'language': language,
            'model_info': metadata['model_info'],
            'statistics': {
                'total_questions': len(metadata['data_info']['questions']),
                'unique_entreprises': len(set(metadata['data_info']['entreprises'])),
                'embedding_dimension': metadata['model_info']['embedding_dimension'],
                'calculation_date': metadata['calculation_info']['timestamp']
            }
        }
    
    def get_all_engines_info(self) -> Dict:
        """
        Récupère les informations de tous les moteurs
        
        Returns:
            dict: Informations de tous les moteurs
        """
        info = {}
        for lang in self.metadata.keys():
            info[lang] = self.get_engine_info(lang)
        return info

def load_engines_from_precomputed(embeddings_dir: str = "embeddings", 
                                languages: List[str] = None, 
                                index_type: str = "flat") -> Dict:
    """
    Fonction utilitaire pour charger les moteurs depuis les embeddings pré-calculés
    
    Args:
        embeddings_dir: Répertoire des embeddings
        languages: Langues à charger
        index_type: Type d'index FAISS
        
    Returns:
        dict: Moteurs chargés
    """
    loader = EmbeddingLoader(embeddings_dir)
    return loader.load_all_engines(languages, index_type)

def main():
    """Fonction de test du chargeur"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test du chargeur d'embeddings")
    parser.add_argument("--embeddings_dir", type=str, default="embeddings", 
                       help="Répertoire des embeddings pré-calculés")
    parser.add_argument("--languages", nargs="+", default=["fr", "en"], 
                       help="Langues à charger")
    parser.add_argument("--index_type", type=str, default="flat", 
                       help="Type d'index FAISS")
    parser.add_argument("--query", type=str, default="sécurité informatique", 
                       help="Requête de test")
    parser.add_argument("--top_k", type=int, default=3, 
                       help="Nombre de résultats")
    
    args = parser.parse_args()
    
    # Charger les moteurs
    loader = EmbeddingLoader(args.embeddings_dir)
    engines = loader.load_all_engines(args.languages, args.index_type)
    
    if not engines:
        print("❌ Aucun moteur chargé")
        return 1
    
    # Afficher les informations
    print("\n📊 Informations des moteurs:")
    for lang, info in loader.get_all_engines_info().items():
        print(f"  {lang}: {info['statistics']['total_questions']} questions")
    
    # Test de recherche
    print(f"\n🔍 Test de recherche: '{args.query}'")
    for lang, engine in engines.items():
        print(f"\n--- Résultats pour {lang} ---")
        results = loader.search(engine, args.query, args.top_k)
        
        for i, result in enumerate(results, 1):
            print(f"{i}. Score: {result['score']:.4f}")
            print(f"   Question: {result['question'][:100]}...")
            print(f"   Entreprise: {result['entreprise']}")
            print(f"   Année: {result['annee']}")
            print()
    
    return 0

if __name__ == "__main__":
    exit(main()) 