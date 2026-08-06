# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
from datetime import date

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = "Internet.nl Dashboard"
copyright = "2020-2024, ECP / Internet.nl"
author = "internet.nl"
render_date = date.today()
today = os.environ.get("DOCS_RENDER_DATE", f"{render_date:%B} {render_date.day}, {render_date:%Y}")

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
]

latex_documents = [
    ("index", "dashboard.tex", "Internet.nl Dashboard Documentation", "internet.nl", "manual"),
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

autodoc_member_order = "bysource"

latex_engine = "lualatex"
latex_elements = {
    "papersize": "a4paper",
    "fontpkg": r"""
\directlua{luaotfload.add_fallback("dashboardemoji", {"Noto Color Emoji:mode=harf;"})}
\setmainfont{LiberationSans-Regular.ttf}[
    Scale=0.95,
    BoldFont=LiberationSans-Bold.ttf,
    ItalicFont=LiberationSans-Italic.ttf,
    BoldItalicFont=LiberationSans-BoldItalic.ttf,
    RawFeature={fallback=dashboardemoji}
]
\setsansfont{LiberationSans-Regular.ttf}[
    Scale=0.95,
    BoldFont=LiberationSans-Bold.ttf,
    ItalicFont=LiberationSans-Italic.ttf,
    BoldItalicFont=LiberationSans-BoldItalic.ttf,
    RawFeature={fallback=dashboardemoji}
]
\setmonofont{DejaVuSansMono.ttf}[
    Scale=0.92,
    BoldFont=DejaVuSansMono-Bold.ttf,
    ItalicFont=DejaVuSansMono-Oblique.ttf,
    BoldItalicFont=DejaVuSansMono-BoldOblique.ttf
]
""",
    "sphinxsetup": "verbatimforcewraps=true",
    "preamble": r"""
\usepackage[titles]{tocloft}
\cftsetpnumwidth {1.25cm}\cftsetrmarg{1.5cm}
\setlength{\cftchapnumwidth}{0.75cm}
\setlength{\cftsecindent}{\cftchapnumwidth}
\setlength{\cftsecnumwidth}{1.25cm}
""",
    "fncychap": r"\usepackage[Bjornstrup]{fncychap}",
    "printindex": r"\footnotesize\raggedright\printindex",
}
latex_show_urls = "footnote"
