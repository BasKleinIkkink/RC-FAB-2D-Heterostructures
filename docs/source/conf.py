# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

# Add the package directory to the path so that we can import the package
import os, sys
sys.path.insert(0, os.path.abspath('..\..'))

project = 'LION Van der Waals Stacking Facility: Stacking setup'
copyright = '2022, Nynra'
author = 'Nynra'
release = '0.0.2'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
]

# Some config options for parsing th edocstrings
autodoc_member_order = 'bysource'
napoleon_google_docstring = False
napoleon_include_init_with_doc = True
napoleon_use_param = True
napoleon_use_ivar = False
napoleon_include_private_with_doc = True

templates_path = ['_templates']
exclude_patterns = []

source_suffix = '.rst'
master_doc = 'index'
language = 'en'
pygments_style = 'sphinx'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_theme = 'alabaster'
html_static_path = ['_static']
html_theme = 'furo'

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# This is required for the alabaster theme
# refs: http://alabaster.readthedocs.io/en/latest/installation.html#sidebars
# html_sidebars = {
# '**': [
# 'about.html',
# 'navigation.html',
# 'relations.html', # needs 'show_related': True theme option to display
# 'searchbox.html',
# 'donate.html',
# ]
# }

# -- Options for HTMLHelp output ------------------------------------------
# Output file base name for HTML help builder.
htmlhelp_basename = 'mainDoc'

