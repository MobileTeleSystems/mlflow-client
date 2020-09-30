# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import sys, os, re
import subprocess

from collections import OrderedDict
from setuptools_git_versioning import get_tag, get_all_tags, get_sha
from packaging import version as Version

sys.path.insert(0, os.path.abspath('..'))
extensions = ['sphinx.ext.autodoc', 'numpydoc', 'sphinx.ext.autosummary', 'sphinx_rtd_theme', 'changelog']
numpydoc_show_class_members = False

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'mlflow-client'
copyright = '2020, msmarty4'
author = 'msmarty4'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.

ver = Version.parse(subprocess.check_output('python ../setup.py --version', shell=True, universal_newlines=True).strip())
version = ver.base_version
# The full version, including alpha/beta/rc tags.
release = ver.public

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False


# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']


# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'mlflow-client-doc'


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'mlflow-client.tex', 'mlflow-client Documentation',
     'msmarty4', 'manual'),
]


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'mlflow-client', u'mlflow-client Documentation',
     [author], 1)
]


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'mlflow-client', u'mlflow-client documentation',
     author, 'mlflow-client', 'One line description of project.',
     'Miscellaneous'),
]

changelog_sections = ["general", "client", "artifact", "experiment", "model", "page", "run", "tag", "dependency", "docs", "samples", "ci", "tests"]

changelog_inner_tag_sort = ["breaking", "deprecated", "feature", "bug", "refactor"]

changelog_hide_sections_from_tags = True

# how to render changelog links - these are plain
# python string templates, ticket/pullreq/changeset number goes
# in "%s"
changelog_render_ticket = "https://jira.bd.msk.mts.ru/browse/%s"
changelog_render_pullreq = "https://git.bd.msk.mts.ru/bigdata/platform/dsx/mlflow-client/-/merge_requests/%s"
changelog_render_changeset = "https://git.bd.msk.mts.ru/bigdata/platform/dsx/mlflow-client/-/commit/%s"

tags = set([ver])
tags.update(Version.parse(tag) for tag in get_all_tags())
tags = [tag.public for tag in reversed(sorted(list(tags)))]

versions = [("latest", "/latest/")]
versions.extend([(tag, "/{}/".format(tag)) for tag in tags])

tag = get_tag()
tag_sha = get_sha(tag)
head_sha = get_sha('HEAD')
on_tag = tag and head_sha == tag_sha

context = {
    'current_version': release,
    'version_slug': release,
    'versions': versions,
    'downloads': [
        ("html", "http://rep.msk.mts.ru/artifactory/files/mlflow-client-docs/html-{release}.tar.gz".format(release=release))
    ],
    'single_version': False,
    'gitlab_host': 'git.bd.msk.mts.ru',
    'gitlab_user': 'bigdata/platform/dsx',
    'gitlab_repo': 'mlflow-client',
    'gitlab_version': version if on_tag else 'master',
    'conf_py_path': '/docs/',
    'display_gitlab': True,
    'commit': head_sha[:8]
}

if 'html_context' in globals():
    html_context.update(context)

else:
    html_context = context