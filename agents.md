## Cautions
Do not use "constr" from pydantic, as that is deprecated and will be removed.  Use from pydantic import StringConstraints.


## Overview
This is a python django application. It exposes a Django Ninja APIs for manipulating data under `/api/v1/`. The project
is dependent on websecmap for storing data, starting scans and building reports.

Task queuing and scheduling happens with django celery beat, and tasks are created with celery. Authentication to the
app happens with django allauth, a legacy mode (django-two-factor-auth) will be removed in a future version.

The app is configured with django-constance. The admin is designed with django-jet-reboot. Exception logging happens
with sentry-sdk.

There is no frontend present in this app, though some django templates are present to improve the admin experience. 
The frontend is maintained as a separate repository: `Internet.nl-dashboard-frontend`.

Mail is sent via django-mail-admin. Subdomains are being harvested via another project called ctlssa.

Development is done with sqlite, production runs on postgres.

Caddy is not used for deployment, the app runs in a wsgi environment.
