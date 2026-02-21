# Configuration Sphinx minimale pour pygroundedweb
import os
import sys
from datetime import datetime

# Ajouter le chemin du package pour autodoc
sys.path.insert(0, os.path.abspath('..'))
# Ajouter le répertoire src afin d'importer le package installé depuis les sources
sys.path.insert(0, os.path.abspath('../src'))

project = 'pygroundedweb'
author = 'Norman Francois'
copyright = f"{datetime.now().year}, {author}"

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx_autodoc_typehints',
]

# Template et static
templates_path = ['_templates']
html_static_path = ['_static']

# Thème recommandé
html_theme = 'sphinx_rtd_theme'

# Autodoc options
autodoc_typehints = 'description'
autodoc_member_order = 'bysource'

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
}

# Exclude build
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Project version if available
try:
    from pygroundedweb import __version__ as version
except Exception:
    version = ''

release = version

