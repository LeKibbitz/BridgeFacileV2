# BridgeFacile V2

## 🃏 Plateforme Complète pour l'Apprentissage et l'Arbitrage du Bridge

BridgeFacile V2 est une refonte complète de la plateforme BridgeFacile, intégrant à la fois des fonctionnalités d'apprentissage du bridge et un système complet de consultation du Code 2017 pour l'arbitrage.

### 📚 Fonctionnalités Principales

#### 🎓 Section Cours
- Cours structurés par niveau (débutant à avancé)
- Système de réservation pour cours individuels et en groupe
- Matériels pédagogiques téléchargeables
- Suivi de progression des élèves

#### 📜 Section Arbitrage
- Consultation interactive du Code 2017
- Navigation entre articles avec références croisées
- Système de recherche avancé
- Visualisation des relations entre articles

### 🛠️ Technologies Utilisées

- **Frontend**: React.js, Tailwind CSS
- **Backend**: Supabase (PostgreSQL, Auth, Storage)
- **Traitement PDF**: Python avec pdfplumber
- **Visualisation**: D3.js pour les graphes de références

### 🚀 Installation et Déploiement

```bash
# Cloner le repository
git clone https://github.com/LeKibbitz/BridgeFacileV2.git
cd BridgeFacileV2

# Installer les dépendances
npm install

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos identifiants Supabase

# Lancer en développement
npm run dev

# Construire pour production
npm run build
```

### 📂 Structure du Projet

- `/src` - Code source React
- `/public` - Assets statiques
- `/python_tools` - Outils Python pour le traitement des PDFs
- `/database` - Schémas SQL et scripts de migration

### 🔄 Traitement des PDFs du Code 2017

Le système inclut un parser Python spécialisé qui:
1. Extrait le texte des PDFs du Code 2017
2. Détecte automatiquement les articles de loi
3. Identifie les références croisées entre articles
4. Génère des fichiers CSV et JSON structurés
5. Alimente la base de données Supabase

### 👥 Gestion des Utilisateurs

- **Étudiants**: Accès aux cours uniquement
- **Arbitres**: Accès à la documentation d'arbitrage
- **Enseignants**: Accès complet aux cours et à l'arbitrage
- **Administrateurs**: Gestion complète du site

### 📊 Visualisation des Données

- Graphes interactifs des références entre articles
- Statistiques sur les articles les plus référencés
- Analyse des chaînes de références

### 📱 Responsive Design

Interface adaptative pour:
- Ordinateurs de bureau
- Tablettes
- Smartphones

### 🔒 Sécurité

- Authentification sécurisée via Supabase Auth
- Contrôle d'accès basé sur les rôles
- Protection des données sensibles

### 📄 Licence

© 2025 BridgeFacile - Tous droits réservés

