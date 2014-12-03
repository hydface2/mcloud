

===========================================
Deploying to remote server
===========================================

ModeraCloud allows to deploy application to remote servers, same easily
as to localserver, without any code modification.

Before deModeraCloudCloud, you need to prepare server. Server needed is any
virtualmachine with ubuntu 14.04x64 on board.

Here is quickstart for common cloud providers:

.. toctree::
    :maxdepth: 1

    remote_prepare_aws.rst
    remote_prepare_digitalocean.rst

.. note::

    *AWS* has Free Tier program that allow to ModeraCloudS & ModeraCloud for free and host one simple site
    free forever. However, *DigitalOcean* has more democratic pricing and easier user interface.


After you have a remote servers dig into one of this topics:

.. toctree::
    :maxdepth: 1

    remote_ssl.rst
    remote_start.rst
    remote_publish.rst
    remote_update.rst
    remote_remove.rst
    remote_zero_down.rst

