.. _dev_mul:

.. include:: ../_include/head.rst

============
Translations
============

* Translations are added in `config/language.py <https://github.com/O-X-L/ansible-webui/blob/latest/src/oxl_ansible_webui/aw/config/language.py>`_.

* If you add features that introduce new language-codes - either auto-translate them with a tool like `deepl <https://deepl.com/>`_ or add the new codes commented-out to all languages and create a follow-up issue/ticket.

* New languages also have to be added:

  * to the frontend in `Nav.svelte <https://github.com/O-X-L/ansible-webui/blob/latest/frontend/src/base/Nav.svelte>`_

  * the country's flag needs to be added to `static/img/ <https://github.com/O-X-L/ansible-webui/blob/latest/src/oxl_ansible_webui/aw/static/img/>`_

  * the translations-file needs to be referenced in `config/language.py <https://github.com/O-X-L/ansible-webui/blob/latest/src/oxl_ansible_webui/aw/config/language.py>`_ for them to be picked-up by the API at `api_endpoints/frontend.py <https://github.com/O-X-L/ansible-webui/blob/latest/src/oxl_ansible_webui/aw/api_endpoints/frontend.py>`_ (:code:`APIBackendTranslations`)
