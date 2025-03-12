from datetime import datetime

# pylint: disable=W0622
project = 'Ansible WebUI'
copyright = f'{datetime.now().year}, OXL'
author = 'OXL'
extensions = ['piccolo_theme']
templates_path = ['_templates']
exclude_patterns = []
html_theme = 'piccolo_theme'
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
    'banner_text': '<a href="https://github.com/O-X-L/ansible-webui">Repository on GitHub</a> | '
                   '<a href="https://github.com/O-X-L/ansible-webui/issues/new/choose">Report Errors</a> | '
                   '<a href="https://www.o-x-l.com">Get Support</a>'
}
html_short_title = 'Ansible WebUI'
