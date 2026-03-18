# Opinionated defaults for Sphinx + Shibuya theme projects
# Source: based on Shibuya official docs and sphinx-autoapi best practices
# Template variables: {project_name}, {author_name}, {copyright_year}, {github_url}
# Used by /doc-writer:setup when no conf.py exists in the project

# -- Project metadata -------------------------------------------------------

project = "{project_name}"
author = "{author_name}"
copyright = "{copyright_year}, {author_name}"

# -- Extensions --------------------------------------------------------------

extensions = [
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx_design",
    "autoapi.extension",
]

# -- Napoleon (Google docstring style) ---------------------------------------

napoleon_google_docstring = True
napoleon_numpy_docstring = False

# -- sphinx-autoapi ----------------------------------------------------------

autoapi_dirs = ["../src"]
autoapi_root = "reference/api"
autoapi_add_toctree_entry = False
autoapi_options = [
    "members", "undoc-members", "show-inheritance",
    "show-module-summary", "imported-members",
]
autoapi_python_class_content = "both"
autoapi_member_order = "bysource"

# -- Intersphinx (cross-project linking) -------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# -- Shibuya theme -----------------------------------------------------------

html_theme = "shibuya"
html_theme_options = {
    "accent_color": "violet",
    "color_mode": "auto",
    "github_url": "{github_url}",
    "globaltoc_expand_depth": 1,
    "toctree_maxdepth": 3,
    "toctree_titles_only": True,
    "nav_links": [
        {"title": "Tutorials", "url": "tutorials/index"},
        {"title": "How-To Guides", "url": "how-to/index"},
        {"title": "Explanation", "url": "explanation/index"},
        {"title": "Reference", "url": "reference/index"},
    ],
}
