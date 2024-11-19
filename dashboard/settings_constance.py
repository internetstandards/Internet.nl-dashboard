import os
from collections import OrderedDict

CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

CONSTANCE_ADDITIONAL_FIELDS = {
    "json": ["django.forms.fields.JSONField", {"required": False}],
}

CONSTANCE_CONFIG = {
    # general settings
    'DASHBOARD_FRONTEND_URL': (
        'https://dashboard.example.com',
        'Url where the frontend is reachable on for end users. This url is references in a few parts of the frontend.',
        str
    ),
    'DASHBOARD_MAXIMUM_DOMAINS_PER_LIST': (
        1000,
        'The maximum amount of domains that can be in a list. There will be no crash when somebody imports more '
        'via a spreadsheet: domains will be added but the list will refuse to scan and show a warning.'
        'In normal use cases these limits will not be reached as average lists are about 300 domains. Lists '
        'with 600 domains are unusual. Lists with 10.000+ domains are exceptional.',
        int
    ),
    'DASHBOARD_MAXIMUM_DOMAINS_PER_SPREADSHEET': (
        1000,
        'The maximum amount of domains that can be imported via a spreadsheet at one time. '
        'In normal use cases these limits will not be reached.',
        int
    ),
    'DASHBOARD_MAXIMUM_LISTS_PER_SPREADSHEET': (
        20,
        'The maximum amount of lists that can be imported via a spreadsheet at one time. '
        'In normal usec ases these limits will not be reached.',
        int
    ),
    'DASHBOARD_FRONT_PAGE_URL_LISTS': (
        '',
        'Comma separated list of urllists of which all reports will automatically be shared on the front page. '
        'For example: 1,2,3. No data means the front page will not show any lists, just the usual information.',
        str
    ),

    # scan settings
    'SCAN_AT_ALL': (
        True,
        'This enables or disabled all scans. Note that scans that are picked up will still be processed.',
        bool
    ),
    'INTERNET_NL_API_URL': (
        'https://batch.example.com/api/batch/v2',
        'The internet address for the Internet.nl API installation. This is commonly called a "batch server".',
        str
    ),
    'INTERNET_NL_SCAN_TRACKING_NAME': (
        'Dashboard InternetNL [countrycode]',
        'This setting is used when sending API requests for tracking purposes. Setting this value make it clear who '
        'is sending API requests. A good setting contains something unique about this installation, such as an '
        'organization name. The maximum length is 40 characters.',
        str
    ),
    "SCANNER_NAMESERVERS": (
        ["193.17.47.1", "185.43.135.1", "193.110.81.0", "185.253.5.0", "9.9.9.9", "149.112.112.112",
         "2001:148f:ffff::1", "2001:148f:fffe::1", "2a0f:fc80::", "2a0f:fc81::", "2620:fe::fe", "2620:fe::9"],
        "Nameservers used during scans (dns endpoints and subdomains). This string is loaded as JSON, but not validated"
        " due to limitations of this settings library. Be careful when editing(!). "
        "This information is cached and loaded only once every 10 minutes.",
        "json",
    ),
    "CREDENTIAL_CHECK_URL": (
        "https://batch.example.com/api/",
        "The url where internet.nl api credentials are checked. This is usually the bare INTERNET_NL_API_URL endpoint. "
        "This feature is used in the admin interface at account management. "
        "There the option 'check credentials' can be performed for each account.",
        str
    ),

    # email settings
    'EMAIL_NOTIFICATION_SENDER': (
        'noreply@example.com',
        'The sender of email report notification: this is the e-mail that contains the current scan results and a '
        'summary. It also compares the result to the previous results. Use an e-mail address that is in use.',
        str
    ),
    'EMAIL_FALLBACK_LANGUAGE': (
        'en',
        'Default language used for templates. Template should end with _en in lowercase. Example e-mail templates are '
        'included and can be found in the menu of the admin interface.',
        str
    ),
    'EMAIL_TEST_RECIPIENT': (
        'info@example.com',
        'Which e-mail address receives the testmail from the command "dashboard send_testmail". This command tests if '
        'the e-mail outbox is properly configured.',
        str
    ),
    'EMAIL_DASHBOARD_ADDRESS': (
        'https://example.com',
        'The address of the dashboard, can be set to any url. Available in email template at {{dashboard_address}}. '
        'This is probably the same as the DASHBOARD_FRONTEND_URL. Only in rare cases this would differ.',
        str
    ),

    # security.txt
    "SECURITY_TXT_IS_REDIRECTED": (
        False,
        "Security.txt is used to allow security researchers to report vulnerabilities. This can be either set to a "
        "redirect to an existing security.txt or configured with your own security.txt policy.",
        bool
    ),
    "SECURITY_TXT_REDIRECT_URL": (
        "https://example.com/.well-known/security.txt",
        "The url where the security.txt files redirect to. This is usually an external site.",
        str
    ),
    "SECURITY_TXT_CONTENT": (
        "",
        "The content of the security.txt file, located at .well-known/security.txt. Only "
        "used when redirect is disabled. Go to securitytxt.org to create a configuration "
        "for this installation.",
        str
    ),

    # signup settings
    "SHOW_SIGNUP_FORM": (
        False,
        "Show the signup form on the front page, so visitors of the dashboard can sign up for an account. Currently "
        "only internet.nl signup questions are available. So this might not be useful for most installations.",
        bool,
    ),
    'EMAIL_NOTIFICATION_SENDER_FOR_SIGNUP': (
        'noreply@example.com',
        'The sender of the "thank you" e-mail after signing up. The template for this e-mail can be found in the '
        'E-Mail templates menu of the admin interface.',
        str
    ),
    'DASHBOARD_SIGNUP_NOTIFICATION_EMAIL_ADRESSES': (
        'support@example.com',
        'Comma separated list of email addresses to notify about new signups. Don\'t add extra spaces in between.',
        str
    ),

    # timeouts
    "SCAN_TIMEOUT_MINUTES_DISCOVERING_ENDPOINTS": (
        10000,
        'timeout for phase DISCOVERING_ENDPOINTS',
        int
    ),
    "SCAN_TIMEOUT_MINUTES_RETRIEVING_SCANABLE_URLS": (
        1440,
        'timeout for phase RETRIEVING_SCANABLE_URLS',
        int
    ),
    "SCAN_TIMEOUT_MINUTES_REGISTERING_SCAN_AT_INTERNET_NL": (
        1440,
        'timeout for phase REGISTERING_SCAN_AT_INTERNET_NL',
        int
    ),
    "SCAN_TIMEOUT_MINUTES_IMPORTING_SCAN_RESULTS": (
        10000,
        'timeout for phase IMPORTING_SCAN_RESULTS',
        int
    ),
    "SCAN_TIMEOUT_MINUTES_CREATING_REPORT": (
        10000,
        'timeout for phase CREATING_REPORT',
        int
    ),
    "SCAN_TIMEOUT_MINUTES_SENDING_MAIL": (
        1440,
        'timeout for phase SENDING_MAIL',
        int
    ),
    "SCAN_TIMEOUT_MINUTES_SERVER_ERROR": (
        1440,
        'timeout for phase SERVER_ERROR',
        int
    ),

    # other stuff
    'INTERNET_NL_API_USERNAME': (
        'dummy',
        'Username for the internet.nl API. This option is ignored as every account uses their own credentials. Keep '
        'this value set to dummy for legacy reasons.',
        str),
    'INTERNET_NL_API_PASSWORD': (
        '',
        'Username for the internet.nl API. This option is ignored as every account uses their own credentials. Keep '
        'this value set to dummy for legacy reasons.',
        str
    ),
    'INTERNET_NL_MAXIMUM_URLS': (
        1000,
        'The maximum amount of domains per scan, not relevant for dashboard, only for websecmap.',
        int
    ),

    "SCANNER_LOG_PLANNED_SCANS": (
        False,
        "Used when debugging, logs all changes to planned scans to a separate table. Causes millions of records a day",
        bool,
    ),
    "SCANNER_AUTO_PURGE_FINISHED_SCANS": (
        True,
        "Removes the scan record from the planned scan table, which reduces the amount of data stored.",
        bool,
    ),
    "CONNECTIVITY_TEST_DOMAIN": (
        "internet.nl",
        "A server that is reachable over IPv4. This is used by a worker to determine what kind of scans it can do. "
        "Enter an address that you own or manage.",
        str,
    ),
    "IPV6_TEST_DOMAIN": (
        "internet.nl",
        "A server that is reachable over IPv6. This is used by a worker to determine "
        "what kind of scans it can do. Enter an address that you own or manage.",
        str,
    ),
    "INTERNET_NL_ADD_CALCULATED_RESULTS_WEBSECMAP": (
        False,
        "Add calculated results for web security map. This is used only for installations by the "
        "Internet Cleanup Foundation.",
        bool,
    ),
    "INTERNET_NL_ADD_CALCULATED_RESULTS_FORUM_STANDAARDISATIE": (
        False,
        "Add calculated results for forum standaardisatie, the internet.nl dashboard. These calculations are created "
        "on top of the internet.nl metrics. These are used for official publications. You probably do not need these.",
        bool,
    ),
    "INTERNET_NL_ADD_CALCULATED_RESULTS_VNG_V6": (
        False,
        "Add calculated results for VNG, obsoleted IPv6 derived conclusions. No need to enable these and will be "
        "removed in a future release.",
        bool,
    ),
    "INTERNET_NL_WEB_ONLY_TOP_LEVEL": (
        False,
        "Do not send in subdomains. To reduce the number of tests while still getting an impression on a broader scope",
        bool,
    ),

    "SUBDOMAIN_SUGGESTION_ENABLED": (
        False,
        "Do you want subdomain suggestions to become available in the web interface?",
        bool,
    ),
    "SUBDOMAIN_SUGGESTION_SERVER_ADDRESS": (
        os.environ.get("DASHBOARD_SUBDOMAIN_SUGGESTION_SERVER_ADDRESS", "http://localhost:8001/"),
        "Server address of the suggestions API. To run this API, go to: "
        "https://github.com/internetstandards/Internet.nl-ct-log-subdomain-suggestions-api",
        str,
    ),
    "SUBDOMAIN_SUGGESTION_DEFAULT_TIME_PERIOD": (
        120,
        "The amount of days the domain has to be last seen",
        int,
    ),
    "SUBDOMAIN_SUGGESTION_DEFAULT_EXTEND_TIME_PERIOD": (
        90,
        "The amount of days to extend the range to search for available subdomains",
        int,
    ),
}

