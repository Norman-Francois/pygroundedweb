Tutoriel pas-à-pas
===================

Ce tutoriel guide un nouvel utilisateur pour prendre en main `pygroundedweb` :
- installation
- initialisation et authentification
- création d'un dataset et upload de photos
- création d'une `Configuration` complète
- lancement et suivi d'une `Analysis`

Prérequis
---------

Assurez-vous d'avoir Python 3.9+ et d'avoir installé le package (ou installé depuis les sources) :

.. code-block:: bash

   pip install pygroundedweb
   # ou pour le développement
   # pip install -e .

Initialisation et authentification
----------------------------------

.. code-block:: python

   from pygroundedweb import GroundedWebClient

   # Remplacez par l'URL de votre instance Grounded Web
   client = GroundedWebClient(base_url='http://localhost:8000')
   client.login(email='admin@example.com', password='password')

Créer un dataset et uploader des photos
---------------------------------------

Supposons que vous ayez deux listes de fichiers locaux : `photos_before` et `photos_after`.

.. code-block:: python

   photos_before = ['images/site1_before_01.jpg', 'images/site1_before_02.jpg']
   photos_after = ['images/site1_after_01.jpg']

   # Création du dataset et upload des photos (upload en parallèle)
   dataset = client.dataset.create(
       dataset_name='Site 1 - Inspection',
       photos_before=photos_before,
       photos_after=photos_after,
       max_workers=4,
       progress_callback=lambda done, total: print(f"Uploaded {done}/{total}")
   )

   print(f"Dataset créé : {dataset.pk} - {dataset.name}")

Remarques : le client gère l'initialisation de la ressource côté API, la création des
`datasetphotos`, l'upload vers les URLs présignées, puis la confirmation finale.

Configuration complète
----------------------

Voici un exemple illustratif de création d'une configuration en utilisant les modèles fournis
(par adaption selon votre setup réel). Nous utilisons : `ScaleBar`, `CCTag`, `CloudCompare`, `MicMac`.

.. code-block:: python

   from pygroundedweb import *

   cfg = Configuration(
       name='Standard MicMac + CloudCompare',
       scale_bars=[
           ScaleBar(start=0, end=1, length=0.22),
           ScaleBar(start=2, end=3, length=0.50),
       ],
       detector=CCTag(),
       cloud_processor=CloudCompare(),
       sfm=MicMac(
           distorsion_model=DistortionModel.FRASER_BASIC,
           zoom_final=ZoomFinal.ZOOM_FINAL_MEDIUM,
           tapioca_mode=TapiocaMode.DEFAULT,
           tapioca_resolution=2000,
           tapioca_second_resolution=1000,
       ),
       display_padding=True,
   )

   # Optionnel: créer la configuration via l'API
   cfg_created = client.configuration.create(cfg)
   print(f"Configuration créée : {cfg_created.pk} - {cfg_created.name}")

Lancer une analyse
------------------

Après avoir une configuration et un dataset, lancez l'analyse :

.. code-block:: python

   analysis = client.analysis.create(
       analysis_name='Analyse Site 1',
       configuration=cfg_created,
       dataset=dataset,
       notify_by_email=False,
   )

   print(f"Analyse créée : ID {analysis.pk}")

Suivi des résultats
-------------------

Le serveur peut traiter l'analyse en asynchrone. Voici la version la plus simple et lisible
pour attendre la fin d'une analyse en utilisant la méthode `refresh()` de l'objet :

.. code-block:: python

   import time

   # Récupérer l'analyse une première fois (par ex. après la création)
   analysis = client.analysis.retrieve(analysis.pk)

   # Boucle simple : on met à jour l'objet en place toutes les X secondes
   CHECK_INTERVAL = 15  # secondes

   while True:
       # met à jour l'objet `analysis` en interrogeant le serveur
       analysis.refresh()
       print(f"Statut : {analysis.status}")

       # condition de sortie : l'analyse est terminée (succès ou échec)
       if analysis.status in ("COMPLETED", "FAILED"):
           break

       time.sleep(CHECK_INTERVAL)

Remarque : cette approche est propre et lisible lorsque l'instance `analysis` a été
créée via le client (elle a donc un `_client` attaché). Si vous avez construit l'objet
localement sans passer par le client, `refresh()` lèvera un `RuntimeError` — dans
ce cas, utilisez `client.analysis.retrieve(pk)` à la place.

Conseils de bons usages
-----------------------

- Testez d'abord votre configuration avec un petit dataset pour valider les paramètres SFM.
- Préférez l'upload depuis un réseau stable ; en cas d'échecs réseau, les uploads sont ré-essayés.
- Pour automatiser massivement, implémentez une logique de retry sur la création des ressources
  côté client si vous rencontrez des erreurs temporaires côté API.

Support et suites
-----------------

Si vous avez des problèmes à suivre ce tutoriel, ouvre une Issue sur le dépôt GitHub avec :
- logs (niveau debug) s'il y a des erreurs réseau
- la configuration utilisée
- un petit jeu de données permettant de reproduire
