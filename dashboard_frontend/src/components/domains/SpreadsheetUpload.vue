<style>
#my-spreadsheet-upload-template .block form {
    overflow: visible;
}

/* Improve contrast for uploads, even though you might not see the right colors, you can now actually see the
 symbol and the result. */
.dropzone .dz-preview.dz-success .dz-success-mark svg g path {
    fill: green;
}

.dropzone .dz-preview.dz-error .dz-error-mark svg g g {
    fill: #ff0000;
}

.dz-error {
    border: 5px solid red;
    border-radius: 23px;
    width: 130px !important;
}

.dz-success {
    border: 5px solid green;
    border-radius: 23px;
    width: 130px !important;
}

/** Having the OK sign disappear does not help, and it flies over too fast... */
.dropzone .dz-preview.dz-success .dz-success-mark {
  opacity: 1;
  -webkit-animation: slide-in 3s cubic-bezier(0.77, 0, 0.175, 1) !important;
  -moz-animation: slide-in 3s cubic-bezier(0.77, 0, 0.175, 1) !important;
  -o-animation: slide-in 3s cubic-bezier(0.77, 0, 0.175, 1) !important;
  animation: slide-in 3s cubic-bezier(0.77, 0, 0.175, 1) !important;
}

</style>
<template>
    <div id="my-spreadsheet-upload-template">
        <div class="block fullwidth">
            <p>&nbsp;
                <router-link tag="button" to="/domains">📚 {{ $t("back_to_domains") }}</router-link>
            </p>
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
        </div>
        <div class="block fullwidth">
            <h3>{{ $t("upload.drag_and_drop_uploader.title") }}</h3>
            <p>{{ $t("upload.drag_and_drop_uploader.first_instruction") }}</p>
            <p>{{ $t("upload.drag_and_drop_uploader.nomouse") }}</p>
            <p>{{ $t("upload.drag_and_drop_uploader.process") }}</p>
            <p>{{ $t("upload.drag_and_drop_uploader.details_after_upload") }}</p>
            <p><i>{{ $t("upload.drag_and_drop_uploader.warnings", [max_urls, max_lists]) }}</i></p>

            <vue-dropzone ref="myVueDropzone" id="dropzone" :options="dropzoneOptions" :useCustomSlot=true
                          v-on:vdropzone-sending="dropzone_sendingEvent">
                <div class="dropzone-custom-content">
                    <h3 class="dropzone-custom-title">{{ $t("dropzone.title") }}</h3>
                    <div class="subtitle">{{ $t("dropzone.subtitle") }}</div>
                </div>
            </vue-dropzone>

            <form :action="`${this.$store.state.dashboard_endpoint}/data/upload-spreadsheet/`" method="POST"
                  enctype="multipart/form-data">
                <div class="fallback">
                    <p>{{ $t("upload.drag_and_drop_uploader.fallback_select_a_file") }}</p>
                    <input name="file" type="file"/>
                    <input type="submit">
                </div>
                <input type="hidden" name="csrfmiddlewaretoken" :value="csrf_token">
            </form>

        </div>
        <div class="block fullwidth">
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
                <tr v-for="(upload, index) in upload_history" :key="index">
                    <td width="15%"><span :title="upload.upload_date">{{ humanize_date(upload.upload_date) }}</span>
                    </td>
                    <td width="20%">{{ upload.original_filename }}</td>
                    <td width="8%"><span :title="upload.filesize + ' bytes'">{{
                            humanize_filesize(upload.filesize)
                        }}</span></td>
                    <td>{{ upload.message }}</td>
                </tr>
                </tbody>
            </table>
            <span v-if="!upload_history.length">{{ $t("upload.recent_uploads.no_uploads") }}</span>
        </div>
    </div>
</template>

<script>
import vue2Dropzone from 'vue2-dropzone'
import 'vue2-dropzone/dist/vue2Dropzone.min.css'

