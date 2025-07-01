# Architecture du Site BridgeFacile V2

## 🏗️ Structure Générale

Le site BridgeFacile V2 sera structuré en deux sections principales :

1. **Section Cours** - Pour l'apprentissage du bridge
2. **Section Arbitrage** - Pour la consultation du Code 2017

### 📱 Responsive Design

L'ensemble du site sera conçu avec une approche "mobile-first" pour garantir une expérience utilisateur optimale sur tous les appareils :
- Smartphones
- Tablettes
- Ordinateurs de bureau

## 🔍 Architecture Technique

### Frontend

- **Framework** : React.js
- **Styling** : Tailwind CSS
- **Routing** : React Router
- **State Management** : React Context API + Hooks
- **Animations** : Framer Motion
- **Visualisations** : D3.js (pour les graphes de références)

### Backend

- **Base de données** : PostgreSQL (via Supabase)
- **Authentification** : Supabase Auth
- **Stockage** : Supabase Storage
- **API** : Supabase Functions + REST API

### Outils de Traitement

- **Parser PDF** : Python avec pdfplumber
- **Analyse de références** : Python avec networkx
- **Génération CSV** : Python avec pandas

## 📂 Structure des Dossiers

```
/
├── public/                  # Assets statiques
│   ├── images/              # Images et icônes
│   ├── fonts/               # Polices personnalisées
│   └── favicon.ico          # Favicon
│
├── src/                     # Code source React
│   ├── components/          # Composants réutilisables
│   │   ├── common/          # Composants communs (Header, Footer, etc.)
│   │   ├── courses/         # Composants pour la section Cours
│   │   └── arbitration/     # Composants pour la section Arbitrage
│   │
│   ├── pages/               # Pages principales
│   │   ├── Home.jsx         # Page d'accueil
│   │   ├── Courses/         # Pages des cours
│   │   ├── Arbitration/     # Pages d'arbitrage
│   │   ├── Auth/            # Pages d'authentification
│   │   └── Profile/         # Pages de profil utilisateur
│   │
│   ├── hooks/               # Custom hooks React
│   ├── context/             # Contextes React
│   ├── services/            # Services (API, auth, etc.)
│   ├── utils/               # Fonctions utilitaires
│   ├── styles/              # Styles globaux
│   ├── App.jsx              # Composant racine
│   └── index.jsx            # Point d'entrée
│
├── python_tools/            # Outils Python
│   ├── bridge_law_parser.py # Parser principal
│   ├── reference_detector.py # Détecteur de références
│   └── import_data.py       # Script d'importation en base
│
├── database/                # Scripts de base de données
│   ├── schema.sql           # Schéma principal
│   ├── auth_schema.sql      # Schéma d'authentification
│   └── courses_schema.sql   # Schéma des cours
│
├── docs/                    # Documentation
├── .env.example             # Variables d'environnement d'exemple
├── package.json             # Dépendances npm
└── README.md                # Documentation principale
```

## 🔐 Système d'Authentification

### Rôles Utilisateurs

- **Invité** : Accès limité au contenu public
- **Étudiant** : Accès aux cours auxquels il est inscrit
- **Arbitre** : Accès à la documentation d'arbitrage
- **Enseignant** : Accès aux cours et à l'arbitrage
- **Administrateur** : Accès complet à toutes les fonctionnalités

### Flux d'Authentification

1. Inscription / Connexion via Supabase Auth
2. Attribution d'un rôle par défaut (Étudiant)
3. Possibilité de demander des accès supplémentaires
4. Validation des demandes par un administrateur

## 📚 Section Cours

### Fonctionnalités

- **Catalogue de cours** : Liste des cours disponibles par niveau
- **Détail des cours** : Description, programme, prix
- **Inscription aux cours** : Individuel ou en groupe
- **Paiement en ligne** : Intégration avec Stripe
- **Suivi de progression** : Tableau de bord étudiant
- **Matériels pédagogiques** : PDF, exercices, quiz

### Pages Principales

1. **Liste des cours** : Filtrable par niveau, prix, disponibilité
2. **Détail d'un cours** : Informations complètes et inscription
3. **Tableau de bord étudiant** : Suivi des cours et progression
4. **Matériels pédagogiques** : Ressources téléchargeables

## 📜 Section Arbitrage

### Fonctionnalités

- **Consultation du Code 2017** : Navigation intuitive entre articles
- **Recherche avancée** : Par mot-clé, numéro d'article, contenu
- **Visualisation des références** : Graphe interactif des relations entre articles
- **Annotations personnelles** : Possibilité d'ajouter des notes
- **Export PDF/CSV** : Génération de documents personnalisés

### Pages Principales

1. **Accueil Arbitrage** : Présentation et accès rapide
2. **Navigateur d'articles** : Interface principale de consultation
3. **Recherche avancée** : Formulaire de recherche multicritères
4. **Visualisation** : Graphe interactif des références
5. **Article individuel** : Vue détaillée avec références et annotations

## 🔄 Intégrations

- **Calendrier** : Intégration avec Google Calendar pour la planification des cours
- **Paiement** : Intégration avec Stripe pour les paiements en ligne
- **Email** : Notifications automatiques via SendGrid
- **Analytics** : Suivi des performances avec Google Analytics

## 🚀 Déploiement

- **Hébergement** : Vercel ou Netlify pour le frontend
- **Base de données** : Supabase (PostgreSQL)
- **CI/CD** : GitHub Actions pour le déploiement automatique
- **Domaine** : Configuration avec lekibbitz.fr

## 📈 Évolutions Futures

- **Application mobile** : Version native pour iOS et Android
- **Chatbot** : Assistant virtuel pour l'aide à l'arbitrage
- **Système de tournois** : Organisation et gestion de tournois en ligne
- **Communauté** : Forum d'entraide entre joueurs

