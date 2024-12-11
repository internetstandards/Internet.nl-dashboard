# stuff needed for releasing new versions of the dashboard.
# the tutorial must work.
import logging

from django.core.management import call_command

log = logging.getLogger(__name__)


def test_loading_fixtures(db, django_db_reset_sequences):
    # Note that reset sequences is mandatory, otherwise none of the foreign keys will be set up correctly.

    # these should load without errors. This checks if there have been no breaking migrations and that the entire
    # set of foreign keys are set up correctly in these fixtures.

    # When fixtures are incomplete they will say "FOREIGN KEY constraint failed" for example. It will not
    # say 'what' foreign key or 'what' key was being attempted to be referred to. Because that would be convenient.

    log.debug("Start Loading fixtures")
    call_command("loaddata", "dashboard_production_default_account")
    call_command("loaddata", "dashboard_production_example_email_templates")
    call_command("loaddata", "dashboard_production_periodic_tasks")
    call_command("loaddata", "dashboard_production_default_scanner_configuration")
    call_command("loaddata", "dashboard_production_default_scan_policy")
    log.debug("Done Loading fixtures")
