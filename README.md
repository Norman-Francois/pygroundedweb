# pygroundedweb

Client Python pour l'API Grounded Web.

Ce module fournit une interface orientée objet pour interagir avec l'API Grounded Web, permettant la gestion des datasets, la configuration des outils de photogrammétrie (MicMac, CCTag) et le lancement d'analyses.

## Compatibilité

> [!IMPORTANT]
> Cette version de `pygroundedweb` est strictement liée aux versions de l'API Grounded Web pour garantir la cohérence des schémas de données (Pydantic) et des endpoints API.

| PyGroundedWeb | API Grounded Web (Backend) | Statut   |
|---------------|----------------------------|----------|
| **v1.0.x**    | **v2.x.x**                 | Supporté |

Pour vérifier la version de votre instance API, vous pouvez consulter le point d'entrée `/api/` de votre api.

## Installation

### Via pip

```bash
pip install pygroundedweb
```

### Depuis les sources

Pour le développement local :

```bash
git clone https://github.com/Norman-Francois/pygroundedweb.git
cd pygroundedweb
pip install -e .
```

## Prérequis

* Python 3.9+
* requests
* pydantic >= 2.0

## Utilisation

La bibliothèque expose un client principal `GroundedWebClient` et des modèles de données typés.

### Exemple d'utilisation

```python
from pygroundedweb import *

# 1. Initialisation et authentification
client = GroundedWebClient(base_url="http://localhost:8000")
client.login(email="admin@example.com", password="password")

# 2. Récupération d'un dataset existant
dataset = client.dataset.retrieve(1)

# 3. Définition d'une configuration

config = Configuration(
    name="ConfigTest",
    scale_bars= [
        ScaleBar(start=0, end=1, length=.22),
        ScaleBar(start=2, end=3, length=.22),
        ScaleBar(start=4, end=5, length=.22),
        ScaleBar(start=6, end=7, length=.22)],
    detector= CCTag(),
    cloud_processor= CloudCompare(),
    sfm= MicMac(
        distorsion_model=DistortionModel.FRASER_BASIC,
        zoom_final=ZoomFinal.QUICK_MAC,
        tapioca_mode=TapiocaMode.ALL,
        tapioca_resolution=2000,
        tapioca_second_resolution=1000
    )
)

# 4. Lancement de l'analyse (exemple)
analysis = client.analysis.create(
    analysis_name="Analyse 01",
    configuration=config,
    dataset=dataset,
    notify_by_email=True
)

print(f"Analyse créée : ID {analysis.pk} - Statut : {analysis.status}")

# 5. Rafraîchir le statut de l'analyse depuis l'API
analysis.refresh()

# 6. Afficher l'analyse une fois rafraîchie
print(f"Analyse ID {analysis.pk} - Statut actuel : {analysis.status}")
```

## Documentation

La documentation complète est générée avec Sphinx et se trouve dans le dossier `docs/`.

Pour installer les dépendances nécessaires à la génération de la documentation :

```bash
pip install -r requirements.txt
```

Pour générer la documentation HTML localement :

```bash
cd docs
make html
# Le HTML sera généré dans docs/_build/html
```

Pour un rechargement automatique pendant le développement (optionnel) :

```bash
pip install sphinx-autobuild
cd docs
sphinx-autobuild . _build/html
```

## Structure du projet

* `client` : Gestion des requêtes HTTP et des endpoints API.
* `models` : Définitions Pydantic des objets métier (Analysis, Dataset, Configuration).

## Build

Pour générer le fichier wheel (.whl) pour la distribution :

```bash
pip install build
python3 -m build
```

## Développeur

Ce projet est développé et maintenu par :

* **Norman Francois** - [GitHub](https://github.com/Norman-Francois) | [LinkedIn](https://www.linkedin.com/in/norman-françois)

> [!TIP]
> Si vous souhaitez contribuer au projet ou signaler un bug, n'hésitez pas à ouvrir une **Issue** ou une **Pull Request** sur le dépôt officiel.

## Licence
Ce projet est sous licence **GNU GPL v3**.

* **Utilisation commerciale** : Autorisée.
* **Modification** : Autorisée, mais le code source modifié **doit** être redistribué sous la même licence (GPL v3).
* **Citation** : Vous devez créditer l'auteur original et indiquer si des modifications ont été apportées.
