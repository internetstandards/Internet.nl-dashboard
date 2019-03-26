{% verbatim %}
<template type="x-template" id="scan_monitor_template">
    <div>
        <h3>{{ $t("upload.recent_uploads.title") }}</h3>
        <p>{{ $t("upload.recent_uploads.intro") }}</p>
        <table v-if="scans">
            <thead>
                <tr>
                    <th>{{ $t("upload.recent_uploads.date") }}</th>
                    <th>{{ $t("upload.recent_uploads.filename") }}</th>
                    <th>{{ $t("upload.recent_uploads.filesize") }}</th>
                    <th>{{ $t("upload.recent_uploads.status") }}</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="scan in scans">
                    <td width="10%">{{ scan.id }}</td>
                    <td width="15%"><span :title="scan.started_on">{{ humanize_date(scan.started_on) }}</span></td>
                    <td width="15%"><span :title="scan.finished_on">{{ humanize_date(scan.finished_on) }}</span></td>
                    <td>{{ scan.message }}</td>
                </tr>
            </tbody>
        </table>
        <span v-if="!scans.length">{{ $t("upload.recent_uploads.no_uploads") }}</span>
    </div>
</template>
{% endverbatim %}

<script>

const messages = {
    en: {
        upload: {
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

vueUpload = new Vue({
    i18n,
    name: 'scan_monitor',
    el: '#scan_monitor',
    template: '#scan_monitor_template',
    mixins: [humanize_mixin],
    data: {
        scans: [],
    },
    mounted: function () {
        this.load();
    },
    methods: {
        load: function() {
            this.get_recent_uploads();
        },
        get_recent_uploads: function(){
            fetch(`/data/scan-monitor/`).then(response => response.json()).then(data => {
                this.scans = data;
            }).catch((fail) => {console.log('A loading error occurred: ' + fail);});
        },
    }
});
</script>
