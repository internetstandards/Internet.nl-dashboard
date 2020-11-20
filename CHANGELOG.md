# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


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
