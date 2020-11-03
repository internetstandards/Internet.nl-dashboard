<style>
    figure img {
        border: thin silver solid;
    }
    figcaption {
        text-align: left !important;
        font-style: italic !important;
        font-size: smaller !important;
        color: dimgray;
    }
    figure {

        text-indent: 0;
        border: thin #05BFD6 solid;
        margin: 0.5em;
        padding: 0.5em;
    }

    img.scaled {
      width: 100%;
    }
</style>

<template>
    <div id="demo-template">
        <div class="block fullwidth">
            <h1>{{ $t("title") }}</h1>
            <p v-html="$t('introduction')"></p>
            <p>{{ $t("contact_information") }}<a href='mailto:vraag@internet.nl@subject=dashboard%20access%20request'>vraag@internet.nl</a></p>
        </div>

        <div class="block fullwidth">
            <h2>{{ $t("feature.create_list.title") }}</h2>
            <p>{{ $t("feature.create_list.introduction") }}</p>

            <figure>
              <img src="/static/images/demo/domain_list.png" class="scaled" alt="example list">
              <figcaption>{{ $t("feature.create_list.caption") }}</figcaption>
            </figure>
        </div>

        <div class="block fullwidth">
            <h2>{{ $t("feature.create_list.upload_title") }}</h2>
            <p>{{ $t("feature.create_list.spreadsheet_upload") }}</p>

            <table>
                <tr>
                    <td style="vertical-align: top; text-align: left">
                        <figure>
                          <img src="/static/images/demo/text_upload.png" class="scaled" alt="example list">
                          <figcaption>{{ $t("feature.create_list.text_upload_caption") }}</figcaption>
                        </figure>
                    </td>
                    <td style="vertical-align: top; text-align: left">
                        <figure>
                          <img src="/static/images/demo/spreadsheet_upload.png" class="scaled" alt="example list">
                          <figcaption>{{ $t("feature.create_list.spreadsheet_upload_caption") }}</figcaption>
                        </figure>
                    </td>
                </tr>
            </table>
        </div>

        <div class="block fullwidth">
            <h2>{{ $t("feature.scan_monitor.title") }}</h2>
            <p>{{ $t("feature.scan_monitor.introduction") }}</p>

            <figure>
              <img src="/static/images/demo/scan_progress.png" class="scaled" alt="example list">
              <figcaption>{{ $t("feature.scan_monitor.caption") }}</figcaption>
            </figure>
        </div>

        <div class="block fullwidth">
            <h2>{{ $t("feature.reporting.title") }}</h2>
            <p>{{ $t("feature.reporting.introduction") }}</p>

            <p>{{ $t("feature.reporting.configuration") }}</p>
            <figure>
              <img src="/static/images/demo/report_configuration.png" class="scaled" alt="example list">
              <figcaption>{{ $t("feature.reporting.caption_configuration") }}</figcaption>
            </figure>
        </div>

        <div class="block fullwidth">
            <h2>{{ $t("feature.timeline.title") }}</h2>
            <p>{{ $t("feature.timeline.introduction") }}</p>
            <figure>
              <img src="/static/images/demo/graph_timeline.png" class="scaled" alt="example list">
              <figcaption>{{ $t("feature.timeline.caption") }}</figcaption>
            </figure>
        </div>

        <div class="block fullwidth">
            <h2>{{ $t("feature.bar_charts.title") }}</h2>
            <p>{{ $t("feature.bar_charts.introduction") }}</p>
            <figure>
              <img src="/static/images/demo/bar_chart.png" class="scaled" alt="example list">
              <figcaption>{{ $t("feature.bar_charts.caption") }}</figcaption>
            </figure>
        </div>

        <div class="block fullwidth">
            <h2>{{ $t("feature.table.title") }}</h2>
            <p>{{ $t("feature.table.introduction") }}</p>
            <figure>
              <img src="/static/images/demo/result_table.png" class="scaled" alt="example list">
              <figcaption>{{ $t("feature.table.caption") }}</figcaption>
            </figure>
        </div>

        <div class="block fullwidth">
            <h2>{{ $t("feature.spreadsheet.title") }}</h2>
            <p>{{ $t("feature.spreadsheet.introduction") }}</p>
            <figure>
              <img src="/static/images/demo/spreadsheet.png" class="scaled" alt="example list">
              <figcaption>{{ $t("feature.spreadsheet.caption") }}</figcaption>
            </figure>
        </div>

        <div class="block fullwidth">
            <h2>{{ $t("contact.title") }}</h2>
            <p v-html='$t("contact_information")'></p>
        </div>

    </div>