export default {
    mixins: [],
    data: function () {
        let self = this;
        return {
            csrf_token: "",
            upload_history: [],
            dropzoneOptions: {
                url: `${this.$store.state.dashboard_endpoint}/data/upload-spreadsheet/`,
                thumbnailWidth: 150,
                maxFilesize: 1,

                // no need for CSRF token here anymore...
                withCredentials: true,
                paramName: "file",
                headers: {"X-CSRFToken": this.get_cookie('csrftoken')},

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
                init: function () {
                    // function(file, server_response)
                    this.on("success", function () {
                        // todo: update the domain lists...
                        // That can be done with a state change...
                        self.get_recent_uploads();
                    });
                    this.on("error", function () {
                        self.get_recent_uploads();
                    });
                }
            }
        }
    },
    props: {
        // Something weird happens when an integer is passed, it is still seen as a string.
        max_urls: {type: Number, required: true},
        max_lists: {type: Number, required: true},
    },
    mounted: function () {
        this.get_recent_uploads();
        this.csrf_token = this.get_cookie('csrftoken');
    },
    components: {
        vueDropzone: vue2Dropzone
    },
    methods: {
        dropzone_sendingEvent(file, xhr, formData) {
            // add the csrfmiddlewaretoken to the form.
            formData.append('csrfmiddlewaretoken', this.get_cookie('csrftoken'));
        },

        get_recent_uploads: function () {
            fetch(`${this.$store.state.dashboard_endpoint}/data/upload-history/`, {credentials: 'include'}).then(response => response.json()).then(data => {
                this.upload_history = data;
                this.$store.commit("set_uploads_performed", data.length);
            }).catch((fail) => {
                console.log('A loading error occurred: ' + fail);
            });
        },
    }
}
</script>
<i18n>
{
    "en": {
        "back_to_domains": "Back to domains",
        "dropzone": {
            "title": "Drag and drop to upload content!",
            "subtitle": "...or click to select a file from your computer"
        },
        "upload": {
            "bulk_data_uploader": {
                "title": "Domain Spreadsheet Uploader",
                "introduction": "It\"s possible to upload large amounts of internet addresses and lists using spreadsheets. To do so, please expand on the example spreadsheets listed below. This shows how the data has to be structured. Examples with and without data are provided as Open Document Spreadsheet, Microsoft Office Excel and Comma Separated."
            },
            "empty_file": "Empty file",
            "file_with_example_data": "File with example data",
            "open_document_spreadsheet": "Open Document Spreadsheet (Libre Office)",
            "microsoft_office_excel": "Excel Spreadsheet (Microsoft Office)",
            "comma_separated": "Comma Separated (for programmers)",
            "drag_and_drop_uploader": {
                "title": "Drag and drop uploader",
                "first_instruction": "To upload a bulk address file, drag it onto the \"upload\" rectangle below.",
                "nomouse": "A more conventional upload option is available below the drag and drop uploader.",
                "process": "Uploading happens in two stages. First the progress bar is filled, this means the data is sent to this website successfully. Then some processing happens on the server. When this processing is finished, the uploaded file icon below will change to either Success (green, with a checkmark) or Failed (red, with a cross).",
                "details_after_upload": "Details on the status of the uploaded file can be seen afterwards in the \"recent uploads\" section below this uploader.",
                "warnings": "Important: It\"s possible to upload up until {0} urls in {1} lists per upload. The more is uploaded, the more time it will take. Please wait until the upload is confirmed.",
                "fallback_select_a_file": "Select a file to upload:"
            },
            "recent_uploads": {
                "title": "Recent uploads",
                "intro": "This list shows your recent uploads. The status messages give an impression of what has been created or added. If something went wrong, the status contains hints on what to do next. if your upload was not successful",
                "date": "Date",
                "filename": "Filename",
                "filesize": "Size",
                "status": "Status",
                "no_uploads": "No files uploaded."
            }
        }
    },
    "nl": {
        "back_to_domains": "Terug naar domeinen",
        "dropzone": {
            "title": "Sleep bestanden naar dit vlak om ze te uploaden!",
            "subtitle": "...of klik hier om bestanden te selecteren"
        },
        "upload": {
            "bulk_data_uploader": {
                "title": "Spreadsheet Domeinen Uploader",
                "introduction": "Hiermee is het mogelijk om grote hoeveelheden internet adressen en lijsten toe te voegen. Dit gebeurd met spreadsheets. Begin met het downloaden van de voorbeelden hieronder, deze geven aan wat het juiste formaat is. De voorbeeldbestanden zijn te downloaden in het Open Document formaat, Microsoft Office formaat en Kommagescheiden."
            },
            "empty_file": "Leeg bestand",
            "file_with_example_data": "Bestand met voorbeelddata",
            "open_document_spreadsheet": "Open Document Werkblad (Libre Office)",
            "microsoft_office_excel": "Excel Werkblad (Microsoft Office)",
            "comma_separated": "Kommagescheiden (voor programmeurs)",
            "drag_and_drop_uploader": {
                "title": "Drag and drop uploader",
                "first_instruction": "Sleep het gewenste bestand in de \"upload\" rechthoek hieronder.",
                "nomouse": "Een meer gebruikelijke upload methode is beschikbaar onder het drag and drop gedeelte.",
                "process": "Het uploaden gebeurd in twee fasen. In de eerste fase wordt de voortgangsbalk gevuld. Als deze vol is, is het bestand naar de server gestuurd. Dan is de upload nog niet compleet: de gegevens worden nu verwerkt. Op het moment dat de gegevens verwerkt zijn verschijnt dit als een groen vinkje of rood kruis op het bestand.",
                "details_after_upload": "Details over de status van de upload kunnen naderhand worden bekeken in het \"recente uploads\" onderdeel onder het upload veld.",
                "warnings": "Let op: Het is mogelijk om tot {0} adressen in {0} lijsten te sturen per keer. Hoe meer gegevens, hoe langer het kan duren voordat de upload volledig is. Wees geduldig en wacht tot de upload afgerond is.",
                "fallback_select_a_file": "Selecteer een bestand om te uploaden:"
            },
            "recent_uploads": {
                "title": "Recent geupload",
                "intro": "Deze lijst geeft de meest recente uploads weer. De status berichten geven aan wat er is toegevoegd. Mocht er iets verkeerd zijn gegaan bij het uploaden, dan is hier advies te vinden over wat te verbeteren.",
                "date": "Datum",
                "filename": "Bestand",
                "filesize": "Grootte",
                "status": "Status (in het Engels)",
                "no_uploads": "Nog geen bestanden geüpload."
            }
        }
    }
}
</i18n>