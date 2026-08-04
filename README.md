# Project Boucle

## Présentation

**Project Boucle** est une pipeline ETL (Extract, Transform, Load) automatisé conçu pour l'extraction de données issues de forums web, leur transformation et leur persistance dans des bases de données relationnelles et NoSQL.

Le projet est conteneurisé via Docker et orchestrait par Apache Airflow, tout en conservant la possibilité d'être exécuté de manière autonome.

---

## Architecture et Stack Technique

* **Extraction (Scraping) :** Scrapy (Spiders pour sujets `topics` et messages `posts`).
* **Transformation & Chargement (ETL) :** Python / Spark (`tl_posts.py`, `tl_topics.py`).
* **Stockage & Persistance :**
    * **PostgreSQL :** Connecteur et requêtes via `postgres.py`.
    * **MongoDB :** Connecteur et requêtes via `mongodb.py`.


* **Orchestration :** Apache Airflow (`forum_etl.py`).
* **Conteneurisation :** Docker (`Dockerfile`).

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