# -- Options for LaTeX output ---------------------------------------------
latex_engine = 'pdflatex'
latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    'papersize': 'a4paper',
    'releasename':"Version 0.0.2",
    # Sonny, Lenny, Glenn, Conny, Rejne, Bjarne and Bjornstrup
    # 'fncychap': '\\usepackage[Lenny]{fncychap}',
    'fncychap': '\\usepackage{fncychap}',
    'fontpkg': '\\usepackage{amsmath,amsfonts,amssymb,amsthm}',
    'figure_align':'htbp',
    # The font size ('10pt', '11pt' or '12pt').
    #
    'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    #
    'preamble': r'''
    %% %% %% %% %% %% %% %% %% %% Meher %% %% %% %% %% %% %% %% %%
    %% %add number to subsubsection 2=subsection, 3=subsubsection
    %% % below subsubsection is not good idea

    \setcounter{secnumdepth}{3}
    %
    %% %% Table of content upto 2=subsection, 3=subsubsection
    \setcounter{tocdepth}{2}
    \usepackage{amsmath,amsfonts,amssymb,amsthm}
    \usepackage{graphicx}
    %% % r educe spaces for Table of contents, figures and tables
    %% % i t is used "\addtocontents{toc}{\vskip -1.2cm}" etc. in the document
    \usepackage[notlot,nottoc,notlof]{}
    \usepackage{color}
    \usepackage{transparent}
    \usepackage{eso-pic}
    \usepackage{lipsum}
    \usepackage{footnotebackref} %% link at the footnote to go to the place of footnote in the text
    %% spacing between line
    \usepackage{setspace}
    %% %% \onehalfspacing
    %% %% \doublespacing
    \singlespacing
    %% %% %% %% %% % d atetime
    \usepackage{datetime}
    \newdateformat{MonthYearFormat}{%
    \monthname[\THEMONTH], \THEYEAR}
    %% RO, LE will not work for 'oneside' layout.
    %% Change oneside to twoside in document class
    \usepackage{fancyhdr}
    \pagestyle{fancy}
    \fancyhf{}

    %% % Alternating Header for oneside
    \fancyhead[L]{\ifthenelse{\isodd{\value{page}}}{ \small \nouppercase{\leftmark} }{}}
    \fancyhead[R]{\ifthenelse{\isodd{\value{page}}}{}{ \small \nouppercase{\rightmark} }}
    %% % Alternating Header for two side
    %\fancyhead[RO]{\small \nouppercase{\rightmark}}
    %\fancyhead[LE]{\small \nouppercase{\leftmark}}
    %% for oneside: change footer at right side. If you want to use Left and right then use same as␣
    ˓→header defined above.
    \fancyfoot[R]{\ifthenelse{\isodd{\value{page}}}{{\tiny Meher Krishna Patel} }{\href{http://
    ˓→pythondsp.readthedocs.io/en/latest/pythondsp/toc.html}{\tiny PythonDSP}}}
    %% % Alternating Footer for two side
    %\fancyfoot[RO, RE]{\scriptsize Meher Krishna Patel (mekrip@gmail.com)}
    %% % page number
    \fancyfoot[CO, CE]{\thepage}
    \renewcommand{\headrulewidth}{0.5pt}
    \renewcommand{\footrulewidth}{0.5pt}

    \RequirePackage{tocbibind} %% % c omment this to remove page number for following
    \addto\captionsenglish{\renewcommand{\contentsname}{Table of contents}}
    \addto\captionsenglish{\renewcommand{\listfigurename}{List of figures}}
    \addto\captionsenglish{\renewcommand{\listtablename}{List of tables}}
    % \addto\captionsenglish{\renewcommand{\chaptername}{Chapter}}
    %% reduce spacing for itemize
    \usepackage{enumitem}
    \setlist{nosep}
    %% %% %% %% %% % Quote Styles at the top of chapter
    \usepackage{epigraph}
    \setlength{\epigraphwidth}{0.8\columnwidth}
    \newcommand{\chapterquote}[2]{\epigraphhead[60]{\epigraph{\textit{#1}}{\textbf {\textit{--#2}}}}}
    %% %% %% %% %% % Quote for all places except Chapter
    \newcommand{\sectionquote}[2]{{\quote{\textit{``#1''}}{\textbf {\textit{--#2}}}}}
    ''',

    'maketitle': r'''
    \pagenumbering{Roman} %% % to avoid page 1 conflict with actual page 1
    \begin{titlepage}
    \centering
    \vspace*{40mm} %% % * is used to give space from top
    \textbf{\Huge {Sphinx format for Latex and HTML}}
    \vspace{0mm}
    \begin{figure}[!h]
    \centering
    \includegraphics[scale=0.3]{lion_logo_blue1800x1080.jpg}
    \end{figure}
    \vspace{0mm}
    \Large \textbf{{Meher Krishna Patel}}
    \small Created on : Octorber, 2017
    \vspace*{0mm}
    \small Last updated : \MonthYearFormat\today
    %% \vfill adds at the bottom
    \vfill
    \small \textit{More documents are freely available at }{\href{http://pythondsp.readthedocs.
    ˓→io/en/latest/pythondsp/toc.html}{PythonDSP}}
    \end{titlepage}

    \clearpage
    \pagenumbering{roman}
    \tableofcontents
    \listoffigures
    \listoftables
    \clearpage
    \pagenumbering{arabic}
    ''',
    # Latex figure (float) alignment

    # 'figure_align': 'htbp',
    'sphinxsetup': \
    'hmargin={0.7in,0.7in}, vmargin={1in,1in}, \
    verbatimwithframe=true, \
    TitleColor={rgb}{0,0,0}, \
    HeaderFamily=\\rmfamily\\bfseries, \
    InnerLinkColor={rgb}{0,0,1}, \
    OuterLinkColor={rgb}{0,0,1}',
    'tableofcontents':' ',
}

latex_logo = '_static/lion_logo_blue1800x1080.jpg'
# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
# author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'main.tex', 'Sphinx format for Latex and HTML',
    'Meher Krishna Patel', 'report')
    ]

# -- Options for Epub output ----------------------------------------------
# Bibliographic Dublin Core info.
#epub_title = project
#epub_author = author
#epub_publisher = author
#epub_copyright = copyright

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
#
# epub_identifier = ''
# A unique identification for the text.
#
# epub_uid = ''
# A list of files that should not be packed into the epub file.
#epub_exclude_files = ['search.html']

# Example configuration for intersphinx: refer to the Python standard library.
#intersphinx_mapping = {'https://docs.python.org/': None}
#def setup(app):
#    app.add_stylesheet('custom.css') # remove line numbers
#    app.add_javascript('copybutton.js') # show/hide prompt >>>

# use :numref: for references (instead of :ref:)
#numfig = True
#smart_quotes = False
#html_use_smartypants = False
#html_theme = 'sphinx_rtd_theme'
