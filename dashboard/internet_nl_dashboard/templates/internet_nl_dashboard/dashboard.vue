{% verbatim %}
<style>
/* https://css-tricks.com/rotated-table-column-headers/*/
    th.rotate {
  /* Something you can count on */
  height: 100px;
  white-space: nowrap;
}

th.rotate > div {
  transform:
    /* Magic Numbers */
    translate(15px, 62px)
    /* 45 is really 360 - 45 */
    rotate(315deg);
  width: 30px;
}
th.rotate > div > span {
    border-bottom: 1px solid #ccc;
    padding: 5px 10px;
}
</style>
<template type="x-template" id="report_template">
    <div>
        <h2>Select Report</h2>
        <v-select v-model="selected_report" :options="available_recent_reports"></v-select>
        <h2>Report</h2>

        <h2>Categories</h2>
        <span v-if="selected_category" @click="select_category('')">Remove filter: {{selected_category}}</span>
        <span v-if="!selected_category">&nbsp;</span>
        <div v-for="report in reports">
            <table>
                <tr>
                    <th style="width: 300px">&nbsp;</th>
                    <th class="rotate" v-for="rating in report.calculation.urls[0].endpoints[0].ratings" v-if="report.calculation.urls[0].endpoints.length && is_relevant_for_category(rating.type)">
                        <div @click="select_category(rating.type)"><span>{{rating.type}}</span></div>
                    </th>
                </tr>

                <tr v-for="url in report.calculation.urls" v-if="url.endpoints.length">
                    <td >{{url.url}}</td>
                    <td v-for="rating in url.endpoints[0].ratings" v-if="is_relevant_for_category(rating.type)">
                        <span v-if="rating.ok < 1">❌</span>
                        <span v-if="rating.ok > 0">✅</span>
                    </td>
                </tr>
            </table>
        </div>

    </div>
</template>
{% endverbatim %}

<script>

