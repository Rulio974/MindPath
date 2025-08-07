#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Calculateur d'embeddings pour le moteur de recherche sémantique
Génère les fichiers .npy, index FAISS et métadonnées sans les charger en mémoire
"""

import os
import json
import glob
import argparse
import numpy as np
import faiss
import pickle
from datetime import datetime
from sentence_transformers import SentenceTransformer, CrossEncoder
from tqdm import tqdm
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('embedding_calculation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EmbeddingCalculator:
    """Calculateur d'embeddings qui génère les fichiers sans les charger"""
    
    def __init__(self, embedding_model_name="paraphrase-multilingual-MiniLM-L12-v2", 
                 crossencoder_model_name=None, output_dir="embeddings"):
        """
        Initialise le calculateur d'embeddings
        
        Args:
            embedding_model_name: Nom du modèle Sentence Transformers
            crossencoder_model_name: Nom du modèle Cross-Encoder (optionnel)
            output_dir: Répertoire de sortie pour les fichiers générés
        """
        self.embedding_model_name = embedding_model_name
        self.crossencoder_model_name = crossencoder_model_name
        self.output_dir = output_dir
        
        # Créer le répertoire de sortie
        os.makedirs(output_dir, exist_ok=True)
        
        # Charger les modèles
        logger.info(f"Chargement du modèle d'embedding: {embedding_model_name}")
        self.embedding_model = SentenceTransformer(embedding_model_name)
        
        if crossencoder_model_name:
            logger.info(f"Chargement du modèle cross-encoder: {crossencoder_model_name}")
            self.crossencoder = CrossEncoder(crossencoder_model_name)
        else:
            self.crossencoder = None
    
    def load_dataset(self, directory):
        """
        Charge les fichiers JSON d'un répertoire et extrait les données
        
        Args:
            directory: Répertoire contenant les fichiers JSON
            
        Returns:
            dict: Données extraites (questions, réponses, commentaires, etc.)
        """
        logger.info(f"Chargement des données depuis: {directory}")
        
        json_files = glob.glob(os.path.join(directory, "*.json"))
        if not json_files:
            logger.warning(f"Aucun fichier JSON trouvé dans {directory}")
            return None
        
        data = {
            'questions': [],
            'reponses': [],
            'commentaires': [],
            'entreprises': [],
            'annees': [],
            'metadata': []
        }
        
        for filepath in tqdm(json_files, desc="Chargement des fichiers JSON"):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    file_data = json.load(f)
                
                entreprise = file_data.get("Entreprise", "").strip()
                date_str = file_data.get("date", "").strip()
                annee = ""
                if date_str and "-" in date_str:
                    annee = date_str.split("-")[0]
                
                for item in file_data.get("data", []):
                    question = item.get("Question", "").strip()
                    if question:
                        data['questions'].append(question)
                        data['reponses'].append(item.get("Reponse", "").strip())
                        data['commentaires'].append(item.get("Commentaire", "").strip())
                        data['entreprises'].append(entreprise)
                        data['annees'].append(annee)
                        
                        # Métadonnées pour chaque question
                        metadata = {
                            'entreprise': entreprise,
                            'annee': annee,
                            'date': date_str,
                            'fichier_source': os.path.basename(filepath),
                            'reponse': item.get("Reponse", "").strip(),
                            'commentaire': item.get("Commentaire", "").strip()
                        }
                        data['metadata'].append(metadata)
                        
            except Exception as e:
                logger.error(f"Erreur lors du chargement de {filepath}: {e}")
        
        logger.info(f"Chargé {len(data['questions'])} questions depuis {len(json_files)} fichiers")
        return data
    
    def calculate_embeddings(self, questions, batch_size=64, save_embeddings=True):
        """
        Calcule les embeddings pour les questions
        
        Args:
            questions: Liste des questions
            batch_size: Taille des batchs pour le calcul
            save_embeddings: Si True, sauvegarde les embeddings en .npy
            
        Returns:
            numpy.ndarray: Matrice des embeddings
        """
        if not questions:
            raise ValueError("Aucune question à traiter")
        
        logger.info(f"Calcul des embeddings pour {len(questions)} questions...")
        
        # Calcul des embeddings par batch
        embeddings = self.embedding_model.encode(
            questions,
            convert_to_numpy=True,
            show_progress_bar=True,
            batch_size=batch_size
        )
        
        # Normalisation L2 pour FAISS
        faiss.normalize_L2(embeddings)
        
        logger.info(f"Embeddings calculés: {embeddings.shape}")
        
        if save_embeddings:
            embeddings_path = os.path.join(self.output_dir, "embeddings.npy")
            np.save(embeddings_path, embeddings)
            logger.info(f"Embeddings sauvegardés: {embeddings_path}")
        
        return embeddings
    
    def build_faiss_index(self, embeddings, index_type="flat"):
        """
        Construit l'index FAISS
        
        Args:
            embeddings: Matrice des embeddings
            index_type: Type d'index FAISS ("flat", "ivf", "hnsw")
            
        Returns:
            str: Chemin vers l'index FAISS sauvegardé
        """
        logger.info(f"Construction de l'index FAISS ({index_type})...")
        
        dim = embeddings.shape[1]
        
        if index_type == "flat":
            index = faiss.IndexFlatIP(dim)
        elif index_type == "ivf":
            nlist = min(4096, max(1, embeddings.shape[0] // 30))
            quantizer = faiss.IndexFlatIP(dim)
            index = faiss.IndexIVFFlat(quantizer, dim, nlist, faiss.METRIC_INNER_PRODUCT)
            index.train(embeddings)
        elif index_type == "hnsw":
            index = faiss.IndexHNSWFlat(dim, 32)
            index.hnsw.efConstruction = 200
        else:
            raise ValueError(f"Type d'index non supporté: {index_type}")
        
        index.add(embeddings)
        
        # Sauvegarder l'index
        index_path = os.path.join(self.output_dir, f"faiss_index_{index_type}.idx")
        faiss.write_index(index, index_path)
        
        logger.info(f"Index FAISS sauvegardé: {index_path} ({index.ntotal} vecteurs)")
        return index_path
    
    def save_metadata(self, data, embeddings_shape):
        """
        Sauvegarde les métadonnées
        
        Args:
            data: Données extraites
            embeddings_shape: Forme de la matrice d'embeddings
        """
        metadata = {
            'model_info': {
                'embedding_model': self.embedding_model_name,
                'crossencoder_model': self.crossencoder_model_name,
                'embedding_dimension': embeddings_shape[1],
                'num_questions': embeddings_shape[0]
            },
            'data_info': {
                'questions': data['questions'],
                'reponses': data['reponses'],
                'commentaires': data['commentaires'],
                'entreprises': data['entreprises'],
                'annees': data['annees'],
                'metadata': data['metadata']
            },
            'calculation_info': {
                'timestamp': datetime.now().isoformat(),
                'output_directory': self.output_dir
            }
        }
        
        metadata_path = os.path.join(self.output_dir, "metadata.pkl")
        with open(metadata_path, 'wb') as f:
            pickle.dump(metadata, f)
        
        logger.info(f"Métadonnées sauvegardées: {metadata_path}")
        
        # Sauvegarder aussi en JSON pour lisibilité
        metadata_json = {
            'model_info': metadata['model_info'],
            'calculation_info': metadata['calculation_info'],
            'statistics': {
                'total_questions': len(data['questions']),
                'unique_entreprises': len(set(data['entreprises'])),
                'years_range': f"{min(data['annees']) if data['annees'] else 'N/A'} - {max(data['annees']) if data['annees'] else 'N/A'}",
                'embedding_dimension': embeddings_shape[1]
            }
        }
        
        metadata_json_path = os.path.join(self.output_dir, "metadata.json")
        with open(metadata_json_path, 'w', encoding='utf-8') as f:
            json.dump(metadata_json, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Métadonnées JSON sauvegardées: {metadata_json_path}")
    
    def process_language(self, data_dir, language, batch_size=64, index_type="flat"):
        """
        Traite une langue complète (calcul + sauvegarde)
        
        Args:
            data_dir: Répertoire des données
            language: Code de langue (fr, en)
            batch_size: Taille des batchs
            index_type: Type d'index FAISS
        """
        logger.info(f"=== Traitement de la langue: {language} ===")
        
        # Créer le répertoire de sortie pour cette langue
        lang_output_dir = os.path.join(self.output_dir, language)
        os.makedirs(lang_output_dir, exist_ok=True)
        
        # Sauvegarder le répertoire de sortie temporairement
        original_output_dir = self.output_dir
        self.output_dir = lang_output_dir
        
        try:
            # Charger les données
            data = self.load_dataset(data_dir)
            if not data or not data['questions']:
                logger.warning(f"Aucune donnée trouvée pour {language}")
                return None
            
            # Calculer les embeddings
            embeddings = self.calculate_embeddings(data['questions'], batch_size)
            
            # Construire l'index FAISS
            index_path = self.build_faiss_index(embeddings, index_type)
            
            # Sauvegarder les métadonnées
            self.save_metadata(data, embeddings.shape)
            
            logger.info(f"✅ Langue {language} traitée avec succès")
            return {
                'language': language,
                'num_questions': len(data['questions']),
                'embedding_shape': embeddings.shape,
                'index_path': index_path,
                'output_dir': lang_output_dir
            }
            
        finally:
            # Restaurer le répertoire de sortie original
            self.output_dir = original_output_dir
    
    def process_all_languages(self, data_base_dir, languages=None, batch_size=64, index_type="flat"):
        """
        Traite toutes les langues
        
        Args:
            data_base_dir: Répertoire de base des données
            languages: Liste des langues à traiter (par défaut: fr, en)
            batch_size: Taille des batchs
            index_type: Type d'index FAISS
            
        Returns:
            dict: Résumé du traitement
        """
        if languages is None:
            languages = ["fr", "en"]
        
        results = {}
        
        for lang in languages:
            lang_dir = os.path.join(data_base_dir, lang)
            if os.path.exists(lang_dir):
                result = self.process_language(lang_dir, lang, batch_size, index_type)
                if result:
                    results[lang] = result
            else:
                logger.warning(f"Répertoire non trouvé: {lang_dir}")
        
        # Sauvegarder un résumé global
        summary = {
            'calculation_date': datetime.now().isoformat(),
            'embedding_model': self.embedding_model_name,
            'crossencoder_model': self.crossencoder_model_name,
            'languages_processed': list(results.keys()),
            'results': results,
            'total_questions': sum(r['num_questions'] for r in results.values())
        }
        
        summary_path = os.path.join(self.output_dir, "calculation_summary.json")
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Résumé global sauvegardé: {summary_path}")
        logger.info(f"🎉 Traitement terminé: {summary['total_questions']} questions traitées")
        
        return summary

def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(
        description="Calculateur d'embeddings pour le moteur de recherche sémantique"
    )
    parser.add_argument("--data_dir", type=str, default="backend/data", 
                       help="Répertoire contenant les sous-dossiers 'fr' et 'en'")
    parser.add_argument("--output_dir", type=str, default="embeddings", 
                       help="Répertoire de sortie pour les fichiers générés")
    parser.add_argument("--embedding_model", type=str, 
                       default="paraphrase-multilingual-MiniLM-L12-v2", 
                       help="Nom du modèle d'embedding")
    parser.add_argument("--crossencoder_model", type=str, default=None, 
                       help="Nom du modèle de cross-encoder")
    parser.add_argument("--batch_size", type=int, default=64, 
                       help="Taille des batchs pour la vectorisation")
    parser.add_argument("--index_type", type=str, default="flat", 
                       choices=["flat", "ivf", "hnsw"], 
                       help="Type d'index FAISS")
    parser.add_argument("--languages", nargs="+", default=["fr", "en"], 
                       help="Langues à traiter")
    
    args = parser.parse_args()
    
    # Vérifier que le répertoire de données existe
    if not os.path.exists(args.data_dir):
        logger.error(f"Répertoire de données non trouvé: {args.data_dir}")
        return 1
    
    try:
        # Créer le calculateur
        calculator = EmbeddingCalculator(
            embedding_model_name=args.embedding_model,
            crossencoder_model_name=args.crossencoder_model,
            output_dir=args.output_dir
        )
        
        # Traiter toutes les langues
        summary = calculator.process_all_languages(
            args.data_dir,
            languages=args.languages,
            batch_size=args.batch_size,
            index_type=args.index_type
        )
        
        print("\n" + "="*60)
        print("🎉 CALCUL DES EMBEDDINGS TERMINÉ")
        print("="*60)
        print(f"📁 Répertoire de sortie: {args.output_dir}")
        print(f"🔤 Langues traitées: {', '.join(summary['languages_processed'])}")
        print(f"📊 Total questions: {summary['total_questions']}")
        print(f"🤖 Modèle utilisé: {args.embedding_model}")
        print(f"📋 Résumé détaillé: {os.path.join(args.output_dir, 'calculation_summary.json')}")
        print("="*60)
        
        return 0
        
    except Exception as e:
        logger.error(f"Erreur lors du calcul des embeddings: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 