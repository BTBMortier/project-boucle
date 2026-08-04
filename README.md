# Project Boucle

## Overview

**Project Boucle** est un projet informatique dédié à l'exécution, l'automatisation et la gestion de traitements itératifs (boucles d'exécution, pipelines de données ou tâches récurrentes). Ce dépôt regroupe le code source principal, les configurations d'environnement, ainsi que les suites de tests automatisés.

---

## Architecture et Fonctionnalités

* **Moteur d'exécution itératif :** Orchestration et exécution séquentielle ou parallèle de traitements.
* **Gestion des états et du contexte :** Suivi dynamique de l'avancement, persistance intermédiaire et réinitialisation de boucle.
* **Journalisation et Robustesse :** Capture structurée des logs, gestion centralisée des erreurs et stratégies de réessai (retry policies).
* **Modularité :** Structure en composants indépendants permettant l'ajout ou la modification de traitements sans altérer le cœur du système.

---

## Structure du Projet

```text
project-boucle/
├── config/             # Fichiers de configuration (environnement, constantes)
├── src/                # Code source principal
│   ├── core/           # Moteur d'exécution et logique de la boucle
│   ├── modules/        # Traitements métiers et services tiers
│   └── utils/          # Logger, helpers et utilitaires
├── tests/              # Tests unitaires, d'intégration et de performance
├── .env.example        # Modèle de variables d'environnement
├── .gitignore          # Exclusions Git
├── Dockerfile          # Configuration de conteneurisation
└── README.md           # Documentation principale

```

---

## Prérequis

* **Runtime :** Node.js (`>= 18.x`) ou Python (`>= 3.10`) selon le langage du projet.
* **Gestionnaire de dépendances :** `npm` / `yarn` / `pnpm` ou `pip` / `poetry`.
* **Conteneurisation (optionnel) :** Docker (`>= 20.10`) et Docker Compose.

---

## Installation

1. **Cloner le dépôt :**
```bash
git clone https://github.com/BTBMortier/project-boucle.git
cd project-boucle

```


2. **Installer les dépendances :**
* *Environnement Node.js :*
```bash
npm install

```


* *Environnement Python :*
```bash
pip install -r requirements.txt

```





---

## Configuration

1. Dupliquer le fichier modèle d'environnement :
```bash
cp .env.example .env

```


2. Renseigner les paramètres applicatifs dans le fichier `.env` :
```env
NODE_ENV=development
PORT=3000
LOG_LEVEL=info
MAX_RETRIES=3
TIMEOUT_MS=5000

```



---

## Utilisation

### Mode Développement

```bash
npm run dev
# ou
python src/main.py

```

### Mode Production

```bash
npm start

```

### Exécution via Docker

```bash
docker build -t project-boucle .
docker run -p 3000:3000 --env-file .env project-boucle

```

---

## Tests

Exécuter la suite de tests automatisés pour valider le comportement du code :

```bash
# Lancement de l'ensemble des tests
npm test

# Rapport de couverture du code
npm run test:coverage

```

---

## Processus de Contribution

1. Créer une branche dédiée :
```bash
git checkout -b feature/nom-fonctionnalite

```


2. Valider le respect du linter et la réussite des tests unitaires.
3. Formater les commits selon la convention *Conventional Commits* :
```bash
git commit -m "feat: ajout du module d'itération parallèle"

```


4. Pousser la branche et soumettre une Pull Request vers la branche principale `main`.

---

## Licence

Ce projet est distribué sous licence MIT. Se référer au fichier `LICENSE` pour plus de précisions.
