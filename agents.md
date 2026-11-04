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

Issues of the project can be found here, including front end issues: 
https://github.com/internetstandards/Internet.nl-dashboard/issues

The frontend repo can be found here:
https://github.com/internetstandards/Internet.nl-dashboard-frontend


## Writing tests

Any assert statement should always have a meaning behind them with reasoning what was expected and why. For example:
assert x == 1, <explation here>


## Special precautions:

- Do not ever alter readme.md or agents.md files or `docs/*` without explicit request. Do not ask for this.
- If there are failures in pydantic, don't create stubs but ask the human to fix those linting errors before continuing.
- Do not use "constr" from pydantic, as that is deprecated and will be removed.  Use from pydantic import StringConstraints.
- Do not alter the tldextract.py file.
- When working with Django, don't refer to an objects .pk but by the objects .id. So organization.id
- Don't point to django object instances with a \_id, but with .id, so not organization_id but organization.id
- Do not ever add global or file-wide type ignores, as it obfuscates potential problems
- Avoid adding or copying `# noqa:` and `# ty:ignore` statements, a lot where blanket added to ease migration to
  ruff/ty. They should not be considered a default solution to linting or typing issues.
- Prefer generators over sequences (list, sets, tuples), especially when dealing with things like Url and Endpoint
  objects, as it will reduce memory consumption.
- Avoid arbitrary sorting of sequences (list, sets, tuples).
- Avoid using `capsys` and `caplog` in tests as it makes them flaky.
- Never create solutions using `asyncio`, it will create an undebuggable mess where theory and reality will never meet.
- Do not over-decompose methods into 1/2/3-liners, especially if they are only used once, this results in a deep call
  graph and code maze
- Do not create django models with auto_now or auto_now_add, as this results in hard to debug situations
- Never use `typing.cast` to silence or work around type errors



## Committing code

When committing code, always make sure commits are signed.
When a push is performed, note the gitlab urls and always echo the full urls to the commit / branch so it's easy for a
developer to follow.

## Logging

Write or append all logs to the logging directory agents-log/YYYY-MM-DD-subject.log. Where YYYY-MM-DD is the date
of the log and subject is the name of what you're working on. For example a specific scanner or reporting etc.

Also log any input from the user to the logging directory agents-log/YYYY-MM-DD-subject-input.log. This helps with
documenting parts of the project for others or later llm usage. So human input and llm actions are separate from each other.

The sanity-check does not need to be logged. Logs are not committed to git.