CONSTANCE_CONFIG_FIELDSETS = OrderedDict(
    [
        (
            'General Dashboard Settings', (
                'DASHBOARD_FRONTEND_URL',
                'DASHBOARD_MAXIMUM_DOMAINS_PER_LIST',
                'DASHBOARD_MAXIMUM_DOMAINS_PER_SPREADSHEET',
                'DASHBOARD_MAXIMUM_LISTS_PER_SPREADSHEET',
                'DASHBOARD_FRONT_PAGE_URL_LISTS'
            )
        ),

        (
            'Internet.nl Scan Settings', (
                'SCAN_AT_ALL',
                'INTERNET_NL_API_URL',
                "INTERNET_NL_SCAN_TRACKING_NAME",
                "SCANNER_NAMESERVERS",
                "CREDENTIAL_CHECK_URL",
            )
        ),

        (
            'E-Mail Settings', (
                'EMAIL_NOTIFICATION_SENDER',
                'EMAIL_FALLBACK_LANGUAGE',
                'EMAIL_TEST_RECIPIENT',
                'EMAIL_DASHBOARD_ADDRESS',
            ),
        ),

        (
            "Security.txt", (
                "SECURITY_TXT_IS_REDIRECTED",
                "SECURITY_TXT_REDIRECT_URL",
                "SECURITY_TXT_CONTENT"
            )
        ),

        (
            "Subdomain suggestions", (
                "SUBDOMAIN_SUGGESTION_ENABLED",
                "SUBDOMAIN_SUGGESTION_SERVER_ADDRESS",
                "SUBDOMAIN_SUGGESTION_DEFAULT_TIME_PERIOD",
                "SUBDOMAIN_SUGGESTION_DEFAULT_EXTEND_TIME_PERIOD"
            )
        ),

        (
            'Signup Settings (internet.nl only)', (
                'SHOW_SIGNUP_FORM',
                'EMAIL_NOTIFICATION_SENDER_FOR_SIGNUP',
                'DASHBOARD_SIGNUP_NOTIFICATION_EMAIL_ADRESSES'
            )
        ),

        (
            "Timeouts (advanced)", (
                'SCAN_TIMEOUT_MINUTES_DISCOVERING_ENDPOINTS',
                'SCAN_TIMEOUT_MINUTES_RETRIEVING_SCANABLE_URLS',
                'SCAN_TIMEOUT_MINUTES_REGISTERING_SCAN_AT_INTERNET_NL',
                'SCAN_TIMEOUT_MINUTES_IMPORTING_SCAN_RESULTS',
                'SCAN_TIMEOUT_MINUTES_CREATING_REPORT',
                'SCAN_TIMEOUT_MINUTES_SENDING_MAIL',
                'SCAN_TIMEOUT_MINUTES_SERVER_ERROR',
            )
        ),

        (
            "Logging settings (advanced)", (
                "SCANNER_LOG_PLANNED_SCANS",
                "SCANNER_AUTO_PURGE_FINISHED_SCANS",
            )
        ),

        (
            "Unused / Expert settings", (
                'INTERNET_NL_API_USERNAME',
                'INTERNET_NL_API_PASSWORD',
                'INTERNET_NL_MAXIMUM_URLS',
                "INTERNET_NL_ADD_CALCULATED_RESULTS_WEBSECMAP",
                "INTERNET_NL_ADD_CALCULATED_RESULTS_FORUM_STANDAARDISATIE",
                "INTERNET_NL_ADD_CALCULATED_RESULTS_VNG_V6",
                "INTERNET_NL_WEB_ONLY_TOP_LEVEL",
                "IPV6_TEST_DOMAIN",
                "CONNECTIVITY_TEST_DOMAIN"
            )
        )
    ]
)
