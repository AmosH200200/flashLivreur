# ⚡ FlashLivreur

🌐 **Site en ligne : [https://flashlivreur.onrender.com](https://flashlivreur.onrender.com)**

> Mettez en relation clients et livreurs en quelques clics — rapidement, simplement, en temps réel.

FlashLivreur est une application web qui permet à tout particulier de commander une livraison ou de lancer une course, prise en charge par un livreur disponible. La plateforme centralise et fluidifie les échanges entre **clients**, **livreurs** et **commerçants**.

---

## 🚀 Fonctionnalités

### 👤 Client
- Inscription et authentification sécurisée
- Lancement d'une course en quelques étapes via le bouton **"Lancer une course"**
- Renseignement des informations de livraison (adresse de départ, destination, détails)
- **Suivi en temps réel** du trajet du livreur jusqu'à destination

### 🛵 Livreur
- Inscription sur la plateforme
- Finalisation du compte en agence FlashLivreur (validation physique)
- Réception des courses disponibles directement dans le dashboard
- Possibilité d'**accepter ou refuser** une course selon disponibilité

### 🏪 Commerçant
- *(Fonctionnalité à venir)*

> ⚠️ **Phase bêta** — D'autres fonctionnalités seront ajoutées progressivement.

---

## 🛠️ Prérequis

Avant d'installer le projet, assurez-vous d'avoir :

- [Python 3.10+](https://www.python.org/downloads/)
- [Django 4.x](https://www.djangoproject.com/)
- [Node.js](https://nodejs.org/) (pour les assets JavaScript)
- Un environnement virtuel Python (recommandé)

---

## ⚙️ Installation

```bash
# 1. Cloner le dépôt
git clone https://github.com/AmosH200200/flashLivreur.git 

cd flashLivreur

# 2. Créer et activer l'environnement virtuel
python -m venv env

# Sous Linux / macOS
source env/bin/activate

# Sous Windows
env\Scripts\activate

# 3. Installer les dépendances Python
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
cp .env.example .env
# Renseigner les valeurs dans le fichier .env

# 5. Appliquer les migrations
python manage.py migrate

# 6. Créer un super utilisateur (optionnel)
python manage.py createsuperuser

# 7. Lancer le serveur de développement
python manage.py runserver
```

L'application sera accessible sur : [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 📁 Structure du projet

```
flashlivreur/
├── manage.py
├── requirements.txt
├── .env.example
├── flashlivreur/        # Configuration principale Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/            # Gestion des utilisateurs (clients, livreurs)
├── courses/             # Logique des courses et livraisons
├── static/              # Fichiers CSS, JS
└── templates/           # Templates HTML
```

---

## 🧰 Stack technique

| Technologie | Usage |
|-------------|-------|
| Python / Django | Backend & logique métier |
| JavaScript | Interactions frontend & temps réel |
| HTML / CSS | Interface utilisateur |
| Django Channels *(recommandé)* | Suivi en temps réel (WebSocket) |

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Forkez le projet
2. Créez une branche (`git checkout -b feature/ma-fonctionnalite`)
3. Committez vos changements (`git commit -m "Ajout de ma fonctionnalité"`)
4. Poussez la branche (`git push origin feature/ma-fonctionnalite`)
5. Ouvrez une **Pull Request**

---

## 📬 Contact

Pour toute question ou suggestion, n'hésitez pas à ouvrir une [issue](https://github.com/AmosH200200/flashLivreur/issues) sur le dépôt.

---

*FlashLivreur — Rapide comme l'éclair. ⚡*