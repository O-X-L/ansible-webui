from datetime import datetime

# pylint: disable=W0622
project = 'Ansible WebUI'
copyright = f'{datetime.now().year}, OXL'
author = 'OXL'
extensions = ['sphinx_immaterial']
templates_path = ['_templates']
exclude_patterns = []
html_theme = 'sphinx_immaterial'
html_static_path = ['_static']
html_logo = '_static/img/logo.svg'
html_favicon = '_static/img/logo.svg'
html_js_files = ['https://files.oxl.at/js/feedback.js']
html_css_files = ['css/main.css', 'https://files.oxl.at/css/feedback.css']
master_doc = 'index'
display_version = True
sticky_navigation = True
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}
html_theme_options = {
    # 'banner_text': '<a href="https://github.com/O-X-L/ansible-webui">Repository on GitHub</a> | '
    #                '<a href="https://github.com/O-X-L/ansible-webui/issues/new/choose">Report Errors</a> | '
    #                '<a href="https://www.o-x-l.com">Get Support</a>'
    "site_url": "https://ansible-webui.oxl.app",
    "repo_url": "https://github.com/O-X-L/ansible-webui",
    "repo_name": "Ansible WebUI",
    "globaltoc_collapse": True,
    "features": [
        "navigation.expand",
        # "navigation.tabs",
        # "navigation.tabs.sticky",
        # "toc.integrate",
        "navigation.sections",
        # "navigation.instant",
        # "header.autohide",
        "navigation.top",
        "navigation.footer",
        # "navigation.tracking",
        # "search.highlight",
        "search.share",
        "search.suggest",
        "toc.follow",
        "toc.sticky",
        "content.tabs.link",
        "content.code.copy",
        "content.action.edit",
        "content.action.view",
        "content.tooltips",
        "announce.dismiss",
    ],
    "palette": [
        {
            "media": "(prefers-color-scheme: light)",
            "scheme": "default",
            "primary": "light-blue",
            "accent": "light-green",
            "toggle": {
                "icon": "material/lightbulb",
                "name": "Switch to dark-mode",
            },
        },
        {
            "media": "(prefers-color-scheme: dark)",
            "scheme": "slate",
            "primary": "deep-orange",
            "accent": "lime",
            "toggle": {
                "icon": "material/lightbulb-outline",
                "name": "Switch to light-mode",
            },
        },
    ],
    "version_dropdown": True,
    "version_info": [
        {
            "version": "https://demo.ansible-webui.oxl.app",
            "title": "Demo",
            "aliases": [],
        },
        {
            "version": "https://www.O-X-L.com",
            "title": "About OXL",
            "aliases": [],
        },
    ],
    "social": [
        {
            "icon": "fontawesome/solid/globe",
            "link": "https://www.O-X-L.com",
            "name": "About OXL",
        },
        {
            "icon": "fontawesome/brands/github",
            "link": "https://github.com/O-X-L",
            "name": "OXL on GitHub",
        },
    ],
}
html_title = 'Ansible WebUI'
html_short_title = 'Ansible WebUI'
