#!/usr/bin/env python3
"""
BridgeFacile - Script d'installation et de test
==============================================

Ce script installe les dépendances nécessaires et teste le parser
sur un exemple de fichier PDF du Code 2017.

Auteur: BridgeFacile Team
Date: 2025-01-07
"""

import os
import sys
import subprocess
import shutil
from datetime import datetime

def print_header(text):
    """Affiche un texte formaté comme en-tête."""
    print("\n" + "=" * 60)
    print(f" {text} ".center(60, "="))
    print("=" * 60)

def install_dependencies():
    """Installe les dépendances Python nécessaires."""
    print_header("INSTALLATION DES DÉPENDANCES")
    
    packages = ['pdfplumber', 'PyPDF2']
    
    for package in packages:
        try:
            print(f"Installation de {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package} installé avec succès")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur lors de l'installation de {package}: {e}")
            return False
    
    return True

def setup_directories():
    """Configure les répertoires nécessaires."""
    print_header("CONFIGURATION DES RÉPERTOIRES")
    
    # Répertoires par défaut
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(script_dir, "input")
    output_dir = os.path.join(script_dir, "output")
    
    # Créer les répertoires s'ils n'existent pas
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"✅ Répertoire d'entrée: {input_dir}")
    print(f"✅ Répertoire de sortie: {output_dir}")
    
    return input_dir, output_dir

def check_sample_pdf(input_dir):
    """Vérifie si un exemple de PDF est disponible."""
    print_header("VÉRIFICATION DES FICHIERS PDF")
    
    # Vérifier s'il y a des PDFs dans le répertoire d'entrée
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    
    if pdf_files:
        print(f"✅ {len(pdf_files)} fichier(s) PDF trouvé(s) dans {input_dir}:")
        for pdf in pdf_files:
            print(f"  - {pdf}")
        return True
    else:
        print(f"❌ Aucun fichier PDF trouvé dans {input_dir}")
        print("Veuillez copier les fichiers PDF du Code 2017 dans ce répertoire.")
        return False

def run_parser_test(input_dir, output_dir):
    """Exécute un test du parser."""
    print_header("TEST DU PARSER")
    
    try:
        # Importer le module du parser
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from bridge_law_parser import BridgeLawParser
        
        # Créer le parser
        parser = BridgeLawParser(input_dir, output_dir)
        
        # Exécuter le traitement
        print("Démarrage du traitement...")
        results = parser.run_full_process()
        
        print("\n✅ Test réussi!")
        print(f"📊 Articles extraits: {results['articles']}")
        print(f"🔗 Références détectées: {results['references']}")
        print("\n📁 Fichiers générés:")
        
        for csv_type, csv_path in results['csv_files'].items():
            print(f"  - {csv_type}: {os.path.basename(csv_path)}")
        
        print(f"\n📂 Répertoire de sortie: {output_dir}")
        
        return True
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def main():
    """Fonction principale."""
    print_header("BRIDGEFACILE - INSTALLATION ET TEST")
    print("Ce script va installer les dépendances nécessaires et tester le parser")
    print("sur les fichiers PDF du Code 2017.")
    
    # Installer les dépendances
    if not install_dependencies():
        print("❌ Échec de l'installation des dépendances. Arrêt du script.")
        return
    
    # Configurer les répertoires
    input_dir, output_dir = setup_directories()
    
    # Vérifier les fichiers PDF
    if not check_sample_pdf(input_dir):
        print("\n⚠️  Aucun fichier PDF trouvé. Veuillez copier les fichiers PDF du Code 2017")
        print(f"dans le répertoire: {input_dir}")
        print("\nVous pouvez ensuite relancer ce script pour effectuer le test.")
        return
    
    # Exécuter le test
    if run_parser_test(input_dir, output_dir):
        print("\n🎉 Installation et test réussis!")
        print(f"Les fichiers CSV ont été générés dans: {output_dir}")
        print("\nVous pouvez maintenant utiliser le parser pour traiter vos propres fichiers PDF.")
    else:
        print("\n❌ Le test a échoué. Veuillez vérifier les erreurs ci-dessus.")

if __name__ == "__main__":
    main()

