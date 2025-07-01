#!/usr/bin/env python3
"""
BridgeFacile - Importation des données dans la base
==================================================

Script pour importer les articles de loi et leurs références
dans la base de données Supabase.

Auteur: BridgeFacile Team
Date: 2025-01-07
"""

import os
import sys
import json
import csv
import logging
import argparse
from typing import Dict, List, Any, Optional
import re
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("import_data.log")
    ]
)
logger = logging.getLogger(__name__)

class DatabaseImporter:
    """
    Classe pour importer les données des articles de loi dans la base de données.
    """
    
    def __init__(self, 
                 input_dir: str = "./output",
                 supabase_url: Optional[str] = None,
                 supabase_key: Optional[str] = None):
        """
        Initialise l'importateur de base de données.
        
        Args:
            input_dir: Répertoire contenant les fichiers JSON et CSV à importer
            supabase_url: URL de l'API Supabase (si None, utilise la variable d'environnement SUPABASE_URL)
            supabase_key: Clé API Supabase (si None, utilise la variable d'environnement SUPABASE_KEY)
        """
        self.input_dir = input_dir
        
        # Configurer Supabase
        self.supabase_url = supabase_url or os.environ.get('SUPABASE_URL')
        self.supabase_key = supabase_key or os.environ.get('SUPABASE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            logger.warning("URL ou clé Supabase non définie. Mode simulation activé.")
            self.simulation_mode = True
        else:
            self.simulation_mode = False
            self._init_supabase()
        
        logger.info(f"Importateur initialisé - Entrée: {input_dir}, Mode simulation: {self.simulation_mode}")
    
    def _init_supabase(self):
        """Initialise la connexion à Supabase."""
        try:
            from supabase import create_client
            
            self.supabase = create_client(self.supabase_url, self.supabase_key)
            logger.info("Connexion à Supabase établie")
        except ImportError:
            logger.error("Module supabase non installé. Exécutez 'pip install supabase'.")
            self.simulation_mode = True
        except Exception as e:
            logger.error(f"Erreur lors de la connexion à Supabase: {e}")
            self.simulation_mode = True
    
    def load_data(self) -> Dict[str, Any]:
        """
        Charge les données à importer depuis les fichiers JSON et CSV.
        
        Returns:
            Dict avec les données chargées
        """
        data = {
            "articles": {},
            "references": [],
            "categories": {}
        }
        
        # 1. Charger les articles depuis le JSON amélioré
        refs_dir = os.path.join(self.input_dir, "references")
        if os.path.exists(refs_dir):
            enhanced_json = os.path.join(refs_dir, "enhanced_articles.json")
            if os.path.exists(enhanced_json):
                with open(enhanced_json, 'r', encoding='utf-8') as f:
                    data["articles"] = json.load(f)
                logger.info(f"{len(data['articles'])} articles chargés depuis {enhanced_json}")
            else:
                logger.warning(f"Fichier {enhanced_json} non trouvé")
        
        # 2. Si le fichier amélioré n'existe pas, chercher le fichier original
        if not data["articles"]:
            json_files = [f for f in os.listdir(self.input_dir) if f.startswith('bridge_law_data_') and f.endswith('.json')]
            
            if json_files:
                # Trier par date de modification (le plus récent en premier)
                json_files.sort(key=lambda f: os.path.getmtime(os.path.join(self.input_dir, f)), reverse=True)
                json_file = os.path.join(self.input_dir, json_files[0])
                
                with open(json_file, 'r', encoding='utf-8') as f:
                    data["articles"] = json.load(f)
                logger.info(f"{len(data['articles'])} articles chargés depuis {json_file}")
        
        # 3. Charger les références depuis le CSV amélioré
        if os.path.exists(refs_dir):
            refs_csv = os.path.join(refs_dir, "enhanced_references.csv")
            if os.path.exists(refs_csv):
                with open(refs_csv, 'r', encoding='utf-8', newline='') as f:
                    reader = csv.DictReader(f)
                    data["references"] = list(reader)
                logger.info(f"{len(data['references'])} références chargées depuis {refs_csv}")
        
        # 4. Extraire les catégories à partir des titres d'articles
        data["categories"] = self._extract_categories(data["articles"])
        
        return data
    
    def _extract_categories(self, articles: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Extrait les catégories à partir des titres d'articles.
        
        Args:
            articles: Dict avec les articles
        
        Returns:
            Dict avec les catégories et leurs articles
        """
        categories = {}
        
        for article_id, article_data in articles.items():
            title = article_data.get('title', '')
            
            # Extraire la catégorie à partir du titre
            category_match = re.search(r'LOI\s+\d+\s+-\s+(.*?)(?:\.{2,}|\s{2,}|$)', title, re.IGNORECASE)
            
            if category_match:
                category = category_match.group(1).strip()
                if category not in categories:
                    categories[category] = []
                categories[category].append(article_id)
            else:
                if "Autres" not in categories:
                    categories["Autres"] = []
                categories["Autres"].append(article_id)
        
        logger.info(f"{len(categories)} catégories extraites")
        return categories
    
    def import_to_supabase(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Importe les données dans Supabase.
        
        Args:
            data: Dict avec les données à importer
        
        Returns:
            Dict avec les résultats de l'importation
        """
        if self.simulation_mode:
            logger.info("Mode simulation: les données ne seront pas importées dans Supabase")
            return self._simulate_import(data)
        
        results = {
            "categories": 0,
            "articles": 0,
            "metadata": 0,
            "references": 0,
            "errors": []
        }
        
        try:
            # 1. Importer les catégories
            categories_map = {}  # {category_name: category_id}
            
            for category_name, article_ids in data["categories"].items():
                try:
                    response = self.supabase.table('categories').insert({
                        'name': category_name,
                        'description': f"Catégorie pour les articles: {', '.join(article_ids[:5])}..."
                    }).execute()
                    
                    if response.data:
                        category_id = response.data[0]['id']
                        categories_map[category_name] = category_id
                        results["categories"] += 1
                except Exception as e:
                    logger.error(f"Erreur lors de l'importation de la catégorie {category_name}: {e}")
                    results["errors"].append(f"Catégorie {category_name}: {str(e)}")
            
            logger.info(f"{results['categories']} catégories importées")
            
            # 2. Importer les articles
            articles_map = {}  # {article_id: db_id}
            
            for article_id, article_data in data["articles"].items():
                title = article_data.get('title', '')
                content = article_data.get('content', '')
                source_file = article_data.get('source_file', '')
                
                # Déterminer la catégorie
                category_id = None
                for category_name, cat_article_ids in data["categories"].items():
                    if article_id in cat_article_ids and category_name in categories_map:
                        category_id = categories_map[category_name]
                        break
                
                try:
                    response = self.supabase.table('articles').insert({
                        'article_id': article_id,
                        'title': title,
                        'content': content,
                        'source_file': source_file,
                        'category_id': category_id,
                        'is_active': True
                    }).execute()
                    
                    if response.data:
                        db_id = response.data[0]['id']
                        articles_map[article_id] = db_id
                        results["articles"] += 1
                        
                        # Importer les métadonnées
                        word_count = len(content.split())
                        reference_count = len(article_data.get('references', []))
                        citation_count = len(article_data.get('referenced_by', []))
                        
                        self.supabase.table('article_metadata').insert({
                            'article_id': db_id,
                            'word_count': word_count,
                            'reference_count': reference_count,
                            'citation_count': citation_count,
                            'importance_score': citation_count * 0.7 + reference_count * 0.3
                        }).execute()
                        
                        results["metadata"] += 1
                        
                        # Associer l'article à sa catégorie
                        if category_id:
                            self.supabase.table('article_categories').insert({
                                'article_id': db_id,
                                'category_id': category_id
                            }).execute()
                except Exception as e:
                    logger.error(f"Erreur lors de l'importation de l'article {article_id}: {e}")
                    results["errors"].append(f"Article {article_id}: {str(e)}")
            
            logger.info(f"{results['articles']} articles importés")
            
            # 3. Importer les références
            for ref in data["references"]:
                source_id = ref.get('Article_Source')
                target_id = ref.get('Article_Cible')
                
                if source_id in articles_map and target_id in articles_map:
                    try:
                        self.supabase.table('article_references').insert({
                            'source_article_id': articles_map[source_id],
                            'target_article_id': articles_map[target_id],
                            'reference_type': 'direct'
                        }).execute()
                        
                        results["references"] += 1
                    except Exception as e:
                        logger.error(f"Erreur lors de l'importation de la référence {source_id} -> {target_id}: {e}")
                        results["errors"].append(f"Référence {source_id} -> {target_id}: {str(e)}")
            
            logger.info(f"{results['references']} références importées")
            
        except Exception as e:
            logger.error(f"Erreur générale lors de l'importation: {e}")
            results["errors"].append(f"Erreur générale: {str(e)}")
        
        return results
    
    def _simulate_import(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simule l'importation des données (pour le mode simulation).
        
        Args:
            data: Dict avec les données à importer
        
        Returns:
            Dict avec les résultats simulés
        """
        results = {
            "categories": len(data["categories"]),
            "articles": len(data["articles"]),
            "metadata": len(data["articles"]),
            "references": len(data["references"]),
            "errors": [],
            "simulation": True
        }
        
        # Générer un fichier SQL d'insertion
        sql_file = os.path.join(self.input_dir, f"import_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql")
        
        with open(sql_file, 'w', encoding='utf-8') as f:
            f.write("-- Script d'importation des données générées\n")
            f.write("-- Date: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n\n")
            
            # Catégories
            f.write("-- Insertion des catégories\n")
            for i, (category_name, article_ids) in enumerate(data["categories"].items(), 1):
                f.write(f"INSERT INTO categories (id, name, description) VALUES ({i}, '{category_name.replace("'", "''")}', 'Catégorie pour les articles de loi');\n")
            
            f.write("\n-- Insertion des articles\n")
            for i, (article_id, article_data) in enumerate(data["articles"].items(), 1):
                title = article_data.get('title', '').replace("'", "''")
                content = article_data.get('content', '').replace("'", "''")
                source_file = article_data.get('source_file', '')
                
                # Déterminer la catégorie
                category_id = 1  # Par défaut
                for cat_id, (category_name, cat_article_ids) in enumerate(data["categories"].items(), 1):
                    if article_id in cat_article_ids:
                        category_id = cat_id
                        break
                
                f.write(f"INSERT INTO articles (id, article_id, title, content, source_file, category_id) VALUES ({i}, '{article_id}', '{title}', '{content}', '{source_file}', {category_id});\n")
            
            f.write("\n-- Insertion des métadonnées\n")
            for i, (article_id, article_data) in enumerate(data["articles"].items(), 1):
                content = article_data.get('content', '')
                word_count = len(content.split())
                reference_count = len(article_data.get('references', []))
                citation_count = len(article_data.get('referenced_by', []))
                
                f.write(f"INSERT INTO article_metadata (article_id, word_count, reference_count, citation_count) VALUES ({i}, {word_count}, {reference_count}, {citation_count});\n")
            
            f.write("\n-- Insertion des références\n")
            for i, ref in enumerate(data["references"], 1):
                source_id = ref.get('Article_Source')
                target_id = ref.get('Article_Cible')
                
                # Convertir les IDs d'articles en IDs de base de données
                source_db_id = list(data["articles"].keys()).index(source_id) + 1 if source_id in data["articles"] else 0
                target_db_id = list(data["articles"].keys()).index(target_id) + 1 if target_id in data["articles"] else 0
                
                if source_db_id > 0 and target_db_id > 0:
                    f.write(f"INSERT INTO article_references (source_article_id, target_article_id, reference_type) VALUES ({source_db_id}, {target_db_id}, 'direct');\n")
        
        logger.info(f"Script SQL d'importation généré: {sql_file}")
        results["sql_file"] = sql_file
        
        return results
    
    def run_import(self) -> Dict[str, Any]:
        """
        Exécute le processus complet d'importation.
        
        Returns:
            Dict avec les résultats de l'importation
        """
        logger.info("Démarrage du processus d'importation...")
        
        # 1. Charger les données
        data = self.load_data()
        
        # 2. Importer dans Supabase
        results = self.import_to_supabase(data)
        
        logger.info(f"Importation terminée: {results['articles']} articles, {results['references']} références")
        return results


def install_dependencies():
    """Installe les dépendances nécessaires."""
    import subprocess
    import sys
    
    packages = ['supabase']
    
    print("Installation des dépendances...")
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package} installé")
        except subprocess.CalledProcessError:
            print(f"❌ Erreur installation {package}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Importe les articles de loi dans la base de données Supabase")
    parser.add_argument("--input", "-i", default="./output", help="Répertoire contenant les fichiers à importer")
    parser.add_argument("--url", "-u", help="URL de l'API Supabase")
    parser.add_argument("--key", "-k", help="Clé API Supabase")
    parser.add_argument("--install", action="store_true", help="Installer les dépendances")
    parser.add_argument("--simulate", "-s", action="store_true", help="Mode simulation (ne pas importer dans Supabase)")
    
    args = parser.parse_args()
    
    if args.install:
        install_dependencies()
        sys.exit(0)
    
    # Créer l'importateur
    importer = DatabaseImporter(
        input_dir=args.input,
        supabase_url=args.url,
        supabase_key=args.key
    )
    
    # Forcer le mode simulation si demandé
    if args.simulate:
        importer.simulation_mode = True
    
    # Exécuter l'importation
    try:
        results = importer.run_import()
        
        print("\n✅ Importation terminée avec succès!")
        
        if results.get("simulation", False):
            print("⚠️ Mode simulation: les données n'ont pas été importées dans Supabase")
            print(f"📄 Script SQL généré: {results.get('sql_file', 'N/A')}")
        
        print(f"📊 Catégories importées: {results['categories']}")
        print(f"📄 Articles importés: {results['articles']}")
        print(f"📝 Métadonnées importées: {results['metadata']}")
        print(f"🔗 Références importées: {results['references']}")
        
        if results["errors"]:
            print(f"\n⚠️ {len(results['errors'])} erreurs rencontrées:")
            for i, error in enumerate(results["errors"][:5], 1):
                print(f"  {i}. {error}")
            
            if len(results["errors"]) > 5:
                print(f"  ... et {len(results['errors']) - 5} autres erreurs")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        logger.error(f"Erreur lors de l'importation: {e}", exc_info=True)

