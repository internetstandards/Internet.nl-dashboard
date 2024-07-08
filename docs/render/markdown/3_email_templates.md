# Email Templates

The dashboard can send out mail when scans are finished.
An email is composed using a template. These templates are rich in functionality, and can
be adjusted without the need of re-building and re-deploying this software.

## General information

### Where can i find templates

Templates are located at /admin/django_mail_admin/emailtemplate/ on your installation.
They are part of the admin system and require the right permissions to be edited.
An admin can edit them easily.

### What templates are available

Currently there is one feature that uses an e-mail template, which is scan_finished.
When a scan is finished, this mail template is used to draft a mail.

The scan finished template uses two sub-templates, which are:

- scan_finished
- - detailed_comparison_regression
- - detailed_comparison_improvement

The sub templates are tables that list regressions and improvements.

### How do i define templates in multiple languages

Templates are postfixed with a language identifier. The default is ‘_en’, for English.
The dashboard currently supports two languages, Dutch and English: nl and en.

If a template for \_nl (or any other language) is missing, it will use \_en.

(Technically there are many solutions to make sure translations are multilingual, most of which
require re-compilation or maintenance of external translation files that require a build. When
there are many languages in use, there will be a need to switch.)

### What template system is used

The Django template system is used, with one exception: all fields from the dashboard are strings.

The Django template system is a mix of special tags and HTML, Javascript and CSS. It is also
used in building front end systems which are rendered on the server side.

The Django Template system is documented here:
[https://docs.djangoproject.com/en/3.1/ref/templates/language/](https://docs.djangoproject.com/en/3.1/ref/templates/language/)

### What do i need to watch out for

Syntax mistakes can prevent a mail from being composed or sent. In this case the software will crash.
This is the largest drawback of the current approach. When editing a template, be careful.

### What are the pros and cons of the current approach

Pros:

- No need to recompile / rebuild / deliver the software when templates change
- Multi language in a simple and straightforward way (allowing changes per language)
- Uses well documented systems of django, html, javascript and css.

Cons:

- No syntax highlighting or checking of templates in the editor, use an external editor(!)
- A template per language is annoying when doing maintenance

### How to set up e-mail sending

Email sending uses Django Mail Admin: [https://github.com/Bearle/django_mail_admin/](https://github.com/Bearle/django_mail_admin/)

You need to configure an outbox with proper values. You can test if this works via the command line
: with the command:
  <br/>
  ```default
  dashboard send_testmail
  ```

## Scan Finished mail

### When is this mail sent

This mail is only sent when the user has set that in their profile. You can review that for example here:
/admin/auth/user/1/change/

The fields that are used to send this mail are:

- Mail preferred mail address: an e-mail address
- Mail preferred language: a language from the list (only supporting NL or EN)
- Mail send mail after scan finished: a boolean value if the mail can be sent
- Mail after mail unsubscribe code: automatically generated

If all preconditions are correct, a mail will be queued as part of the scanning process, just before the
scan is finished.

### How to test this mail

A test mail can be sent at will on the admin page of AccountInternetNLScan, here:
/admin/internet_nl_dashboard/accountinternetnlscan/

A mail can only be sent if a scan is finished and the mail preconditions and setup are correct.

When this mail has been queued, either wait for the periodic task that sends mail is performed (once a minute),
or perform this via the command line (during development):

```default
dashboard send_queued_mail --processes=1 --log-level=2
```

### scan_finished tags

- {{unsubscribe_code}}

Allows an unsubscribe from a specific feed of mails. This code can be used without a login. The
url this code is used for is for example:

```default
{{dashboard_address}}/spa/#/unsubscribe?feed=scan_finished&unsubscribe_code={{unsubscribe_code}}
```

- {{recipient}}

The recipient of the email, which is, in order of fallback A) the first name, B) the last name, C) the username.

- {{user_id}}

The id of a user, which might be useful at some point.

- {{list_name}}

The name of the domain list that is being scanned.

- {{report_id}}

The mail is about a report. Using this number a link can be built to the report. For example:

```default
{{dashboard_address}}/spa/#/report/{{report_id}}
```

- {{report_average_internet_nl_score}}

