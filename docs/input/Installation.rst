Installation (draft)
###############

This is a draft document that will be ready in version 5.0 of the internet.nl dashboard.
More about this in this issue: https://github.com/internetstandards/Internet.nl-dashboard/issues/495

Overview
=====================
Setting up and configuring a dashboard instance is somewhat involved due to all available options and tailoring for
specific environments. With this tutorial you should be up and running within a single day, gaining familiarity and
confidence with with running a dashboard installation.

For general and paid support with installations, updates and managing installations: please send a support request to vraag@internet.nl.

Components
-------
The internet.nl dashboard consists of three components: server, backend and frontend.
The server hosts both the backend and frontend application.

Technical overview
------
The backend is written in python/django and communicates via JSON calls over HTTP.
The frontend is written HTML/Javascript/CSS(BootstrapVue).

Both the backend and frontend expose parts of the dashboard application. The frontend is the thing most regular users
will interact with. The backend is only meant for administrators for managing the application and logging in users.

What do you need
--------
* a domain name / address for hosting the application and also sending and receiving e-mail.
* a server, with certain specs...
* novice command line expertise probably
* ...


Server installation
======

0: Limiting access to the admin interface via IP addresses
1: Setting the SECRET_KEY and FIELD_ENCRYPTION_KEY (will happen on installation?) Automate this...
2: Creating the first application user (automated probably)

The fixtures needed to be installed are:

* dashboard_production_periodic_tasks
* dashboard_production_example_email_templates

Possibly an account has to be added and connected to the user. Should this be a command line thing?

todo: add security considerations


Backend application
======================
The backend application creates reports, manages scans and talks to the internet.nl API. This backend
is written in python/django and communicates via JSON calls over HTTP.

When the server is installed, the application uses several defaults.


The admin interface
--------------
All data in the application is visible in the admin interface. This interface should only be reachable by a limited
amount of users. This is enforced via the Server installation.

The admin interface can be viewed on the url ``/admin/``. Visiting this requires an application user which was setup
in the chapter 'server installation'. After logging in, the following interface is presented:

.. image:: installation/admin-interface.png

The interface exposes all database tables but more importantly Users/Account management features and application
configuration. User/account management is discussed in a separate chapter. (todo: link).


Configuration options
------
Configuration of the backend is done via the page ``/admin/constance/config/``. There are dozens of configuration
options each with explanation of what it does. Most settings involving domain names have the value internet.nl or
example.com as settings. These have to be adjusted to your installation domain.



SMTP settings for mails... (outboxes)



Frontend Application
====================

1: does it need configuration?
2: how to install it?
3: how to update it?

Admin shorthands present in the frontend application.
-------
For admins there are several shortcuts available that require some additional work in the backend interface.

These features allow account impersonation, quickly adding accounts+users (with the same name) and statistics.

.. image:: installation/frontend-admin-shorthands.png



Backend shell-level management
===============
The bash shell is used for manually updating and installing the application.

