.. _usage_ssh_hostkeys:

.. include:: ../_include/head.rst

.. |ssh_hostkey_dark| image:: ../_static/img/ssh_hostkey_dark.webp
   :class: wiki-img-dark

.. |ssh_hostkey_light| image:: ../_static/img/ssh_hostkey_light.webp
   :class: wiki-img-light

.. |ssh_hostkey_scan_dark| image:: ../_static/img/ssh_hostkey_scan_dark.webp
   :class: wiki-img-sm-dark

.. |ssh_hostkey_scan_light| image:: ../_static/img/ssh_hostkey_scan_light.webp
   :class: wiki-img-sm-light

.. |ssh_hostkey_job_dark| image:: ../_static/img/ssh_hostkey_job_dark.webp
   :class: wiki-img-sm-dark

.. |ssh_hostkey_job_light| image:: ../_static/img/ssh_hostkey_job_light.webp
   :class: wiki-img-sm-light

.. |ssh_hostkey_log_dark| image:: ../_static/img/ssh_hostkey_log_dark.webp
   :class: wiki-img-sm-dark

.. |ssh_hostkey_log_light| image:: ../_static/img/ssh_hostkey_log_light.webp
   :class: wiki-img-sm-light

============
SSH Hostkeys
============

Manage
######

At the :code:`System - SSH Hostkeys` page you can add and manage known hosts.

|ssh_hostkey_dark|

|ssh_hostkey_light|

You are able to scan targets for existing hostkeys by supplying a DNS-Hostname, IP or Network in CIDR-format.

If you supply a DNS-Hostname - the resolved IPs will also be scanned.

|ssh_hostkey_scan_dark|

|ssh_hostkey_scan_light|

----

Linking
#######

You are able to link SSH-Hostkey-files to Jobs and Repositories.

|ssh_hostkey_job_dark|

|ssh_hostkey_job_light|

You can verify it in the logs:

|ssh_hostkey_log_dark|

|ssh_hostkey_log_light|
