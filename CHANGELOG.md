# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## V4.2.0 - 17 April 2023

### Added
- Editing of domain lists via spreadsheets (uploading and downloading spreadsheet files)
- Tag/label support in spreadsheet uploads and downloads
- Be able to automatically share the latest report of a list
- Signup form for easier onboarding
- Support for automatically sharing of sharing specific reports on the front page

### Changed
- www subdomain discovery has been replaced with crt.sh subdomain discovery
- Support for Django 4.2, with psql12
- Minimum python version is now 3.10


## V4.1.0 - 7 February 2023

### Added
- RPKI and Security.txt metrics

### Changed
- Small Changes
 - Added github action for building and testing, removing travis
 - Upgraded dependencies
 - Added tag normalization


- Bugfixes
 - The credential check url of the internet.nl api instance can now be configured (#396)
 - Some labels have been corrected
 - Removed CSRF from public reports
 - Previous report now always selects the same report type



## [Fourth Version] - 2021 Oct 29

### Added
- Home: New homepage with a public report list
- Tour: Updated tour screenshots, added lightbox and translated it to Dutch
- Domains: Tag / label support for domains in a list: allows filtering reports on (multiple) tags
- Domains: A tool to automatically discover and add www subdomains to a domain list
- Domains: Filtering on the domain list
- Domains: Start a web and mail scan from the same list: no need to keep two separate lists

- Reports: Report sharing: share a report under a public url, with optional password  
- Reports: Expert feature: allow report times to be shifted to include newer (rescanned) metrics
- Reports: Doughnut charts with a percentage in the middle
  
- Profile: A new profile page with notification settings and metric settings

### Changed
- Small changes
  - The menu has been re-written to reduce code complexity
  - Icons have been added everywhere
  - The UI has been streamlined in many areas: less clutter, less lines
  - The scan monitor looks nicer, with color inidication when scans are finished
  - Username is now visible in the menu for admins / impersonating users
  - Add SPDX licence info
  - Extra fields now have a calculated category conclusion
  - Option to use EU resolvers for prechecks (#250)
  - Updated javascript + python dependencies
  
- Bugfixes
  - Speed up domain list and scan monitor queries
  - Fix possible CSRF issue, using axios
  - Add stricter QA for python, squashing a few potential bugs
  - Textual issues
  - Bulk uploads in excel with https:// or pages in an url now work
  - Correct graph average when extra fields are disabled
  - Lists that are not planned to scan now don't show a date far in the future
  - Update TLS ciphers on the server
  - Update CSP header
  - E-mail sending domain is now in the excel export, non-sending domain has been removed
  - Report page does not reload every 5 minutes anymore


## [Third Version] - 2020 Nov 20

### Added
- Notification e-mails
    - When a scan is finished, a mail is sent to your account (set up details under Account)
    - A second scan on the same list will create a notification mail which includes a comprehensive change report
    - Management of notification in Account settings, unsubscription via a direct link
- Statistics on how the dashboard is used (for project managers only)

### Changed
- Small changes
    - Domain-list manager will show how many duplicates have been removed when adding domains
    - Scan monitor now has progress bars
    - Report selection is more user friendly
    - Report timeline now shows what report is being viewed (report number is on the timeline)
    - Reports allow to compare scores
    - Overall translations have been improved
    - Overall notifications now come with an additional toast notification
    - Overall notification now contain date and time information
    - Overall nicer UI, better response times
    - Admin features such as changing account and adding users have been slightly improved

- Bugfixes
    - Scans got stuck in a loop under rare situations, both the rare situation and the loop have been fixed
    - Scans can now finish if the API returns no data for certain domain ({'example.com': 'error'})
    - Overall accordions will not alter the navigation state (Command+R or CTRL-F5 now works after clicking them)
    - Overall hamburger menu works on mobile
    - Overall header of website will be hidden when scrolling
    - Report table headers now render correctly in Safari
    - Reports will now not contain the X-XSS-Protection field

- Architecture
    - Separation of the UI and the Django code, UI is now in a separate repository
    - Split complex components in various sub-components for easier understanding, logic and development
    - Application of BootstrapVue components, scoped styling (mostly)
    - Application of NPM builds, BootstrapVue
    - Removal of jQuery, lodash and moment.js (moment is still used by charts.js)
    - Application of tree shaking syntax for BootstrapVue
    - Application of vue-18n translations blocks, translations can be maintained with Babeledit

### Removed
- Support for Python < 3.8

##API 2.0 Version - 2020-05-20

### Added
- Works with API 2.0, which has more direct results, as well as technical details and translation keys which allows new features in the future
- Various bugfixes, mainly in the report table

## [Second Version] - 2020-01-30
Version 2 solves over 40 issues on our GitHub tracker. The most noteworthy are addressed in this log:

### Added
- Comparison of individual metrics between the current report and a second report. An arrow indicates an improved or deteriorated metric.
- The report timeline is now able to show multiple reports.
- Printing support for reports, including a better header and page layout.
- Sorting of columns in the report table.
- Possibility to stop a running scan (see scan progress in the scan monitor).
- Indication of changes between domains in the report and domains in the list.

### Changed
- Major speed improvements in navigation due to using a Vue Single Page Application.
- Major speed improvements in showing reports due to less data in the report, pre-calculations and rendering optimizations.
- Ability to start a scan after the previous one has ended (no 24 hour cooldown anymore).
- Easier, more robust and faster adding of domains.
- Revamped scanning process, which gives better insight into the state of the scan.
- Revamped report settings section.
- New colors and patterns in the report.
- Moved javascript management to NPM.
- Improved navigation in the admin interface.

### Removed
- "Perform scans" in Domain List settings.


## [First Version] - 2020-09-20
This first version was built before issues where logged in GitHub. The first version brought these major features:

### Added
- Ability to manage domains in lists and perform scans on those lists
- Ability to view running scans
- Ability to view reports with the results of the scan
- Ability to import domains using spreadsheets and a web interface
- Report with charts per metric-type and a table per individual metric
- Export findings to Excel
- Ability to filter what metrics are visible in the report
- Power tools for admins (quickly adding existing API accounts and impersonation)
- Ability to use second factor authentication

[Third Version]: https://github.com/internetstandards/Internet.nl-dashboard/milestone/4?closed=1
[Second Version]: https://github.com/internetstandards/Internet.nl-dashboard/milestone/2?closed=1
[First Version]: https://github.com/internetstandards/Internet.nl-dashboard/milestone/1?closed=1
