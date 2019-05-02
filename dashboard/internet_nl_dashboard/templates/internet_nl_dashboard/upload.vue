{% verbatim %}
<template type="x-template" id="upload_template">
    <div>
        <h1>{{ $t("upload.bulk_data_uploader.title") }}</h1>
        <p>{{ $t("upload.bulk_data_uploader.introduction") }}</p>
        <table>
            <tr>
                <th></th>
                <th>{{ $t("upload.empty_file") }}</th>
                <th>{{ $t("upload.file_with_example_data") }}</th>
            </tr>
            <tr>
                <td>
                    {{ $t("upload.open_document_spreadsheet") }}
                </td>
                <td>
                    <a href="/static/sample_spreadsheets/libre_office_spreadsheet_empty.ods">Empty.ods</a>
                </td>
                <td>
                    <a href="/static/sample_spreadsheets/libre_office_spreadsheet_with_example_data.ods">Example.ods</a>
                </td>
            </tr>
            <tr>
                <td>
                    {{ $t("upload.microsoft_office_excel") }}
                </td>
                <td>
                    <a href="/static/sample_spreadsheets/microsoft_office_spreadsheet_empty.xlsx">Empty.xlsx</a>
                </td>
                <td>
                    <a href="/static/sample_spreadsheets/microsoft_office_spreadsheet_with_example_data.xlsx">Example.xlsx</a>
                </td>
            </tr>
            <tr>
                <td>
                    {{ $t("upload.comma_separated") }}
                </td>
                <td>
                    <a href="/static/sample_spreadsheets/text_spreadsheet_empty.csv">Empty.csv</a>
                </td>
                <td>
                    <a href="/static/sample_spreadsheets/text_spreadsheet_with_example_data.csv">Example.csv</a>
                </td>
            </tr>
        </table>

        <h3>{{ $t("upload.drag_and_drop_uploader.title") }}</h3>
        <p>{{ $t("upload.drag_and_drop_uploader.first_instruction") }}</p>
        <p>{{ $t("upload.drag_and_drop_uploader.nomouse") }}</p>
        <p>{{ $t("upload.drag_and_drop_uploader.process") }}</p>
        <p>{{ $t("upload.drag_and_drop_uploader.details_after_upload") }}</p>
        <p><i>{{ $t("upload.drag_and_drop_uploader.warnings") }}</i></p>
        <form action="/data/upload-spreadsheet/" method="POST"
          class="dropzone"
          id="my-awesome-dropzone" enctype="multipart/form-data">
            <div class="fallback">
                <p>{{ $t("upload.drag_and_drop_uploader.fallback_select_a_file") }}</p>
                <input name="file" type="file"/>
                <input type="submit">
            </div>
        {% endverbatim %}{% csrf_token %}{% verbatim %}
        </form>
        <form action="/data/upload-spreadsheet/" method="POST" enctype="multipart/form-data">
            <div class="fallback">
                <p>{{ $t("upload.drag_and_drop_uploader.fallback_select_a_file") }}</p>
                <input name="file" type="file"/>
                <input type="submit">
            </div>
        {% endverbatim %}{% csrf_token %}{% verbatim %}
        </form>

        <h3>{{ $t("upload.recent_uploads.title") }}</h3>
        <p>{{ $t("upload.recent_uploads.intro") }}</p>
        <table v-if="upload_history">
            <thead>
                <tr>
                    <th>{{ $t("upload.recent_uploads.date") }}</th>
                    <th>{{ $t("upload.recent_uploads.filename") }}</th>
                    <th>{{ $t("upload.recent_uploads.filesize") }}</th>
                    <th>{{ $t("upload.recent_uploads.status") }}</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="upload in upload_history">
                    <td width="15%"><span :title="upload.upload_date">{{ humanize_date(upload.upload_date) }}</span></td>
                    <td width="20%">{{ upload.original_filename }}</td>
                    <td width="8%"><span :title="upload.filesize + ' bytes'">{{ humanize_filesize(upload.filesize) }}</span></td>
                    <td>{{ upload.message }}</td>
                </tr>
            </tbody>
        </table>
        <span v-if="!upload_history.length">{{ $t("upload.recent_uploads.no_uploads") }}</span>
    </div>
</template>
{% endverbatim %}

<script>
Dropzone.options.myAwesomeDropzone = {
    // The name that will be used to transfer the file
    paramName: "file",

    // 1MB is more than enough to house 10.000+ urls.
    maxFilesize: 1,

    // https://gitlab.com/meno/dropzone#enqueuing-file-uploads
    parallelUploads: 1, // handle one at a time to reduce load a bit (except not if you bypass this)
    autoProcessQueue: true,

    /*
    * Client side protection to accept only excel and ods files. Note that given the complexity of these formats,
    * there's a wide window of uploading corrupted or malicious files.
    *
    * More info about mime types:
    * https://stackoverflow.com/questions/4212861/what-is-a-correct-mime-type-for-docx-pptx-etc#4212908
    * https://www.openoffice.org/framework/documentation/mimetypes/mimetypes.html
    * */
    acceptedFiles:
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,' +
        'application/vnd.ms-excel,' +
        'application/vnd.oasis.opendocument.spreadsheet,' +
        'text/plain,' +
        'text/x-csv,' +
        'text/csv',

    // Use this to test when there is a malfunction in the uploader code.
    forceFallback: false,

    // Some events reload the recent uploaded file list.
    init: function() {
        this.on("success", function(file, server_response) {
            vueUpload.get_recent_uploads();
        });
        this.on("error", function(file, server_response) {
            vueUpload.get_recent_uploads();
        });
    }
};

vueUpload = new Vue({
    i18n,
    name: 'uploads',
    el: '#uploads',
    template: '#upload_template',
    mixins: [humanize_mixin],
    data: {
        upload_history: [],
    },
    mounted: function () {
        this.get_recent_uploads();
    },
    methods: {
        get_recent_uploads: function(){
            fetch(`/data/upload-history/`).then(response => response.json()).then(data => {
                this.upload_history = data;
            }).catch((fail) => {console.log('A loading error occurred: ' + fail);});
        },
    }
});
</script>