</template>

<script>
export default {
}
</script>
<i18n>
{
    "en": {
        "title": "Internet.nl Dashboard Tour",
        "introduction": "The internet.nl allows bulk scans and reporting up to thousands of domains. Scan for IPv6, TLS, DMARC, SPF, DANE, DKIM, DNSSEC, HTTP Headers and more. Below is an overview of features included in the dashboard:",
        "contact_information": "To use the dashboard on internet.nl, contact: ",
        "feature": {
            "create_list": {
                "title": "Bulk domain scans for web and mail",
                "introduction": "Many domains can be stored in lists. These lists are configured to perform either the web or mail scan.",
                "spreadsheet_upload": "Importing your domains is easy with either text import or spreadsheet uploads.",
                "caption": "This image shows the 'Internet.nl Public Web Demo' list. It contains just five domains. The list has options for configuration, adding domains, direct scanning, scheduled scanning, exporting to csv and of course deletion.",
                "upload_title": "Upload domains via text or spreadsheet",
                "text_upload_caption": "Using text, a large number of domains can quickly be added.",
                "spreadsheet_upload_caption": "It's also possible to upload Excel, ODS and CSV files domains. Examples are available on the upload page."
            },
            "scan_monitor": {
                "title": "Monitor scans",
                "introduction": "Scans can be performed simultaneously. The scan monitor shows the progress of each scan and allows for cancelling scans.",
                "caption": "The image shows several scans, of which one is still running. Our demo scan is finished and a report is ready."
            },
            "reporting": {
                "title": "Configurable reports",
                "introduction": "The report is printer friendly and contains several graphs and a result table. It's even possible to download the report as a spreadsheet.",
                "configuration": "The report is customizable to only show what your organization focuses on.",
                "caption_configuration": "All IPv6 metrics are now visible in the report. Enable or disable the entire group with one click and even include an average.",
                "graphs": "Several charts are auto-generated, showing compliance to modern standards in an instance."
            },
            "timeline": {
                "title": "Track progress over time",
                "introduction": "Every time a list is scanned, the data in the timeline grows. The timeline allow comparing multiple lists over time, showing multiple lines.",
                "caption": "The timeline shows the average internet.nl score every time the same list is scanned. This helps keeping track of overall progress."
            },
            "bar_charts": {
                "title": "Bar charts",
                "introduction": "These bar are more versatile than meets the eye. It's possible to compare reports (up to five) and they are available for every category and subcategory (such as IPv6, DNSSEC, TLS).",
                "caption": "In this demo of course everybody has a 100% score, which is obvious. This image shows 6 bars with 100% score."
            },
            "table": {
                "title": "Table view, with comparison",
                "introduction": "Of course all results are visible in a table. The table is split into several categories and only shows the information that is needed. The table has a power feature: it's possible to compare data with a second report and see improvements/declines for all domains that are in both reports.",
                "caption": "The IPv6 results show that everything is correct. It's possible to filter domains and view the complete report on internet.nl. Of course sorting of results is included."
            },
            "spreadsheet": {
                "title": "Spreadsheet exports",
                "introduction": "The table can be exported to Excel, Libreoffice and CSV data. The Excel spreadsheet includes some statistics over the presented metrics.",
                "caption": "The Excel spreadsheet is opened in Numbers. It contains the same data as presented in the table."
            }

        },
        "contact": {
            "title": "Contact for access"
        }
    },
    "nl": {

    }
}

</i18n>