The average score in the report.

- {{report_number_of_urls}}

The total number of urls in this report.

- {{scan_id}}

The number of the scan performed, which might be useful for context and tracking purposes.

- {{scan_started_on}}

The date and time when the scan started, in ISO format.

- {{scan_finished_on}}

An approximation of when the scan is finished. This mail is sent as part of the scanning process, which
is thus not yet finished. It might be off by a minute or two. This is also in ISO format.

- {{scan_duration}}

Number of seconds it took to complete a scan. Also an approximation.

- {{scan_type}}

Either web or mail. Can be used in sentences like:

```default
The {{scan_type}} scan on {{list_name}} is finished.
```

- {{previous_report_available}}

If there is a previous report for this list. The value will be “True” if that is the case. Otherwise it will
be “False”. Note that this is a string value, not a boolean value.

- {{previous_report_average_internet_nl_score}}

The average score of the previous report. This is used for easy overall comparison.

- {{compared_report_id}}

The id of the previous report, can be used to build a link with a comparison, such as:

```default
{{dashboard_address}}/spa/#/report/{{report_id}}/{{compared_report_id}}
```

- {{comparison_is_empty}}

A string boolean containing either “True” or “False”. The comparison is empty when all values
compared to the previous and current report are the same. There has been no change, at all.

If the comparison is empty, there is no need to show any details of course.

- {{improvement}}

The number of improvements made in the current report, compared to the last report.

- {{regression}}

The number of regressions in the current report, compared to the last report.

- {{neutral}}

The number of neutral values in the current report, compared to the last report.
Neutral is either unchanged, or a comparison against an error, not-testable or other hard to compare value.

- {{comparison_report_available}}

A simple value to check if a comparison is available. Can be used to enable or disable sections of the email.

- {{comparison_report_contains_improvement}}

Set to “True” if there are improvements in the comparsion. There might be only improvements and no regressions and
vice versa.

- {{comparison_report_contains_regression}}

Set to “True” if there are regressions available.

- {{days_between_current_and_previous_report}}

The number of days between the current and previous report.

- {{comparison_table_improvement}}

This is a rendered section of html, based on the detailed_comparison_improvement(_en) template. To
use pre-rendered html, use the following in your e-mail, using the word “safe”:

{{comparison_table_improvement|safe}}

- {{comparison_table_regression}}

See comparison_table_improvement.

- {{domains_exclusive_in_current_report}}

A comma separated string of domains that are available in the current report, but not in the previous report.
These are new domains that have been added to the list, usually. There are also edge cases where the
domain could not be scanned last time, but it could this time.

- {{domains_exclusive_in_other_report}}

A comma separated string of domains that are only available in the previous report. Probably those domains
have been deleted from the list of domains during the new scan.

- {{dashboard_address}}

The web address of the dashboard. This is configured in the settings at: /admin/constance/config/

### Example template

scan_finished_en takes into account a multitude of situations where there are no scan results.

This template will probably be quickly outdated, but shows how to build a nice template with the fields above.

