# 🔁 Project Boucle

[![Data Pipeline](https://img.shields.io/badge/Architecture-ETL-blue.svg)](#)
[![Docker](https://img.shields.io/badge/Container-Docker-2496ED.svg)](#)
[![Apache Airflow](https://img.shields.io/badge/Orchestration-Airflow-017CEE.svg)](#)
[![Python](https://img.shields.io/badge/Engine-PySpark-3776AB.svg)](#)

## 📌 Présentation

**Project Boucle** est un pipeline ETL (Extract, Transform, Load) automatisé et résilient, conçu pour l'ingestion massive de flux textuels non structurés issus du web. 

Le système orchestre l'extraction automatisée des contenus, leur nettoyage/normalisation distribuée via Spark, et leur stockage hybride (Relationnel & Document) pour des besoins d'analyse à grande échelle.

L'ensemble de l'architecture est conteneurisé et orchestré via **Apache Airflow**, tout en restant exécutable en mode CLI autonome.

---

## 📐 Architecture & Infrastructure

Le pipeline suit un modèle séquentiel strict piloté par DAG, garantissant l'intégrité des données à chaque étape de transformation :

```mermaid
graph TD
    %% Source
    WEB[🌐 Forums Web / Sources Unstructured]

    %% Ingestion
    subgraph Ingestion ["1. Ingestion (Scrapy)"]
        SP_T[Spider: topics]
        SP_P[Spider: posts]
    end

    %% Storage Temp
    RAW[📄 Raw JL Buffer]

    %% Processing
    subgraph Processing ["2. Transformation (PySpark)"]
        TL_T[tl_topics.py / Cleaning & Normalization]
        TL_P[tl_posts.py / Content Parsing & Structuring]
    end

    %% Persistence
    subgraph Persistence ["3. Persistance Hybride"]
        PG[(🐘 PostgreSQL / Data Structurée)]
        MG[(🍃 MongoDB / Archiving Document)]
    end

    %% Flow Relations
    WEB -->|Scrape| SP_T & SP_P
    SP_T & SP_P -->|Dump Brut| RAW
    RAW -->|Stream/Batch Ingest| TL_T & TL_P
    TL_T & TL_P -->|Persist SQL| PG
    TL_T & TL_P -->|Archive NoSQL| MG

    %% Orchestration Overlay
    subgraph Control [" Orchestration (Apache Airflow) "]
        DAG[DAG: forum_etl]
    end

    DAG -.->|Trigger & Monitor| Ingestion
    DAG -.->|Trigger & Monitor| Processing

```

---

## 🛠️ Stack Technique

* **Scraping & Parsing :** Scrapy (Spiders asynchrones multi-threads)
* **Processing & ETL :** Python, Apache Spark / PySpark
* **Bases de Données :** PostgreSQL (Données relationnelles), MongoDB (Archivage JSON)
* **Orchestration :** Apache Airflow (DAGs orientés événements/planning)
* **Environnement :** Docker, Bash

```

---

### 💡 Pourquoi cette intro tape plus fort :
1. **Terminologie Pro :** Utilisation de termes comme *flux textuels non structurés*, *modèle séquentiel strict*, *persistance hybride*, *ingestion massive*.
2. **Badges d'en-tête :** Les petits shields en haut donnent tout de suite un aspect projet Open-Source maintenu.
3. **Schéma Mermaid épuré :** Il sépare visuellement l'Ingestion, le Traitement (PySpark), la Persistance et le Contrôle (Airflow) pour qu'un recruteur ou un Lead Tech comprenne l'architecture complète en **3 secondes d'œil**.

```

---

## Arborescence du Projet

```text
.
├── Dockerfile
├── requirements.txt
├── README.md
└── pipeline/
    ├── scrapy.cfg
    ├── boucled_scrapers/             # Projets et spiders Scrapy
    │   ├── items.py
    │   ├── middlewares.py
    │   ├── pipelines.py
    │   ├── settings.py
    │   └── spiders/
    │       ├── topics.py             # Spider d'extraction des sujets
    │       ├── posts.py              # Spider d'extraction des posts
    │       ├── long_posts.py
    │       ├── long_topics.jl
    │       └── launch_spiders.sh
    ├── boucled_etl/                  # Scripts de transformation et chargement
    │   ├── tl_topics.py              # Traitement des sujets
    │   ├── tl_posts.py               # Traitement des messages
    │   ├── tl_topics.ipynb
    │   ├── tl_posts.ipynb
    │   └── convert_nbs.sh            # Conversion des notebooks en scripts Python
    ├── boucled_db/                   # Interactions avec les bases de données
    │   ├── postgres.py               # Gestion du stockage PostgreSQL
    │   ├── mongodb.py                # Gestion du stockage MongoDB
    │   └── change_psql_password.sh
    └── dags/                         # Orchestration Airflow
        └── forum_etl.py              # DAG de planification du pipeline

```

---

## Flux d'Exécution (DAG Airflow)

Le DAG `forum_etl` planifie l'exécution séquentielle des étapes suivantes :

1. **`scrape_topics` :** Lancement du spider Scrapy `topics` pour exporter les données brutes dans `topics.jl`.
2. **`scrape_posts` :** Exécution du spider `posts` à la suite de la récupération des sujets.
3. **`transload_posts` :** Nettoyage, transformation et chargement des messages via `tl_posts.py`.
4. **`transload_topics` :** Transformation et persistance finale des sujets via `tl_topics.py`.

---

## Installation et Déploiement

### Option 1 : Déploiement Conteneurisé (Docker)

1. Construire l'image Docker :
```bash
docker build -t project-boucle .

```


2. Exécuter le conteneur :
```bash
docker run -d --name project-boucle-container project-boucle

```



### Option 2 : Exécution Locale / Autonome

1. Cloner le dépôt :
```bash
git clone https://github.com/BTBMortier/project-boucle.git
cd project-boucle

```


2. Installer les dépendances Python :
```bash
pip install -r requirements.txt

```


3. Exécuter manuellement les composants du pipeline :
```bash
# 1. Extraction
cd pipeline/boucled_scrapers/spiders
scrapy crawl topics -O topics.jl
scrapy crawl posts

# 2. Transformation et chargement
python3 ../../boucled_etl/tl_posts.py
python3 ../../boucled_etl/tl_topics.py

```



---

## Conversion des Notebooks

Les fichiers de prototypage `.ipynb` situés dans `pipeline/boucled_etl/` peuvent être convertis en scripts Python exécutables via le script utilitaire fourni :

```bash
bash pipeline/boucled_etl/convert_nbs.sh

```
