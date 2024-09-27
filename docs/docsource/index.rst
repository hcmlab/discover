..  NovaServer documentation master file, created by
    sphinx-quickstart on Thu Apr 20 15:40:50 2023.
    You can adapt this file completely to your liking, but it should at least
    contain the root `toctree` directive.

:github_url: https://github.com/hcmlab/nova-server


NovaServer documentation!
======================================

This project contains a nova backend that can be used to train models or generate explanations for the models on a remote server.
The server api can be used either from the UI itself or as a standalone tool to just interact with an existing nova database.

.. toctree::
    :maxdepth: 2
    :caption: Getting started

    tutorials/introduction
    tutorials/examples
      
.. toctree::
     :maxdepth: 2
     :caption: Packages

     api/nova_server.app
     api/nova_server.backend
     api/nova_server.exec
     api/nova_server.route
     api/nova_server.utils

.. toctree::
    :maxdepth: 2
    :caption: Modules

    modules/overview_link.md


Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
