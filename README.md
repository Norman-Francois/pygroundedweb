# pygroundedweb

Client Python pour l'API Grounded Web.

Ce module fournit une interface orientée objet pour interagir avec l'API Grounded Web, permettant la gestion des datasets, la configuration des outils de photogrammétrie (MicMac, CCTag) et le lancement d'analyses.

## Compatibilité

> [!IMPORTANT]
> Cette version de `pygroundedweb` est strictement liée aux versions de l'API Grounded Web pour garantir la cohérence des schémas de données (Pydantic) et des endpoints API.

| PyGroundedWeb | API Grounded Web (Backend) | Statut       |
|---------------|----------------------------|--------------|
| **v1.1.x**    | **v1.x.x ou supérieure**   | Supporté     |

Pour vérifier la version de votre instance API, vous pouvez consulter le point d'entrée `/api/` de votre api.

## Installation

### Via pip

```bash
pip install pygroundedweb
```

### Depuis les sources

Pour le développement local :

```bash
git clone [https://github.com/Norman-Francois/pygroundedweb.git](https://github.com/Norman-Francois/pygroundedweb.git)
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
from pygroundedweb import (
    GroundedWebClient,
    Configuration,
    ScaleBar,
    MicMac,
    CCTag,
    CloudCompare,
    DistortionModel
)

# 1. Initialisation et authentification
client = GroundedWebClient(base_url="http://localhost:8000/api")
client.login(username="admin", password="password")

# 2. Récupération d'un dataset existant
dataset = client.dataset.retrieve(pk=1)

# 3. Définition de la configuration d'analyse
config = Configuration(
    name="Config Standard",
    scale_bars=[
        ScaleBar(start=0, end=1, length=0.22),
        ScaleBar(start=2, end=3, length=0.50)
    ],
    detector=CCTag(),
    cloud_processor=CloudCompare(),
    sfm=MicMac(
        distorsion_model=DistortionModel.FRASER_BASIC,
        tapioca_resolution=2000
    )
)

# 4. Lancement de l'analyse
analysis = client.analysis.create(
    analysis_name="Analyse Batch 01",
    configuration=config,
    dataset=dataset,
    notify_by_email=True
)

print(f"Analyse créée : ID {analysis.pk} - Statut : {analysis.status}")

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
