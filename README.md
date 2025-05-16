# ChainTracker - Plateforme de visualisation de cyptomonnaies

## Motivations

ChainTracker est un projet personnel que j'ai développé durant mon temps libre afin de m'exercer au langage Python. Pour moi, maîtriser Python est essentiel, et je souhaitais réaliser un projet concret qui me motive vraiment.

En effet, lors de mes études, les projets proposés étaient souvent réalisés dans des langages qui ne m'intéressaient pas (Java, PHP, C) et abordaient des thématiques peu inspirantes. Passionné par la finance et l’univers des cryptomonnaies, j'ai décidé de créer une application web capable de suivre mes coins préférés à travers les transactions, un suivi global, ainsi qu’un suivi de portefeuille.

Ce projet combine ainsi l’envie d’apprendre en pratique et de proposer un outil utile, même s’il reste à taille modeste. ChainTracker est à la fois un terrain d’entraînement et un véritable petit projet personnel.

## Fonctionnalités & Utilisation

### Accès libre (sans compte)
Lorsqu’un utilisateur arrive sur ChainTracker, il peut naviguer librement sans avoir besoin de se connecter. Il a accès à plusieurs informations clés sur les principales cryptomonnaies comme Ethereum, Binance Smart Chain (BNB), Bitcoin, Solana et Polygon, notamment :

Le prix actuel

La capitalisation boursière (market cap)

Le temps moyen de transaction (TPS)

Le gas price (frais de transaction)

Les derniers blocs minés

L’utilisateur peut aussi consulter la liste des dernières transactions sur les réseaux Ethereum, BNB, Bitcoin et Polygon, avec des détails comme : le hash, l’adresse émettrice (from), l’adresse destinataire (to), la valeur transférée, et les frais associés.

En complément, un graphique de dispersion permet de visualiser la répartition des transactions selon des tranches de valeur, offrant une vision claire et interactive des flux sur les différents réseaux.

### Accès portfolio (réservé aux utilisateurs connectés)

Pour accéder à la fonctionnalité portfolio, l’utilisateur doit créer un compte et se connecter. Cette section permet de gérer ses portefeuilles crypto sur les réseaux Ethereum, BNB et Polygon.

Une fois connecté, l’utilisateur peut :

Ajouter les adresses de ses portefeuilles cryptos, avec un label personnalisé.

Suivre en temps réel la balance de chaque portefeuille, ainsi que sa valeur en USD.

Visualiser la valeur totale de ses portefeuilles, et la répartition de ses actifs grâce à un graphique en doughnut.

Supprimer à tout moment l’un de ses portefeuilles depuis son espace personnel.

Cette fonctionnalité offre un suivi précis et pratique, centralisant toutes ses cryptos en un seul endroit sécurisé.

## Fonctionnement Technique
ChainTracker s’appuie principalement sur Django côté serveur pour gérer les requêtes, traiter les données et générer les pages web. Le front-end utilise des bibliothèques modernes comme Chart.js pour les graphiques et AOS (Animate On Scroll) pour les animations visuelles agréables.

**Disclaimer**
Pour récupérer les données blockchain, ChainTracker utilise l’API prédéfinie Alchemy. Cependant, les endpoints Solana et Bitcoin ne sont pas encore complètement supportés : il n’est pas encore possible d’accéder aux transactions Solana ni aux valeurs des transactions Bitcoin via cette API. Ces limitations sont temporaires et seront levées au fur et à mesure.

### Achitecture

1. **Collecte des données**
  - Pour les cryptomonnaies comme Ethereum, Binance Smart Chain (BNB) et Polygon, ChainTracker interroge directement l’API Alchemy via la bibliothèque Web3.py. Ces données comprennent le prix du gaz, les     derniers blocs, et les transactions récentes.
  - Pour Bitcoin et Solana, l’application effectue des requêtes JSON-RPC vers les endpoints correspondants d’Alchemy pour obtenir des informations sur les blocs.
  - Les données de marché (prix USD, capitalisation) sont récupérées via l’API CoinGecko.
  - Afin d’optimiser les performances et limiter les appels API, certains résultats sont mis en cache temporairement.