const messages = {
    en: {
        upload: {
            bulk_data_uploader: {
                title: 'Bulk Address Uploader',
                introduction: 'It\'s possible to upload large amounts of internet addresses and lists using spreadsheets. To do so,\n' +
                    '            please expand on the example spreadsheets listed below. This shows how the data has to be structured.\n' +
                    '            Examples with and without data are provided as Open Document Spreadsheet, Microsoft Office Excel and Comma Separated.',
            },
            empty_file: 'Empty file',
            file_with_example_data: 'File with example data',
            open_document_spreadsheet: 'Open Document Spreadsheet (Libre Office)',
            microsoft_office_excel: 'Excel Spreadsheet (Microsoft Office)',
            comma_separated: 'Comma Separated (for programmers)',

            drag_and_drop_uploader: {
                title: 'Drag and drop uploader',
                first_instruction: 'To upload a bulk address file, drag it onto the \'upload\' rectangle below.',
                nomouse: 'A more conventional upload option is available below the drag and drop uploader.',
                process: 'Uploading happens in two stages.\n' +
                    '        First the progress bar is filled, this means the data is sent to this website successfully. Then\n' +
                    '        some processing happens on the server. When this processing is finished, the uploaded file icon below\n' +
                    '        will change to either Success (green, with a checkmark) or Failed (red, with a cross).',
                details_after_upload: 'Details on the status of the uploaded file can be seen afterwards in the \'recent uploads\' section below\n' +
                    '        this uploader.',
                warnings: 'Important: It\'s possible to upload up until 10000 urls in 200 categories per upload. The more\n' +
                    '        is uploaded, the more time it will take. Please wait until the upload is confirmed.',
                fallback_select_a_file: 'Select a file to upload:',
            },

            recent_uploads: {
                title: 'Recent uploads',
                intro: 'This list shows your recent uploads. The status messages give an impression of what has been ' +
                    'created or added. If something went wrong, the status contains hints on what to do next.' +
                    'if your upload was not successful',
                date: 'Date',
                filename: 'Filename',
                filesize: 'Size',
                status: 'Status',
                no_uploads: 'No files uploaded.',
            }
        }
    },
    nl: {
        upload: {
            bulk_data_uploader: {
                title: 'Bulk Address Uploader',
                introduction: 'Hiermee is het mogelijk om grote hoeveelheden internet adressen en lijsten toe ' +
                    'te voegen. Dit gebeurd met spreadsheets. Begin met het downloaden van de voorbeelden hieronder, ' +
                    'deze geven aan wat het juiste formaat is. De voorbeeldbestanden zijn te downloaden in het ' +
                    'Open Document formaat, Microsoft Office formaat en Kommagescheiden.',
            },
            empty_file: 'Leeg bestand',
            file_with_example_data: 'Bestand met voorbeelddata',
            open_document_spreadsheet: 'Open Document Werkblad (Libre Office)',
            microsoft_office_excel: 'Excel Werkblad (Microsoft Office)',
            comma_separated: 'Kommagescheiden (voor programmeurs)',

            drag_and_drop_uploader: {
                title: 'Drag and drop uploader',
                first_instruction: 'Sleep het gewenste bestand in de \'upload\' rechthoek hieronder.',
                nomouse: 'Een meer gebruikelijke upload methode is beschikbaar onder het drag and drop gedeelte.',
                process: 'Het uploaden gebeurd in twee fasen. In de eerste fase wordt de voortgangsbalk gevuld. Als ' +
                    'deze vol is, is het bestand naar de server gestuurd. Dan is de upload nog niet compleet: de gegevens ' +
                    'worden nu verwerkt. Op het moment dat de gegevens verwerkt zijn verschijnt dit als een groen vinkje of' +
                    'rood kruis op het bestand.',
                details_after_upload: 'Details over de status van de upload kunnen naderhand worden bekeken ' +
                    'in het \'recente uploads\' onderdeel onder het upload veld.',
                warnings: 'Let op: Het is mogelijk om tot 10.000 adressen en 200 categorien te sturen per keer. Hoe meer' +
                    ' gegevens, hoe langer het kan duren voordat de upload volledig is. Wees geduldig en wacht tot de upload afgerond is.',
                fallback_select_a_file: 'Selecteer een bestand om te uploaden:',
            },

            recent_uploads: {
                title: 'Recent geupload',
                intro: 'Deze lijst geeft de meest recente uploads weer. De status berichten geven aan wat er is toegevoegd. ' +
                    'Mocht er iets verkeerd zijn gegaan bij het uploaden, dan is hier advies te vinden over wat te verbeteren.',
                date: 'Datum',
                filename: 'Bestand',
                filesize: 'Grootte',
                status: 'Status (in het Engels)',
                no_uploads: 'Nog geen bestanden geüpload.',
            }
        }
    }
};

const i18n = new VueI18n({
    locale: get_cookie('dashboard_language'),
    fallbackLocale: 'en',
    messages,
});


