Usage
=====

Installation
------------

.. code-block:: bash

   pip install pygroundedweb
   # ou depuis les sources pour le dev
   # git clone <repo>
   # pip install -e .

Exemple rapide
--------------

.. code-block:: python

   from pygroundedweb import GroundedWebClient

   client = GroundedWebClient(base_url='http://localhost:8000')
   client.login(email='admin@example.com', password='password')

   # Récupérer un dataset
   dataset = client.dataset.retrieve(1)
   print(dataset.name)

   # Créer une analyse (exemple minimal)
   # config = ... construisez une Configuration valide
   # analysis = client.analysis.create('Mon analyse', configuration=config, dataset=dataset)

Documentation API
-----------------

La documentation API est générée depuis les docstrings du code et se trouve dans la section "API".
