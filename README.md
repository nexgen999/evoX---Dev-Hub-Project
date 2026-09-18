# **Evox Dev Hub Project**

**Evox Dev Hub Project** est un hub/portfolio Single Page Application (SPA) ultra-modulaire, moderne et dynamique. Conçu avec une architecture propre, il permet à tout développeur ou créateur de générer sa propre vitrine de projets responsive avec mode Sombre / Dark Theme.

L'ensemble du contenu (profil, catégories, projets, réseaux sociaux) est entièrement piloté par des fichiers de configuration **JSON** localisés dans `/web/config/` et modifiables via une interface graphique Python GUI (Tkinter) intuitive.

# **✨ Fonctionnalités Principales**

| Fonctionnalité | Description |
| :---- | :---- |
| **Interface Dark-Mode** | UI épurée construite en HTML5, CSS moderne avec conteneurs sécurisés et typographie claire. |
| **Intégration API GitHub** | Récupération en temps réel des métriques utilisateur (dépôts publics, followers) et des favoris sans restriction. |
| **Recherche & Filtrage** | Filtrage instantané par mots-clés, catégories ou tags, combiné à un sélecteur de tri intelligent. |
| **Commutateur de Vue** | Basculez instantanément entre la **Vue Grille** et la **Vue Liste**. |
| **Aperçu Markdown** | Affichage interactif des README.md via conversion automatique des liens et images vers les serveurs Raw. |
| **Studio de Gestion** | Application desktop Python pour effectuer les opérations CRUD sur les fichiers JSON. |

# **📁 Arborescence du Projet**

t  
Evox-Dev-Hub-Project/  
├── assets/  
│   └── banner.png             \# Bannière d'en-tête du README  
├── index.html                 \# Point d'entrée principal de l'application Web  
└── web/  
├── css/  
│   └── style.css          \# Feuille de style principale (variables, responsive)  
├── js/  
│   └── app.js             \# Logique applicative, routeur et appels API GitHub  
└── config/  
├── profile.json       \# Métadonnées du profil utilisateur  
├── categories.json    \# Liste des catégories et icônes  
├── projects.json      \# Projets mis en avant  
├── socials.json       \# Liens de réseaux sociaux  
└── script\_gui\_python.py \# Studio GUI Python Tkinter pour gérer les JSONs

\#\# ⚙️ Explications des Fichiers de Configuration JSON

Tous les fichiers de données se situent dans le dossier \`/web/config/\`.

\#\#\# 1\. \`profile.json\`

Définit les informations personnelles affichées sur l'en-tête.

\`\`\`json

{

  "username": "nexgen999",

  "handle": "nexgen999",

  "avatar": "",

  "bio": "I love Releases & PS5 Homebrew Development",

  "stats": {

    "repos": 128,

    "followers": 69

  }

}

## **2\. `categories.json`**

Définit la liste des filtres et les catégories pour classer vos travaux.\[

  {

    "id": "all",

    "name": "Tous",

    "icon": "fa-solid fa-border-all"

  },

  {

    "id": "ps5",

    "name": "PS5 / PlayStation",

    "icon": "fa-brands fa-playstation"

  },

  {

    "id": "web",

    "name": "Web / Store",

    "icon": "fa-solid fa-globe"

  }

\]

## **3\. `projects.json`**

Contient la liste de vos projets locaux personnalisés.\[

  {

    "id": "evox-coreos",

    "title": "evoX-CoreOS",

    "category": "ps5",

    "description": "Écosystème automatisé et intelligent pour PlayStation 5.",

    "images": \[\],

    "github": "",

    "demo": "",

    "tags": \["PS5", "Payloads", "Store"\]

  }

\]

## **4\. `socials.json`**

Gère les icônes et liens de réseaux sociaux affichés sur le profil.\[

  {

    "name": "GitHub",

    "url": "",

    "icon": "fa-brands fa-github"

  },

  {

    "name": "Discord",

    "url": "",

    "icon": "fa-brands fa-discord"

  }

\]

# **🚀 Démarrage Rapide**

## **Lancer le Hub Web en local**

Vous pouvez héberger le projet avec n'importe quel serveur web statique ou via Python :h

# **Avec Python 3**

python \-m http.server 8000Rendez-vous ensuite sur \`http://localhost:8000\`.

\#\#\# Lancer l'Éditeur Python GUI

Pour modifier vos projets et configurations sans toucher au code, utilisez le studio intégré :

\`\`\`bash

cd web/config

python script\_gui\_python.py

# **📄 Licence**

Ce projet est sous licence **MIT**. Vous êtes libre de le forker, de le modifier et de l'adapter pour votre propre portfolio.

---

*Dernière mise à jour :* Date