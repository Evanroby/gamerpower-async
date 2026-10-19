import importlib.metadata

project = "gamerpower-async"
author = "evanroby"
copyright = "2026, evanroby"
release = importlib.metadata.version("gamerpower-async")
version = ".".join(release.split(".")[:2])

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

autodoc_member_order = "bysource"
autodoc_typehints = "description"
autodoc_typehints_format = "short"
napoleon_google_docstring = True
napoleon_numpy_docstring = False

exclude_patterns = ["_build"]

html_theme = "furo"
html_title = f"gamerpower-async {release}"
