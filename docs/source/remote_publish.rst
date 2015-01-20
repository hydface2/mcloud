
=======================================
Publishing deployed application
=======================================

Publishing means exposing application under external domain name.

First make sure domain name is pointing to the correct ip address by pinging it::

    $ ping my-domain.com

Then you can say mcloud to publish application::

    $ mcloud -h  publish flask-redis@<ip-here> my-domain.com

Then you will see your domain name in url list in *mcloud list* command.
Load balancer is already reconfigured, so you can open your url in browser.

If you need SSL for your domain, you can publish ssl version of domain as well::

    $ mcloud -h <ip-here> publish flask-redis my-domain.com --ssl

.. note::
    Your application should be ready for ssl trafic. read :ref:`ssl` for details.

Unpublish is similar::

    $ mcloud -h <ip-here> unpublish my-domain.com

or::

    $ mcloud -h <ip-here> unpublish my-domain.com --ssl

App name is not needed here, as MCloud nows to which application app domain belongs.
One domain may belong to only one application.

.. note::
    "my-domain.com --ssl" is different domain than "my-domain.com" by MCLoud opinion,
    so you can bind SSL version and non-ssl to different applications.

