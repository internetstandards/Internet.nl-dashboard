# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## Version 3 - Email improvements

### Added
- Sends out templated e-mails when a report is finished
- Change report is included in sent e-mail

### Changed
- The UI and django services are now in separate repositories for quicker builds and faster development
- Bugfix on crashing scans from the api.
- Bugfixes on non-progressing scans.
- Bugfixes on crashes with workers.
- Hamburger menu fixes
- The project is now on Python 3.8
- Dependencies have been upgraded

### Removed
Support for Python < 3.8

##API 2.0 Version - 2020-05-??

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

[Second Version]: https://github.com/internetstandards/Internet.nl-dashboard/milestone/2?closed=1
[First Version]: https://github.com/internetstandards/Internet.nl-dashboard/milestone/1?closed=1