2. **Traitement des données**
  - Les vues Django traitent ces données pour les organiser (extraction, filtrage, calculs) avant de les envoyer au front-end.
  - Par exemple, les transactions sont nettoyées pour convertir des objets spécifiques (HexBytes) en formats lisibles.
  - Le portefeuille utilisateur est géré via une base de données locale, avec association des adresses crypto et calcul des valeurs totales en USD en temps réel.


3. **Affichage et interaction**
  - Les pages web affichent dynamiquement les données reçues à travers des templates Django.
  - Les graphiques (barres, doughnut) sont réalisés avec Chart.js pour offrir une visualisation claire et interactive.
  - Les animations douces et l’effet de défilement sont assurés grâce à la bibliothèque AOS, ce qui améliore l’expérience utilisateur.

### Exemple de flux utilisateur simple
  - L’utilisateur arrive sur la page d’accueil.
  - Django récupère les dernières données blockchain via Alchemy et CoinGecko.
  - Les données sont traitées et envoyées au template, qui affiche les infos (prix, blocs, transactions).
  - Si l’utilisateur est connecté et utilise la section portfolio, ses adresses sont utilisées pour interroger la blockchain via Web3.py et afficher ses soldes et graphiques personnalisés.

## Installation

### 0. Prérequis

Avant de commencer, assurez-vous d’avoir installé sur votre machine :
Python 3.8+
Téléchargez-le depuis le [[site officiel](https://python.org)](https://python.org).
pip (gestionnaire de paquets Python, généralement inclus avec Python).
Git (optionnel, mais recommandé pour cloner le dépôt)
Téléchargez-le depuis [git-scm.com](git-scm.com).

### 1. Cloner le dépôt GitHub

Ouvrez un terminal (ou invite de commande) et tapez :

```dotenv
git clone https://github.com/ton-utilisateur/ChainTracker.git
cd ChainTracker

(si vous n’avez pas Git, vous pouvez aussi télécharger le ZIP depuis GitHub et l’extraire.)
[site officiel](https://www.php.net/)

### 2. Créer un environnement virtuel Python

C’est une bonne pratique pour isoler les dépendances du projet :

```dotenv
python -m venv venv

Puis activez-le :

Sur Windows :
```dotenv
venv\Scripts\activate

Sur macOS/Linux :
```dotenv
source venv/bin/activate

### 3. Installer les dépendances

Avec l’environnement virtuel activé, installez les packages nécessaires :

```dotenv
pip install -r requirements.txt


### 4. **Configurer les variables d’environnement**:
Copiez le fichier .env.example (ou créez un fichier .env) à la racine du projet et configurez les variables importantes :

```dotenv
DEBUG=True
SECRET_KEY=ta_clef_secrete
ALCHEMY_API_ENDPOINTS={"ethereum": "https://eth-mainnet.alchemyapi.io/v2/votre_clef", "bnb": "...", "polygon": "...", "bitcoin": "...", "solana": "..."}
DATABASE_URL=sqlite:///db.sqlite3

Note :
Remplacez votre_clef_secrete par une vraie clé secrète Django .
Remplissez les URLs d’Alchemy avec vos propres endpoints.
    
### 5. **Initialiser la base de données**:
Exécutez les commandes suivantes pour créer la base et appliquer les migrations :

```dotenv
python manage.py migrate

### 6. **Lancer le serveur de développement**:

```dotenv
python manage.py runserver

Puis ouvrez votre navigateur à l’adresse : [http://127.0.0.1:8000](http://127.0.0.1:8000)

## Contact

- HOPSORE Paul -  [hopsorepaul@gmail.com](mailto:hopsorepaul@gmail.com)