```default
Hi {{recipient}},<br>
<br>
The {{scan_type}} scan on '{{list_name}}' has finished and your report is ready. The average internet.nl score in this report is {{report_average_internet_nl_score}}%. <br>
<br>
View the report at this link: <br>
<a href="{{dashboard_address}}/spa/#/report/{{report_id}}">
        {{dashboard_address}}/spa/#/report/{{report_id}}/</a><br>


{% if previous_report_available == "False" %}
<br>
This is the first report for '{{list_name}}'. The next time this list is scanned, a comparison report will be included in this mail.
{% endif %}

{% if previous_report_available == "True" and comparison_is_empty == "True" %}
<br>
A previous report, #{{compared_report_id}}, is available but contains no changes compared to this report. Therefore no change summary was included.
{% endif %}


{% if previous_report_available == "True" and comparison_is_empty == "False" %}
<br>
<h3>Changes compared to previous report</h3>
Below a summary is given compared to the previous report, #{{compared_report_id}}. The previous report was made {{days_between_current_and_previous_report}} days ago and had an average score of {{previous_report_average_internet_nl_score}}%.<br>
<br>
You can view the comparison in detail on the dashboard at <a href="{{dashboard_address}}/spa/#/report/{{report_id}}/{{compared_report_id}}">{{dashboard_address}}/spa/#/report/{{report_id}}/{{compared_report_id}}</a><br>
<br>
<h4>Summary of changes:</h4>
<table>
    <tr style='font-weight: bold; text-align: center;'>
        <td>{{improvement}}</td><td>{{regression}}</td><td>{{neutral}}</td>
    </tr>
    <tr>
        <td>Improvements</td><td>Regressions</td><td>Neutral</td>
    </tr>
</table>
{% endif %}


{% if previous_report_available == "True" and comparison_report_contains_improvement != "True" and comparison_report_contains_regression != "True" %}
<br>
Only neutral changes have been observed, therefore no detailed overview of changes is included in this e-mail.<br>
{% endif %}

{% if comparison_report_contains_improvement == "True" or comparison_report_contains_regression == "True" %}
{% if comparison_report_contains_improvement == "True" %}
<br>
<h4>Overview of improvements:</h4>
<table style="">
    <tr>
        <th>Domain</th>
        <th>Score</th>
        <th>Improvement(s)</th>
        <th>Metrics improved</th>
    </tr>
    {{comparison_table_improvement|safe}}
</table>
{% endif %}

{% if comparison_report_contains_regression == "True" %}
<br>
<h4>Overview of regressions:</h4>
<table>
    <tr>
        <th>Domain</th>
        <th>Score</th>
        <th>Regeression(s)</th>
        <th>Metrics regressed</th>
    </tr>
    {{comparison_table_regression|safe}}
</table>
{% endif %}

{% endif %}

{% if domains_exclusive_in_current_report != "" %}
<br>
This report includes new domains, which are not included because they could not be compared: {{ domains_exclusive_in_current_report}}.
{% endif %}

{% if domains_exclusive_in_other_report != "" %}
<br>
The following domains have disappeared in the new report, and are thus not included above: {{ domains_exclusive_in_other_report}}.
{% endif %}

<br>
Regards,<br>
The internet.nl dashboard<br>
<br>
[
<a href="{{dashboard_address}}/spa/#/unsubscribe?feed=scan_finished&unsubscribe_code={{unsubscribe_code}}">unsubscribe</a>
-
<a href="{{dashboard_address}}/spa/#/account">preferences</a>
 ]

<style>
table th, table td{
        padding: 5px;
}
</style>
```

detailed_comparison_regression_en:

```default
{% for record in data %}
<tr style='background-color: {% cycle 'rgba(0,0,0,.05)' 'inherit' %};'>
    <td style="vertical-align: baseline">
        {{ record.url }}
    </td>
    <td style="vertical-align: baseline">
        <a href="{{ record.new.report }}" target="_blank">
            <img src="https://dashboard.internet.nl/static/images/vendor/internet_nl/favicon.png" style="height: 16px;">
            {{ record.new.score }}%
        </a>
    </td>
    <td style="vertical-align: baseline">
        {{ record.changes.regression }}
    </td>
    <td>
        <ul>
        {% for metric in record.changes.regressed_metrics %}
            <li>{{ metric }}</li>
        {% endfor %}
        </ul>
    </td>
</tr>
{% endfor %}
```

detailed_comparison_improvement_en:

```default
{% for record in data %}
<tr style='background-color: {% cycle 'rgba(0,0,0,.05)' 'inherit' %};'>
    <td style="vertical-align: baseline">{{ record.url }}</td>
    <td style="vertical-align: baseline">
        <a href="{{ record.new.report }}" target="_blank">
            <img src="https://dashboard.internet.nl/static/images/vendor/internet_nl/favicon.png" style="height: 16px;">
            {{ record.new.score }}%
        </a>
    </td>
    <td style="vertical-align: baseline">
        {{ record.changes.improvement }}
    </td>
    <td>
        <ul>
        {% for metric in record.changes.improved_metrics %}
            <li>{{ metric }}</li>
        {% endfor %}
        </ul>
    </td>
</tr>
{% endfor %}
```

PageBreak