// todo: order of the fields, and possible sub sub categories
vueReport = new Vue({
    i18n,
    name: 'report',
    el: '#report',
    template: '#report_template',
    mixins: [humanize_mixin],
    data: {
        reports: [],
        categories: {
            'web': [
                'internet_nl_web_tls',
                'internet_nl_web_dnssec',
                'internet_nl_web_ipv6'
            ],
            'mail': [
                'internet_nl_mail_dashboard_tls',
                'internet_nl_mail_dashboard_auth',
                'internet_nl_mail_dashboard_dnssec',
                'internet_nl_mail_dashboard_ipv6'
            ],
            'internet_nl_web_tls': [
                'internet_nl_web_https_cert_domain',
                'internet_nl_web_https_http_redirect',
                'internet_nl_web_https_cert_chain',
                'internet_nl_web_https_tls_version',
                'internet_nl_web_https_tls_clientreneg',
                'internet_nl_web_https_tls_ciphers',
                'internet_nl_web_https_http_available',
                'internet_nl_web_https_dane_exist',
                'internet_nl_web_https_http_compress',
                'internet_nl_web_https_http_hsts',
                'internet_nl_web_https_tls_secreneg',
                'internet_nl_web_https_dane_valid',
                'internet_nl_web_https_cert_pubkey',
                'internet_nl_web_https_cert_sig',
                'internet_nl_web_https_tls_compress',
                'internet_nl_web_https_tls_keyexchange'
            ],
            'internet_nl_web_dnssec': [
                'internet_nl_web_dnssec_valid',
                'internet_nl_web_dnssec_exist'
            ],
            'internet_nl_web_ipv6': [
                'internet_nl_web_ipv6_ws_similar',
                'internet_nl_web_ipv6_ws_address',
                'internet_nl_web_ipv6_ns_reach',
                'internet_nl_web_ipv6_ws_reach',
                'internet_nl_web_ipv6_ns_address'
            ],
            'internet_nl_mail_dashboard_tls': [
                'internet_nl_mail_starttls_cert_domain',
                'internet_nl_mail_starttls_tls_version',
                'internet_nl_mail_starttls_cert_chain',
                'internet_nl_mail_starttls_tls_available',
                'internet_nl_mail_starttls_tls_clientreneg',
                'internet_nl_mail_starttls_tls_ciphers',
                'internet_nl_mail_starttls_dane_valid',
                'internet_nl_mail_starttls_dane_exist',
                'internet_nl_mail_starttls_tls_secreneg',
                'internet_nl_mail_starttls_dane_rollover',
                'internet_nl_mail_starttls_cert_pubkey',
                'internet_nl_mail_starttls_cert_sig',
                'internet_nl_mail_starttls_tls_compress',
                'internet_nl_mail_starttls_tls_keyexchange'

            ],
            'internet_nl_mail_dashboard_auth': [
                'internet_nl_mail_auth_dmarc_policy',
                'internet_nl_mail_auth_dmarc_exist',
                'internet_nl_mail_auth_spf_policy',
                'internet_nl_mail_auth_dkim_exist',
                'internet_nl_mail_auth_spf_exist'
            ],
            'internet_nl_mail_dashboard_dnssec': [
                'internet_nl_mail_dnssec_mailto_exist',
                'internet_nl_mail_dnssec_mailto_valid',
                'internet_nl_mail_dnssec_mx_valid',
                'internet_nl_mail_dnssec_mx_exist'
            ],
            'internet_nl_mail_dashboard_ipv6': [
                'internet_nl_mail_ipv6_mx_address',
                'internet_nl_mail_ipv6_mx_reach',
                'internet_nl_mail_ipv6_ns_reach',
                'internet_nl_mail_ipv6_ns_address'
            ]
        },

        selected_category: '',

        available_recent_reports: [],
        selected_report: 0

    },
    mounted: function(){
        this.get_available_recent_reports();
    },
    methods: {
        load: function(report_id) {
            this.get_report_data(report_id);
        },
        get_report_data: function(report_id){
            fetch(`/data/report/get/${report_id}/`).then(response => response.json()).then(data => {
                this.reports = data;
            }).catch((fail) => {console.log('A loading error occurred: ' + fail);});
        },
        get_available_recent_reports: function(){
            fetch(`/data/report/recent/`).then(response => response.json()).then(data => {
                options = [];
                for(let i = 0; i < data.length; i++){
                    data[i].created_on = this.humanize_date(data[i].created_on);
                    options.push({'value': data[i].id, 'label': `${data[i].id}: ${data[i].list_name} (type: ${data[i].type}, from: ${data[i].created_on})`})
                }
                this.available_recent_reports = options;
            }).catch((fail) => {console.log('A loading error occurred: ' + fail);});
        },
        is_relevant_for_category: function(value){
            if (this.selected_category !== "") {
                if (this.categories[this.selected_category].includes(value)) {
                    return true;
                }
            }
            else
                // If not category has been selected, just return the overarching categories.
                return this.categories['web'].includes(value) || this.categories['mail'].includes(value)
        },

        select_category: function(category_name){

            if (Object.keys(this.categories).includes(category_name))
                this.selected_category = category_name;
            else
                this.selected_category = "";


        },
    },
    watch: {
        selected_report: function () {
            // load selected organization id
            this.load(this.selected_report.value);
        }
    }

});
</script>
