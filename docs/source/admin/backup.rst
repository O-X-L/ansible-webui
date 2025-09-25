.. _administration_backup:

.. include:: ../_include/head.rst


======
Backup
======

The only data to back-up is:

* Your encryption key

* The database - placed at :code:`${HOME}/.config/ansible-webui/aw.db` or as configured

  Especially when using SQLite as database - it is recommended as these DBs can get corrupted on some occasion

* The logs - placed at :code:`${HOME}/.local/share/ansible-webui/` or as configured
