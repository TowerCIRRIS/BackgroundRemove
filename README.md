# Suppression d'arrière-plan (application locale)

Application web minimale pour supprimer l'arrière-plan d'une image. Elle repose sur la bibliothèque Python [withoutbg](https://github.com/withoutbg/withoutbg-python) et s'exécute sur l'ordinateur de l'utilisateur : le serveur écoute uniquement sur `127.0.0.1` et n'est pas accessible depuis le réseau.

## Contenu du dossier

| Fichier | Rôle |
| --- | --- |
| `app.py` | Serveur Flask : réception de l'image, traitement par withoutbg, renvoi d'un PNG |
| `index.html` | Interface web (aperçu avant/après, choix du fond, téléchargement) |
| `requirements.txt` | Dépendances Python |
| `install.bat` | Installation automatisée sous Windows (environnement virtuel et dépendances) |
| `run.bat` | Lancement sous Windows (serveur et ouverture du navigateur) |

Les trois fichiers doivent rester dans le même dossier.

## Prérequis

- **Python 3.10 ou supérieur** (le code utilise la syntaxe de typage `str | None`).
- **pip**, le gestionnaire de paquets de Python (inclus avec Python dans la plupart des installations).
- **Environ 1,5 Go d'espace disque** pour le modèle de segmentation, téléchargé automatiquement lors du premier traitement local.
- **Une connexion Internet pour le premier lancement uniquement** (téléchargement du modèle depuis Hugging Face). Le fonctionnement ultérieur est entièrement hors ligne. Une procédure d'installation sans accès Internet est décrite plus bas.
- **Un navigateur web récent** (Firefox, Chrome, Edge ou Safari).

Aucun processeur graphique (GPU) n'est requis : le modèle s'exécute sur le processeur (CPU) via ONNX (*Open Neural Network Exchange*, format standard de modèles d'apprentissage automatique).

Dépendances Python installées par `requirements.txt` :

| Paquet | Usage |
| --- | --- |
| `withoutbg` | Modèle et logique de suppression d'arrière-plan |
| `flask` (3.0 ou supérieur) | Serveur web local |
| `pillow` | Lecture, orientation et écriture des images |

## Installation et lancement rapides (Windows)

1. Double-cliquer sur `install.bat` : le script vérifie la présence de Python 3.10 ou supérieur, crée l'environnement virtuel `.venv` et installe les dépendances.
2. Double-cliquer sur `run.bat` : le script démarre le serveur et ouvre automatiquement l'interface dans le navigateur. Si l'installation n'a pas encore été effectuée, `run.bat` la déclenche.

Pour arrêter l'application, fermer la fenêtre de commandes ou appuyer sur `Ctrl+C`. Les sections suivantes décrivent l'installation manuelle, valable pour Windows, macOS et Linux.

## Installation manuelle

Les commandes suivantes s'exécutent dans un terminal ouvert dans le dossier contenant les fichiers de l'application. L'utilisation d'un environnement virtuel évite d'installer les dépendances dans l'installation Python globale.

### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Si l'activation est refusée par la politique d'exécution des scripts, la commande suivante l'autorise pour la session en cours :

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### macOS et Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Lancement

Avec l'environnement virtuel activé :

```bash
python app.py
```

L'interface est ensuite disponible à l'adresse <http://127.0.0.1:5000>. L'arrêt du serveur s'effectue avec `Ctrl+C` dans le terminal.

Lors des lancements suivants, il suffit de réactiver l'environnement virtuel (commande `activate` ci-dessus), puis d'exécuter `python app.py`.

## Utilisation

1. Déposer une image dans la zone prévue, cliquer pour la choisir, ou la coller avec `Ctrl+V`.
2. Conserver le moteur **Local** (option par défaut).
3. Cliquer sur **Supprimer l'arrière-plan**.
4. Choisir au besoin un fond de remplacement (transparent, blanc, noir ou couleur personnalisée).
5. Télécharger le résultat au format PNG, ou le copier dans le presse-papiers.

Formats acceptés en entrée : JPG, PNG, WebP, BMP et TIFF, jusqu'à 25 Mo. Le résultat est toujours un PNG ; le fond « transparent » conserve le canal alpha (canal de transparence de l'image).

Le premier traitement local télécharge le modèle et peut durer plusieurs minutes. Les traitements suivants réutilisent le modèle déjà chargé en mémoire.

## Retouche du résultat

Le modèle décide seul de ce qui constitue le sujet : withoutbg n'expose aucun paramètre de sensibilité. Lorsqu'un élément voulu est supprimé (une main tenant un objet, par exemple), ou qu'un élément indésirable est conservé, l'interface permet de corriger le résultat sans retraitement.

| Outil | Effet |
| --- | --- |
| **Baguette** | Un clic sur une zone supprimée à tort restaure toute la région contiguë de teinte similaire (par exemple une main et l'avant-bras en un seul clic). Un nouveau clic sur les parties restantes, notamment dans l'ombre, complète la zone. Avec `Alt` maintenu, le clic efface la région au lieu de la restaurer. |
| **Tolérance** de la baguette | Écart de teinte accepté par rapport au point cliqué. Une valeur trop élevée fait déborder la région sur le fond ; une valeur trop faible laisse des trous. La valeur par défaut est 18. |
| **Pinceau : restaurer** | Repeint la zone avec les pixels de l'image originale. |
| **Pinceau : effacer** | Rend la zone transparente. |
| **Taille** et **dureté** du pinceau | Diamètre (en pourcentage de la plus grande dimension de l'image) et netteté du bord du trait. |
| **Annuler** / **Rétablir** | Historique des traits (`Ctrl+Z`, `Ctrl+Y`). |
| **Original en filigrane** | Affiche l'original en transparence sous le résultat, pour repérer les zones à restaurer. |
| **Bords semi-transparents : renforcer l'opacité** | Augmente l'opacité des zones que le modèle a conservées de façon partielle (bords flous, cheveux). N'a aucun effet sur une zone entièrement supprimée, qui se récupère avec la baguette ou le pinceau. |
| **Nettoyage** | Supprime les résidus très peu opaques laissés par le modèle. |
| **Réinitialiser les retouches** | Supprime tous les traits et remet les deux réglages à zéro. |

Raccourcis : `W` sélectionne la baguette, `X` bascule entre les pinceaux « restaurer » et « effacer », `Alt` maintenu inverse temporairement l'outil actif, `[` et `]` modifient la taille du pinceau.

La baguette compare la teinte (chrominance) de chaque pixel à celle du point cliqué, sans tenir compte de la luminosité : une peau éclairée et une peau dans l'ombre sont ainsi regroupées, alors qu'un fond neutre (carrelage, mur) en reste distinct. Elle fonctionne moins bien lorsque l'élément à récupérer a une teinte proche de celle du fond.

Les retouches sont prévisualisées à une résolution réduite pour rester fluides, mais le fichier téléchargé est recomposé à la **résolution complète** de l'image.

## Fonctionnement hors ligne

Pour éviter tout accès à Internet au premier lancement :

1. Télécharger l'ensemble du dossier du modèle depuis <https://huggingface.co/withoutbg/withoutbg-openweights-onnx>.
2. Conserver ensemble tous les fichiers du dossier (le fichier `withoutbg-open-weights.onnx` ainsi que son fichier de métadonnées `withoutbg-open-weights.onnx.json` et les autres graphes du modèle).
3. Définir la variable d'environnement `WITHOUTBG_MODEL_PATH` avec le chemin du fichier `withoutbg-open-weights.onnx` avant de lancer l'application.

Windows (PowerShell) :

```powershell
$env:WITHOUTBG_MODEL_PATH = "C:\chemin\vers\withoutbg-open-weights.onnx"
python app.py
```

macOS et Linux :

```bash
export WITHOUTBG_MODEL_PATH="/chemin/vers/withoutbg-open-weights.onnx"
python app.py
```

## Mode API cloud (optionnel)

L'interface propose un second moteur, l'API (interface de programmation) cloud de withoutBG, dont la qualité est supérieure sur les cheveux et la fourrure. Ce mode est payant, nécessite une clé commençant par `sk_` et **envoie l'image aux serveurs de withoutBG**. La clé peut être saisie dans l'interface ou fournie par la variable d'environnement `WITHOUTBG_API_KEY`. Ce mode n'est pas nécessaire au fonctionnement local.

## Dépannage

| Symptôme | Cause probable et solution |
| --- | --- |
| `403 Forbidden` ou échec lors du téléchargement du modèle | Accès à Hugging Face bloqué (pare-feu, proxy, réseau d'entreprise). Utiliser la procédure de la section « Fonctionnement hors ligne ». |
| `ModuleNotFoundError: No module named 'withoutbg'` | L'environnement virtuel n'est pas activé, ou `pip install -r requirements.txt` n'a pas été exécuté. |
| `Address already in use` | Le port 5000 est occupé. Modifier la valeur `port=5000` à la fin de `app.py`, puis ouvrir la nouvelle adresse. |
| Erreur de syntaxe à l'import de `app.py` | Version de Python inférieure à 3.10. Vérifier avec `python --version`. |
| « Image trop lourde » | Le fichier dépasse 25 Mo. Réduire l'image, ou ajuster `MAX_UPLOAD_MB` dans `app.py`. |
| Contours transparents perdus après enregistrement | Un enregistrement au format JPG supprime la transparence. Conserver le format PNG. |

## Licences

Le code de cette application s'appuie sur le SDK (*Software Development Kit*) withoutbg, publié sous licence Apache 2.0. Le modèle de segmentation est un composant distinct soumis à ses propres conditions, notamment la licence Meta DINOv3 pour une partie des poids et la licence MIT pour la branche BiRefNet. Les conditions complètes figurent dans le dépôt <https://github.com/withoutbg/withoutbg-python> et sur la page du modèle sur Hugging Face. Une vérification de ces conditions est recommandée avant tout usage commercial.
