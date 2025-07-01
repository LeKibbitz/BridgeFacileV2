#!/usr/bin/env python3
"""
BridgeFacile - Traitement des PDFs du Code 2017
===============================================

Module spécialisé pour parser les PDFs du Code 2017 de bridge,
extraire les articles de loi et détecter les références entre articles.

Auteur: BridgeFacile Team
Date: 2025-01-07
"""

import os
import sys
import re
import csv
import json
import logging
from typing import Dict, List, Tuple, Set, Optional, Any
from datetime import datetime
import shutil

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("bridge_law_parser.log")
    ]
)
logger = logging.getLogger(__name__)

class BridgeLawParser:
    """
    Parser spécialisé pour les documents du Code 2017 de bridge.
    Extrait les articles de loi et détecte les références entre articles.
    """
    
    def __init__(self, 
                 input_dir: str = "./input",
                 output_dir: str = "./output"):
        """
        Initialise le parser avec les répertoires d'entrée et de sortie.
        
        Args:
            input_dir: Répertoire contenant les PDFs du Code 2017
            output_dir: Répertoire de sortie pour les fichiers CSV
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.available_methods = self._detect_available_methods()
        
        # Créer le répertoire de sortie s'il n'existe pas
        os.makedirs(output_dir, exist_ok=True)
        
        # Patterns regex pour la détection des articles et références
        self.article_pattern = re.compile(r'(?:LOI|ARTICLE)\s+(\d+[A-Z]?(?:\.\d+)?)', re.IGNORECASE)
        self.reference_pattern = re.compile(r'(?:Loi|Article|Voir|Cf\.?)\s+(\d+[A-Z]?(?:\.\d+)?)', re.IGNORECASE)
        
        # Stockage des articles et références
        self.articles = {}  # {article_id: {content, title, references, ...}}
        self.references = {}  # {article_id: [referenced_articles]}
        
        logger.info(f"Parser initialisé - Entrée: {input_dir}, Sortie: {output_dir}")
        logger.info(f"Méthodes disponibles: {', '.join(self.available_methods)}")
    
    def _detect_available_methods(self) -> List[str]:
        """Détecte les méthodes de parsing disponibles."""
        methods = []
        
        try:
            import pdfplumber
            methods.append('pdfplumber')
        except ImportError:
            pass
        
        try:
            import PyPDF2
            methods.append('pypdf2')
        except ImportError:
            pass
        
        if os.system('which pdftotext > /dev/null 2>&1') == 0:
            methods.append('pdftotext')
        
        return methods
    
    def parse_pdf(self, pdf_path: str, method: Optional[str] = None) -> Dict[str, Any]:
        """Parse un PDF et retourne le contenu extrait."""
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"Fichier PDF non trouvé: {pdf_path}")
        
        if method is None:
            if 'pdfplumber' in self.available_methods:
                method = 'pdfplumber'
            elif 'pypdf2' in self.available_methods:
                method = 'pypdf2'
            elif 'pdftotext' in self.available_methods:
                method = 'pdftotext'
            else:
                raise RuntimeError("Aucune méthode de parsing disponible. Installez pdfplumber ou PyPDF2.")
        
        logger.info(f"Parsing de {pdf_path} avec la méthode: {method}")
        
        if method == 'pdfplumber':
            return self._parse_with_pdfplumber(pdf_path)
        elif method == 'pypdf2':
            return self._parse_with_pypdf2(pdf_path)
        elif method == 'pdftotext':
            return self._parse_with_pdftotext(pdf_path)
        else:
            raise ValueError(f"Méthode de parsing non supportée: {method}")
    
    def _parse_with_pdfplumber(self, pdf_path: str) -> Dict[str, Any]:
        """Parse avec pdfplumber (méthode recommandée)."""
        import pdfplumber
        
        result = {
            'text': '',
            'pages': [],
            'metadata': {},
            'method': 'pdfplumber'
        }
        
        with pdfplumber.open(pdf_path) as pdf:
            result['metadata'] = {
                'num_pages': len(pdf.pages),
                'file_size': os.path.getsize(pdf_path),
                'filename': os.path.basename(pdf_path)
            }
            
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text() or ''
                result['pages'].append({
                    'page_number': i + 1,
                    'text': page_text,
                    'char_count': len(page_text)
                })
                result['text'] += page_text + '\n'
        
        return result
    
    def _parse_with_pypdf2(self, pdf_path: str) -> Dict[str, Any]:
        """Parse avec PyPDF2 (méthode de fallback)."""
        import PyPDF2
        
        result = {
            'text': '',
            'pages': [],
            'metadata': {},
            'method': 'pypdf2'
        }
        
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            result['metadata'] = {
                'num_pages': len(reader.pages),
                'file_size': os.path.getsize(pdf_path),
                'filename': os.path.basename(pdf_path)
            }
            
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text() or ''
                result['pages'].append({
                    'page_number': i + 1,
                    'text': page_text,
                    'char_count': len(page_text)
                })
                result['text'] += page_text + '\n'
        
        return result
    
    def _parse_with_pdftotext(self, pdf_path: str) -> Dict[str, Any]:
        """Parse avec pdftotext (méthode système)."""
        import subprocess
        
        result = {
            'text': '',
            'pages': [],
            'metadata': {},
            'method': 'pdftotext'
        }
        
        try:
            output = subprocess.run(
                ['pdftotext', pdf_path, '-'],
                capture_output=True,
                text=True,
                check=True
            )
            
            result['text'] = output.stdout
            result['metadata'] = {
                'file_size': os.path.getsize(pdf_path),
                'filename': os.path.basename(pdf_path)
            }
            
            # Estimation du nombre de pages (approximative)
            page_breaks = result['text'].count('\f')
            result['metadata']['num_pages'] = max(1, page_breaks + 1)
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Erreur pdftotext: {e}")
        
        return result
    
    def extract_articles(self, pdf_path: str) -> Dict[str, Dict[str, Any]]:
        """
        Extrait les articles de loi d'un PDF du Code 2017.
        
        Returns:
            Dict avec les articles extraits {article_id: {content, title, ...}}
        """
        # Parser le PDF
        result = self.parse_pdf(pdf_path)
        text = result['text']
        
        # Extraire les articles
        articles = {}
        current_article = None
        current_content = []
        
        # Diviser le texte en lignes
        lines = text.split('\n')
        
        for line in lines:
            # Détecter un nouvel article
            article_match = self.article_pattern.search(line)
            
            if article_match:
                # Si on était déjà en train de traiter un article, le sauvegarder
                if current_article:
                    articles[current_article] = {
                        'content': '\n'.join(current_content),
                        'title': current_content[0] if current_content else '',
                        'references': self._extract_references('\n'.join(current_content)),
                        'source_file': os.path.basename(pdf_path)
                    }
                
                # Commencer un nouvel article
                current_article = article_match.group(1)
                current_content = [line]
            elif current_article:
                # Continuer à ajouter du contenu à l'article courant
                current_content.append(line)
        
        # Sauvegarder le dernier article
        if current_article and current_content:
            articles[current_article] = {
                'content': '\n'.join(current_content),
                'title': current_content[0] if current_content else '',
                'references': self._extract_references('\n'.join(current_content)),
                'source_file': os.path.basename(pdf_path)
            }
        
        logger.info(f"Extraction terminée: {len(articles)} articles trouvés dans {pdf_path}")
        return articles
    
    def _extract_references(self, text: str) -> List[str]:
        """
        Extrait les références vers d'autres articles dans un texte.
        
        Returns:
            Liste des IDs d'articles référencés
        """
        references = []
        
        # Trouver toutes les références
        for match in self.reference_pattern.finditer(text):
            ref = match.group(1)
            if ref not in references:
                references.append(ref)
        
        return references
    
    def process_all_pdfs(self) -> Dict[str, Dict[str, Any]]:
        """
        Traite tous les PDFs du répertoire d'entrée.
        
        Returns:
            Dict avec tous les articles extraits
        """
        all_articles = {}
        
        # Lister tous les fichiers PDF
        pdf_files = [f for f in os.listdir(self.input_dir) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            logger.warning(f"Aucun fichier PDF trouvé dans {self.input_dir}")
            return all_articles
        
        logger.info(f"Traitement de {len(pdf_files)} fichiers PDF...")
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(self.input_dir, pdf_file)
            try:
                # Extraire les articles
                articles = self.extract_articles(pdf_path)
                
                # Ajouter à la collection complète
                all_articles.update(articles)
                
                logger.info(f"✅ {pdf_file}: {len(articles)} articles extraits")
            except Exception as e:
                logger.error(f"❌ Erreur avec {pdf_file}: {e}")
        
        # Mettre à jour les références croisées
        self._update_cross_references(all_articles)
        
        # Sauvegarder les articles
        self.articles = all_articles
        
        return all_articles
    
    def _update_cross_references(self, articles: Dict[str, Dict[str, Any]]) -> None:
        """
        Met à jour les références croisées entre articles.
        
        Args:
            articles: Dict avec tous les articles extraits
        """
        # Construire le graphe de références
        references = {}
        
        for article_id, article_data in articles.items():
            refs = article_data.get('references', [])
            references[article_id] = refs
            
            # Ajouter les références inverses
            for ref in refs:
                if ref in articles:
                    if 'referenced_by' not in articles[ref]:
                        articles[ref]['referenced_by'] = []
                    
                    if article_id not in articles[ref]['referenced_by']:
                        articles[ref]['referenced_by'].append(article_id)
        
        # Sauvegarder les références
        self.references = references
        
        logger.info(f"Références croisées mises à jour pour {len(articles)} articles")
    
    def save_to_csv(self) -> Dict[str, str]:
        """
        Sauvegarde les articles extraits en CSV.
        
        Returns:
            Dict avec les chemins des fichiers CSV créés
        """
        if not self.articles:
            logger.warning("Aucun article à sauvegarder. Exécutez process_all_pdfs() d'abord.")
            return {}
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_files = {}
        
        # 1. CSV des articles
        articles_csv = os.path.join(self.output_dir, f"bridge_articles_{timestamp}.csv")
        with open(articles_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'Article_ID', 'Titre', 'Contenu', 'Source', 'Références', 'Référencé_Par'
            ])
            
            for article_id, article_data in self.articles.items():
                writer.writerow([
                    article_id,
                    article_data.get('title', ''),
                    article_data.get('content', ''),
                    article_data.get('source_file', ''),
                    ','.join(article_data.get('references', [])),
                    ','.join(article_data.get('referenced_by', []))
                ])
        
        csv_files['articles'] = articles_csv
        logger.info(f"Articles sauvegardés dans: {articles_csv}")
        
        # 2. CSV des références
        references_csv = os.path.join(self.output_dir, f"bridge_references_{timestamp}.csv")
        with open(references_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Article_Source', 'Article_Cible'])
            
            for article_id, refs in self.references.items():
                for ref in refs:
                    if ref in self.articles:  # Ne sauvegarder que les références valides
                        writer.writerow([article_id, ref])
        
        csv_files['references'] = references_csv
        logger.info(f"Références sauvegardées dans: {references_csv}")
        
        # 3. CSV des métadonnées
        metadata_csv = os.path.join(self.output_dir, f"bridge_metadata_{timestamp}.csv")
        with open(metadata_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'Article_ID', 'Nombre_Mots', 'Nombre_Références', 'Nombre_Citations'
            ])
            
            for article_id, article_data in self.articles.items():
                content = article_data.get('content', '')
                word_count = len(content.split())
                ref_count = len(article_data.get('references', []))
                cited_count = len(article_data.get('referenced_by', []))
                
                writer.writerow([
                    article_id,
                    word_count,
                    ref_count,
                    cited_count
                ])
        
        csv_files['metadata'] = metadata_csv
        logger.info(f"Métadonnées sauvegardées dans: {metadata_csv}")
        
        # 4. Fichier JSON complet (pour intégration web)
        json_file = os.path.join(self.output_dir, f"bridge_law_data_{timestamp}.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.articles, f, ensure_ascii=False, indent=2)
        
        csv_files['json'] = json_file
        logger.info(f"Données JSON sauvegardées dans: {json_file}")
        
        return csv_files
    
    def create_individual_article_files(self) -> List[str]:
        """
        Crée des fichiers individuels pour chaque article (pour l'intégration web).
        
        Returns:
            Liste des chemins des fichiers créés
        """
        if not self.articles:
            logger.warning("Aucun article à sauvegarder. Exécutez process_all_pdfs() d'abord.")
            return []
        
        # Créer un répertoire pour les articles individuels
        articles_dir = os.path.join(self.output_dir, "articles")
        os.makedirs(articles_dir, exist_ok=True)
        
        created_files = []
        
        for article_id, article_data in self.articles.items():
            # Nettoyer l'ID pour le nom de fichier
            safe_id = article_id.replace('.', '_')
            file_path = os.path.join(articles_dir, f"article_{safe_id}.json")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(article_data, f, ensure_ascii=False, indent=2)
            
            created_files.append(file_path)
        
        logger.info(f"{len(created_files)} fichiers d'articles individuels créés dans: {articles_dir}")
        return created_files
    
    def generate_navigation_index(self) -> str:
        """
        Génère un fichier d'index pour la navigation entre articles.
        
        Returns:
            Chemin du fichier d'index créé
        """
        if not self.articles:
            logger.warning("Aucun article à indexer. Exécutez process_all_pdfs() d'abord.")
            return ""
        
        # Créer l'index
        index = {
            "articles": {},
            "categories": {},
            "stats": {
                "total_articles": len(self.articles),
                "total_references": sum(len(refs) for refs in self.references.values())
            }
        }
        
        # Ajouter les articles à l'index
        for article_id, article_data in self.articles.items():
            # Version simplifiée pour l'index
            index["articles"][article_id] = {
                "title": article_data.get('title', ''),
                "references": article_data.get('references', []),
                "referenced_by": article_data.get('referenced_by', []),
                "source_file": article_data.get('source_file', '')
            }
        
        # Sauvegarder l'index
        index_file = os.path.join(self.output_dir, "bridge_law_index.json")
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Index de navigation créé: {index_file}")
        return index_file
    
    def generate_web_assets(self) -> Dict[str, str]:
        """
        Génère les fichiers nécessaires pour l'intégration web.
        
        Returns:
            Dict avec les chemins des fichiers créés
        """
        web_assets = {}
        
        # 1. Créer le répertoire des assets web
        web_dir = os.path.join(self.output_dir, "web")
        os.makedirs(web_dir, exist_ok=True)
        
        # 2. Copier les données JSON
        json_file = os.path.join(self.output_dir, "bridge_law_data.json")
        if os.path.exists(json_file):
            web_json = os.path.join(web_dir, "bridge_law_data.json")
            shutil.copy(json_file, web_json)
            web_assets['json'] = web_json
        
        # 3. Créer un fichier de configuration
        config = {
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "article_count": len(self.articles),
            "reference_count": sum(len(refs) for refs in self.references.values()),
            "structure": {
                "articles": "Liste des articles avec leur contenu",
                "references": "Graphe des références entre articles",
                "metadata": "Métadonnées sur les articles"
            }
        }
        
        config_file = os.path.join(web_dir, "config.json")
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        web_assets['config'] = config_file
        
        logger.info(f"Assets web générés dans: {web_dir}")
        return web_assets
    
    def run_full_process(self) -> Dict[str, Any]:
        """
        Exécute le processus complet de traitement des PDFs.
        
        Returns:
            Dict avec les résultats du traitement
        """
        logger.info("Démarrage du traitement complet...")
        
        # 1. Traiter tous les PDFs
        self.process_all_pdfs()
        
        # 2. Sauvegarder en CSV
        csv_files = self.save_to_csv()
        
        # 3. Créer les fichiers individuels
        article_files = self.create_individual_article_files()
        
        # 4. Générer l'index de navigation
        index_file = self.generate_navigation_index()
        
        # 5. Générer les assets web
        web_assets = self.generate_web_assets()
        
        results = {
            "articles": len(self.articles),
            "references": sum(len(refs) for refs in self.references.values()),
            "csv_files": csv_files,
            "article_files": len(article_files),
            "index_file": index_file,
            "web_assets": web_assets
        }
        
        logger.info(f"Traitement complet terminé: {len(self.articles)} articles extraits")
        return results


def install_dependencies():
    """Installe les dépendances nécessaires."""
    import subprocess
    import sys
    
    packages = ['pdfplumber', 'PyPDF2']
    
    print("Installation des dépendances...")
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package} installé")
        except subprocess.CalledProcessError:
            print(f"❌ Erreur installation {package}")


if __name__ == "__main__":
    # Vérifier les arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--install":
        install_dependencies()
        sys.exit(0)
    
    # Répertoires par défaut
    input_dir = "./input"
    output_dir = "./output"
    
    # Permettre de spécifier les répertoires en ligne de commande
    if len(sys.argv) > 2:
        input_dir = sys.argv[1]
        output_dir = sys.argv[2]
    
    # Créer le parser
    parser = BridgeLawParser(input_dir, output_dir)
    
    # Exécuter le traitement complet
    try:
        results = parser.run_full_process()
        
        print("\n✅ Traitement terminé avec succès!")
        print(f"📊 Articles extraits: {results['articles']}")
        print(f"🔗 Références détectées: {results['references']}")
        print("\n📁 Fichiers générés:")
        
        for csv_type, csv_path in results['csv_files'].items():
            print(f"  - {csv_type}: {os.path.basename(csv_path)}")
        
        print(f"\n📂 Répertoire de sortie: {output_dir}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        logger.error(f"Erreur lors du traitement: {e}", exc_info=True)

