# 📱 Projet Data Science - Web Scraping Smartphones Tunisie

## 🎯 Objectif

Ce projet a pour objectif de collecter, nettoyer et analyser les données des smartphones disponibles sur les principaux sites e-commerce tunisiens (**Tunisianet** et **Mytek**). Les données extraites permettent de créer un dataset complet pour l'analyse des prix, caractéristiques techniques et tendances du marché des smartphones en Tunisie.

## 📋 Description

Le projet comprend :
- **Web Scraping** : Extraction automatisée des données produits depuis Tunisianet et Mytek
- **Nettoyage des données** : Parsing et normalisation des spécifications techniques
- **Enrichissement** : Complétion des données manquantes via des sources externes (GSMArena)
- **Export CSV** : Génération de datasets prêts pour l'analyse

### Données collectées
- Nom du modèle et marque
- Prix en Dinar Tunisien (DT)
- Spécifications : RAM, Stockage, Batterie, Écran, Caméras
- Réseau (3G/4G/5G), Système d'exploitation, Processeur
- Couleur, Garantie, Disponibilité en stock

## 📁 Structure du Projet

```
├── code/                    # Scripts Python
│   ├── scrape_tunisianet_smartphones.py
│   ├── scrape_mytek_smartphones.py
│   └── fill_missing_specs.py
├── dataset/                 # Fichiers CSV
│   ├── tunisianet_smartphones.csv
│   ├── tunisianet_smartphones_filled.csv
│   ├── tunisianet_smartphones_completed.csv
│   ├── mytek_smartphones.csv
│   ├── mytek_smartphones_filled.csv
│   └── mytek_smartphones_complete.csv
├── requirements.txt         # Dépendances Python
└── README.md
```

## 🛠️ Installation

```bash
pip install -r requirements.txt
```

## 🚀 Utilisation

### Scraper Tunisianet

```bash
# Scraper toutes les pages (~369 produits)
python code/scrape_tunisianet_smartphones.py

# Scraper les N premières pages (ex: 2 pages pour test)
python code/scrape_tunisianet_smartphones.py 2
```

### Scraper Mytek

```bash
python code/scrape_mytek_smartphones.py
```

### Compléter les données manquantes

```bash
python code/fill_missing_specs.py dataset/tunisianet_smartphones.csv
```

## 📊 Colonnes du Dataset

| Colonne           | Description                    |
|-------------------|--------------------------------|
| model             | Nom du produit                 |
| brand             | Fabricant (Samsung, Apple…)    |
| reference         | Référence produit              |
| price_dt          | Prix en Dinar Tunisien         |
| ram_gb            | RAM (Go)                       |
| storage_gb        | Stockage interne (Go)          |
| battery_mah       | Capacité batterie (mAh)        |
| screen_inches     | Taille écran (pouces)          |
| camera_rear_mp    | Caméra arrière (MP)            |
| camera_front_mp   | Caméra frontale (MP)           |
| network           | 3G / 4G / 5G                   |
| os                | Android / iOS                  |
| processor_type    | Type de processeur             |
| color             | Couleur                        |
| warranty          | Garantie (ex: 1 an)            |
| in_stock          | Disponibilité en stock         |
| description       | Description courte             |
| url               | Lien vers la page produit      |

## 🔧 Technologies Utilisées

- **Python 3.x**
- **BeautifulSoup4** - Parsing HTML
- **Selenium** - Scraping de pages dynamiques (Mytek)
- **Requests** - Requêtes HTTP
- **Pandas** - Manipulation de données

## 👥 Auteur

- **iheblam**

## 📄 Licence

Ce projet est développé dans le cadre d'un projet académique.
