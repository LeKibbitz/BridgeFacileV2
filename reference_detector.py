#!/usr/bin/env python3
"""
BridgeFacile - Détection avancée des références entre articles
=============================================================

Module spécialisé pour améliorer la détection des références entre articles
du Code 2017 de bridge.

Auteur: BridgeFacile Team
Date: 2025-01-07
"""

import os
import re
import json
import csv
import logging
from typing import Dict, List, Set, Tuple, Any, Optional
import networkx as nx
from collections import defaultdict

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("reference_detector.log")
    ]
)
logger = logging.getLogger(__name__)

class ReferenceDetector:
    """
    Détecteur avancé de références entre articles du Code 2017 de bridge.
    """
    
    def __init__(self, 
                 input_dir: str = "./output",
                 output_dir: str = "./output/references"):
        """
        Initialise le détecteur de références.
        
        Args:
            input_dir: Répertoire contenant les fichiers CSV et JSON générés par le parser
            output_dir: Répertoire de sortie pour les fichiers de références améliorés
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        
        # Créer le répertoire de sortie s'il n'existe pas
        os.makedirs(output_dir, exist_ok=True)
        
        # Patterns regex pour la détection des références
        self.reference_patterns = [
            # Format standard: "Loi 40" ou "Article 40"
            re.compile(r'(?:Loi|Article|Voir|Cf\.?)\s+(\d+[A-Z]?(?:\.\d+)?)', re.IGNORECASE),
            
            # Format avec parenthèses: "(voir Loi 40)"
            re.compile(r'\(\s*(?:voir|cf\.?)\s+(?:Loi|Article)\s+(\d+[A-Z]?(?:\.\d+)?)\s*\)', re.IGNORECASE),
            
            # Format avec tiret: "- Loi 40"
            re.compile(r'-\s*(?:Loi|Article)\s+(\d+[A-Z]?(?:\.\d+)?)', re.IGNORECASE),
            
            # Format avec section: "Loi 40.2" ou "Article 40B"
            re.compile(r'(?:Loi|Article)\s+(\d+[A-Z]?(?:\.\d+)?[A-Z]?)', re.IGNORECASE),
            
            # Format numérique simple: "40" (contexte dépendant)
            re.compile(r'(?<=\s)(\d+)(?=\s)', re.IGNORECASE)
        ]
        
        # Stockage des articles et références
        self.articles = {}  # {article_id: {content, title, references, ...}}
        self.references = {}  # {article_id: [referenced_articles]}
        self.reference_graph = nx.DiGraph()  # Graphe orienté des références
        
        logger.info(f"Détecteur de références initialisé - Entrée: {input_dir}, Sortie: {output_dir}")
    
    def load_articles(self, json_file: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        Charge les articles depuis un fichier JSON.
        
        Args:
            json_file: Chemin vers le fichier JSON contenant les articles
                      Si None, cherche le fichier le plus récent dans input_dir
        
        Returns:
            Dict avec les articles chargés
        """
        if json_file is None:
            # Chercher le fichier JSON le plus récent
            json_files = [f for f in os.listdir(self.input_dir) if f.startswith('bridge_law_data_') and f.endswith('.json')]
            
            if not json_files:
                raise FileNotFoundError(f"Aucun fichier JSON d'articles trouvé dans {self.input_dir}")
            
            # Trier par date de modification (le plus récent en premier)
            json_files.sort(key=lambda f: os.path.getmtime(os.path.join(self.input_dir, f)), reverse=True)
            json_file = os.path.join(self.input_dir, json_files[0])
        
        logger.info(f"Chargement des articles depuis: {json_file}")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            self.articles = json.load(f)
        
        logger.info(f"{len(self.articles)} articles chargés")
        return self.articles
    
    def detect_references(self) -> Dict[str, List[str]]:
        """
        Détecte les références entre articles avec une précision améliorée.
        
        Returns:
            Dict avec les références détectées {article_id: [referenced_articles]}
        """
        if not self.articles:
            logger.warning("Aucun article chargé. Exécutez load_articles() d'abord.")
            return {}
        
        references = {}
        
        for article_id, article_data in self.articles.items():
            content = article_data.get('content', '')
            
            # Détecter les références avec tous les patterns
            refs = set()
            for pattern in self.reference_patterns:
                for match in pattern.finditer(content):
                    ref = match.group(1)
                    # Vérifier si la référence existe comme article
                    if ref in self.articles:
                        refs.add(ref)
            
            # Filtrer les auto-références (sauf si explicites)
            if article_id in refs and not self._is_explicit_self_reference(content, article_id):
                refs.remove(article_id)
            
            references[article_id] = list(refs)
        
        # Mettre à jour les références dans les articles
        for article_id, refs in references.items():
            self.articles[article_id]['references'] = refs
        
        # Mettre à jour les références inverses
        self._update_inverse_references()
        
        # Sauvegarder les références
        self.references = references
        
        logger.info(f"Détection améliorée: {sum(len(refs) for refs in references.values())} références trouvées")
        return references
    
    def _is_explicit_self_reference(self, content: str, article_id: str) -> bool:
        """
        Vérifie si un article fait explicitement référence à lui-même.
        
        Args:
            content: Contenu de l'article
            article_id: ID de l'article
        
        Returns:
            True si l'article fait explicitement référence à lui-même
        """
        # Patterns pour les auto-références explicites
        patterns = [
            re.compile(r'cette\s+(?:loi|article)', re.IGNORECASE),
            re.compile(r'présente\s+(?:loi|article)', re.IGNORECASE),
            re.compile(f'(?:loi|article)\s+{article_id}\s+elle-même', re.IGNORECASE)
        ]
        
        for pattern in patterns:
            if pattern.search(content):
                return True
        
        return False
    
    def _update_inverse_references(self) -> None:
        """Met à jour les références inverses dans les articles."""
        # Réinitialiser les références inverses
        for article_data in self.articles.values():
            article_data['referenced_by'] = []
        
        # Ajouter les références inverses
        for article_id, article_data in self.articles.items():
            for ref in article_data.get('references', []):
                if ref in self.articles:
                    if 'referenced_by' not in self.articles[ref]:
                        self.articles[ref]['referenced_by'] = []
                    
                    if article_id not in self.articles[ref]['referenced_by']:
                        self.articles[ref]['referenced_by'].append(article_id)
    
    def build_reference_graph(self) -> nx.DiGraph:
        """
        Construit un graphe orienté des références entre articles.
        
        Returns:
            Graphe orienté (DiGraph) des références
        """
        if not self.references:
            logger.warning("Aucune référence détectée. Exécutez detect_references() d'abord.")
            return nx.DiGraph()
        
        # Créer un nouveau graphe
        G = nx.DiGraph()
        
        # Ajouter tous les articles comme nœuds
        for article_id, article_data in self.articles.items():
            G.add_node(article_id, title=article_data.get('title', ''))
        
        # Ajouter les références comme arêtes
        for article_id, refs in self.references.items():
            for ref in refs:
                if ref in self.articles:  # Vérifier que l'article référencé existe
                    G.add_edge(article_id, ref)
        
        self.reference_graph = G
        
        logger.info(f"Graphe de références construit: {G.number_of_nodes()} nœuds, {G.number_of_edges()} arêtes")
        return G
    
    def analyze_references(self) -> Dict[str, Any]:
        """
        Analyse les références entre articles.
        
        Returns:
            Dict avec les résultats de l'analyse
        """
        if not self.reference_graph or self.reference_graph.number_of_nodes() == 0:
            logger.warning("Graphe de références vide. Exécutez build_reference_graph() d'abord.")
            return {}
        
        G = self.reference_graph
        
        # Calculer diverses métriques
        analysis = {
            "article_count": G.number_of_nodes(),
            "reference_count": G.number_of_edges(),
            "most_referenced": [],
            "most_referencing": [],
            "central_articles": [],
            "isolated_articles": [],
            "reference_chains": [],
            "circular_references": []
        }
        
        # Articles les plus référencés
        in_degrees = sorted(G.in_degree(), key=lambda x: x[1], reverse=True)
        analysis["most_referenced"] = in_degrees[:10]
        
        # Articles faisant le plus de références
        out_degrees = sorted(G.out_degree(), key=lambda x: x[1], reverse=True)
        analysis["most_referencing"] = out_degrees[:10]
        
        # Articles centraux (centralité d'intermédiarité)
        try:
            betweenness = nx.betweenness_centrality(G)
            central_articles = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)
            analysis["central_articles"] = central_articles[:10]
        except:
            logger.warning("Impossible de calculer la centralité d'intermédiarité")
        
        # Articles isolés (sans références entrantes ou sortantes)
        isolated = [node for node, degree in G.degree() if degree == 0]
        analysis["isolated_articles"] = isolated
        
        # Détecter les chaînes de références
        try:
            # Trouver les chemins les plus longs
            longest_paths = []
            for source in G.nodes():
                for target in G.nodes():
                    if source != target:
                        try:
                            paths = list(nx.all_simple_paths(G, source, target, cutoff=10))
                            if paths:
                                longest_path = max(paths, key=len)
                                if len(longest_path) > 3:  # Ignorer les chemins courts
                                    longest_paths.append(longest_path)
                        except:
                            pass
            
            # Trier par longueur et prendre les 10 plus longs
            longest_paths.sort(key=len, reverse=True)
            analysis["reference_chains"] = longest_paths[:10]
        except:
            logger.warning("Impossible de calculer les chaînes de références")
        
        # Détecter les références circulaires
        try:
            cycles = list(nx.simple_cycles(G))
            analysis["circular_references"] = cycles
        except:
            logger.warning("Impossible de détecter les références circulaires")
        
        logger.info(f"Analyse des références terminée: {len(analysis['most_referenced'])} articles les plus référencés")
        return analysis
    
    def save_enhanced_references(self) -> Dict[str, str]:
        """
        Sauvegarde les références améliorées.
        
        Returns:
            Dict avec les chemins des fichiers créés
        """
        if not self.references:
            logger.warning("Aucune référence à sauvegarder. Exécutez detect_references() d'abord.")
            return {}
        
        output_files = {}
        
        # 1. Sauvegarder les articles mis à jour
        articles_json = os.path.join(self.output_dir, "enhanced_articles.json")
        with open(articles_json, 'w', encoding='utf-8') as f:
            json.dump(self.articles, f, ensure_ascii=False, indent=2)
        
        output_files['articles_json'] = articles_json
        logger.info(f"Articles mis à jour sauvegardés dans: {articles_json}")
        
        # 2. Sauvegarder les références au format CSV
        references_csv = os.path.join(self.output_dir, "enhanced_references.csv")
        with open(references_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Article_Source', 'Article_Cible'])
            
            for article_id, refs in self.references.items():
                for ref in refs:
                    writer.writerow([article_id, ref])
        
        output_files['references_csv'] = references_csv
        logger.info(f"Références améliorées sauvegardées dans: {references_csv}")
        
        # 3. Sauvegarder l'analyse des références
        if hasattr(self, 'reference_graph') and self.reference_graph.number_of_nodes() > 0:
            analysis = self.analyze_references()
            
            analysis_json = os.path.join(self.output_dir, "reference_analysis.json")
            with open(analysis_json, 'w', encoding='utf-8') as f:
                # Convertir les éléments non sérialisables
                analysis_serializable = {}
                for key, value in analysis.items():
                    if isinstance(value, list):
                        if key in ["most_referenced", "most_referencing"]:
                            analysis_serializable[key] = [(str(node), degree) for node, degree in value]
                        elif key in ["central_articles"]:
                            analysis_serializable[key] = [(str(node), float(centrality)) for node, centrality in value]
                        elif key in ["reference_chains", "circular_references"]:
                            analysis_serializable[key] = [list(map(str, path)) for path in value]
                        else:
                            analysis_serializable[key] = list(map(str, value))
                    else:
                        analysis_serializable[key] = value
                
                json.dump(analysis_serializable, f, ensure_ascii=False, indent=2)
            
            output_files['analysis_json'] = analysis_json
            logger.info(f"Analyse des références sauvegardée dans: {analysis_json}")
        
        # 4. Sauvegarder le graphe de références au format GraphML
        if hasattr(self, 'reference_graph') and self.reference_graph.number_of_nodes() > 0:
            try:
                graph_file = os.path.join(self.output_dir, "reference_graph.graphml")
                nx.write_graphml(self.reference_graph, graph_file)
                
                output_files['graph_file'] = graph_file
                logger.info(f"Graphe de références sauvegardé dans: {graph_file}")
            except Exception as e:
                logger.error(f"Erreur lors de la sauvegarde du graphe: {e}")
        
        return output_files
    
    def generate_navigation_data(self) -> Dict[str, Any]:
        """
        Génère des données de navigation pour l'interface web.
        
        Returns:
            Dict avec les données de navigation
        """
        if not self.articles or not self.references:
            logger.warning("Articles ou références manquants. Exécutez load_articles() et detect_references() d'abord.")
            return {}
        
        # Créer la structure de navigation
        navigation = {
            "articles": {},
            "categories": {},
            "reference_network": {
                "nodes": [],
                "links": []
            }
        }
        
        # Ajouter les articles à la navigation
        for article_id, article_data in self.articles.items():
            # Version simplifiée pour la navigation
            navigation["articles"][article_id] = {
                "id": article_id,
                "title": article_data.get('title', ''),
                "references": article_data.get('references', []),
                "referenced_by": article_data.get('referenced_by', [])
            }
        
        # Créer les catégories (groupes d'articles)
        categories = defaultdict(list)
        for article_id, article_data in self.articles.items():
            # Extraire la catégorie à partir du titre
            title = article_data.get('title', '')
            category_match = re.search(r'LOI\s+\d+\s+-\s+(.*?)(?:\.{2,}|\s{2,}|$)', title, re.IGNORECASE)
            
            if category_match:
                category = category_match.group(1).strip()
                categories[category].append(article_id)
            else:
                categories["Autres"].append(article_id)
        
        # Ajouter les catégories à la navigation
        for category, article_ids in categories.items():
            navigation["categories"][category] = article_ids
        
        # Créer les données pour le réseau de références (visualisation D3.js)
        if hasattr(self, 'reference_graph') and self.reference_graph.number_of_nodes() > 0:
            G = self.reference_graph
            
            # Ajouter les nœuds
            for node in G.nodes():
                navigation["reference_network"]["nodes"].append({
                    "id": node,
                    "title": self.articles[node].get('title', '') if node in self.articles else node,
                    "in_degree": G.in_degree(node),
                    "out_degree": G.out_degree(node)
                })
            
            # Ajouter les liens
            for source, target in G.edges():
                navigation["reference_network"]["links"].append({
                    "source": source,
                    "target": target
                })
        
        # Sauvegarder les données de navigation
        nav_file = os.path.join(self.output_dir, "navigation_data.json")
        with open(nav_file, 'w', encoding='utf-8') as f:
            json.dump(navigation, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Données de navigation générées: {len(navigation['articles'])} articles, {len(navigation['categories'])} catégories")
        return navigation
    
    def run_full_process(self) -> Dict[str, Any]:
        """
        Exécute le processus complet de détection et d'analyse des références.
        
        Returns:
            Dict avec les résultats du processus
        """
        logger.info("Démarrage du processus complet de détection des références...")
        
        # 1. Charger les articles
        self.load_articles()
        
        # 2. Détecter les références améliorées
        self.detect_references()
        
        # 3. Construire le graphe de références
        self.build_reference_graph()
        
        # 4. Analyser les références
        analysis = self.analyze_references()
        
        # 5. Sauvegarder les références améliorées
        output_files = self.save_enhanced_references()
        
        # 6. Générer les données de navigation
        navigation = self.generate_navigation_data()
        
        results = {
            "articles": len(self.articles),
            "references": sum(len(refs) for refs in self.references.values()),
            "output_files": output_files,
            "analysis": {
                "most_referenced": len(analysis.get('most_referenced', [])),
                "circular_references": len(analysis.get('circular_references', [])),
                "isolated_articles": len(analysis.get('isolated_articles', []))
            },
            "navigation": {
                "categories": len(navigation.get('categories', {})),
                "network_nodes": len(navigation.get('reference_network', {}).get('nodes', [])),
                "network_links": len(navigation.get('reference_network', {}).get('links', []))
            }
        }
        
        logger.info(f"Processus complet terminé: {results['references']} références détectées")
        return results


def install_dependencies():
    """Installe les dépendances nécessaires."""
    import subprocess
    import sys
    
    packages = ['networkx']
    
    print("Installation des dépendances...")
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package} installé")
        except subprocess.CalledProcessError:
            print(f"❌ Erreur installation {package}")


if __name__ == "__main__":
    import sys
    
    # Vérifier les arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--install":
        install_dependencies()
        sys.exit(0)
    
    # Répertoires par défaut
    input_dir = "./output"
    output_dir = "./output/references"
    
    # Permettre de spécifier les répertoires en ligne de commande
    if len(sys.argv) > 2:
        input_dir = sys.argv[1]
        output_dir = sys.argv[2]
    
    # Installer les dépendances si nécessaire
    try:
        import networkx as nx
    except ImportError:
        print("Installation de networkx...")
        install_dependencies()
    
    # Créer le détecteur de références
    detector = ReferenceDetector(input_dir, output_dir)
    
    # Exécuter le processus complet
    try:
        results = detector.run_full_process()
        
        print("\n✅ Détection des références terminée avec succès!")
        print(f"📊 Articles analysés: {results['articles']}")
        print(f"🔗 Références détectées: {results['references']}")
        
        print("\n📈 Analyse des références:")
        print(f"  - Articles les plus référencés: {results['analysis']['most_referenced']}")
        print(f"  - Références circulaires: {results['analysis']['circular_references']}")
        print(f"  - Articles isolés: {results['analysis']['isolated_articles']}")
        
        print("\n📁 Fichiers générés:")
        for file_type, file_path in results['output_files'].items():
            print(f"  - {file_type}: {os.path.basename(file_path)}")
        
        print(f"\n📂 Répertoire de sortie: {output_dir}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        logger.error(f"Erreur lors du processus: {e}", exc_info=True)

