# DeepSeek Local App

DeepSeek Local App est un outil puissant conçu pour [brève description du projet]. Ce guide vous expliquera étape par étape comment configurer et utiliser le projet après l'avoir téléchargé depuis GitHub.

## Table des matières
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Contribuer](#contribuer)
- [Licence](#licence)
- [Créateurs](#créateurs)

---

## Prérequis

Avant de commencer, assurez-vous d'avoir les éléments suivants installés sur votre système :
- [Python](https://www.python.org/) (version X.X.X ou supérieure)
- [Git](https://git-scm.com/)
- [Ollama](https://ollama.com) (pour gérer les modèles IA)
- Toute autre dépendance spécifique à votre projet

---

## Installation

1. Clonez le dépôt depuis GitHub :
   ```bash
   git clone https://github.com/your-username/deepseek-local-app.git
   ```

2. Accédez au répertoire du projet :
   ```bash
   cd deepseek-local-app
   ```

3. Installez les dépendances Python requises :
   ```bash
   pip install -r requirements.txt
   ```

4. Installez **Ollama** :
   - Téléchargez et installez Ollama depuis [ollama.com](https://ollama.com).
   - Assurez-vous qu'Ollama est correctement configuré et accessible via `OLLAMA_HOST` (par défaut : `127.0.0.1:11434`).

5. Téléchargez le modèle **DeepSeek-Coder-v2** :
   - Une fois Ollama installé, exécutez la commande suivante pour télécharger le modèle :
     ```bash
     ollama pull deepseek-coder-v2
     ```

---

## Configuration

1. Localisez le fichier `.env` à la racine du projet. S'il n'existe pas, créez-en un et ajoutez les variables suivantes :
   ```properties
   DEFAULT_MODEL=deepseek-coder-v2
   CODE_STYLE=production
   DOC_STYLE=comments,type_hints
   OLLAMA_HOST=127.0.0.1:11434
   ```

2. Modifiez les valeurs si nécessaire pour les adapter à votre environnement.

---

## Utilisation

1. Lancez l'application avec **Gradio** :
   ```bash
   python app.py
   ```

2. Accédez à l'application dans votre navigateur à l'adresse suivante :
   ```
   http://127.0.0.1:7860
   ```

3. Suivez les instructions affichées à l'écran pour interagir avec l'application.

---

## Contribuer

Les contributions sont les bienvenues ! Veuillez suivre ces étapes pour contribuer :
1. Forkez le dépôt.
2. Créez une nouvelle branche :
   ```bash
   git checkout -b nom-de-la-fonctionnalité
   ```
3. Apportez vos modifications et validez-les :
   ```bash
   git commit -m "Description des modifications"
   ```
4. Poussez votre branche :
   ```bash
   git push origin nom-de-la-fonctionnalité
   ```
5. Ouvrez une pull request sur GitHub.

---

## Licence

Ce projet est sous licence [MIT License](LICENSE).

---

## Créateurs

Ce projet a été créé par :
- **Mohamed Salem Deddah**
- **Cheikh Mokhtar Maouloud**

Pour toute question ou assistance, contactez-nous à l'adresse suivante :  
**medsalmmedalyed@gmail.com**

---

N'hésitez pas à nous contacter si vous rencontrez des problèmes ou si vous avez des questions !
