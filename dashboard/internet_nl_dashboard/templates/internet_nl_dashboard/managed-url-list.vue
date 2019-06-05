{% verbatim %}
<template type="x-template" id="managed-url-list">
    <article class="managed-url-list">
        <a :name="list.id"></a>
        <h3>
            <button v-if="!is_opened" @click="open_list()">📘 {{ list.name }}</button>
            <button v-if="is_opened" @click="close_list()">📖 {{ list.name }}</button>

            <div v-if="is_opened" style="float:right;">
                <button @click="start_editing_settings()">📝 {{ $t("domain_management.button_labels.configure") }}</button>
                <button @click="start_bulk_add_new()">💖 {{ $t("domain_management.button_labels.add_domains") }}</button>
                <template v-if="urls.length">
                    <template v-if="list.enable_scans">
                        <button v-if="list.scan_now_available" @click="start_scan_now()">🔬 {{ $t("domain_management.button_labels.scan_now") }}</button>

                        <button v-if="!list.scan_now_available && !list.last_scan_finished" disabled="disabled"
                        :title='$t("domain_management.button_labels.scan_now_scanning")'>
                            <img width="15" style="border-radius: 50%" src="/static/images/vendor/internet_nl/probe-animation.gif">
                            {{ $t("domain_management.button_labels.scan_now_scanning") }}
                        </button>
                        <button v-if="!list.scan_now_available && list.last_scan_finished" disabled="disabled"
                        :title='$t("domain_management.button_labels.timeout_for_24_hours")'>
                            <img width="15" style="border-radius: 50%" src="/static/images/vendor/internet_nl/probe-animation.gif">
                            {{ $t("domain_management.button_labels.timeout_for_24_hours") }}
                        </button>
                    </template>
                    <button v-if="!list.enable_scans" disabled="disabled"
                    :title='$t("domain_management.button_labels.scanning_disabled")'>
                        🔬 {{ $t("domain_management.button_labels.scanning_disabled") }}
                    </button>
                </template>
                <button @click="start_deleting()">🔪 {{ $t("domain_management.button_labels.delete") }}</button>
            </div>
        </h3>
        <br>

        <div v-if="is_opened">
            <h4>{{ $t("domain_management.about_this_list.header") }}</h4>
            <span v-if="list.last_scan">
                {{ $t("domain_management.about_this_list.last_scan_started") }}: {{ humanize_date(list.last_scan) }}.
                <span v-if="!list.last_scan_finished">({{ $t("domain_management.about_this_list.still_running") }})</span>
                <span v-if="list.last_scan_finished">({{ $t("domain_management.about_this_list.finished") }})</span>
            </span>
            <span v-if="!list.last_scan">
                {{ $t("domain_management.about_this_list.last_scan_started") }}: {{ $t("domain_management.about_this_list.not_scanned_before") }}.
            </span>
            <div class="scan-configuration">
                <div v-if="list.enable_scans">
                    {{ $t("domain_management.about_this_list.type_of_scan_performed") }}:
                    <span title="Web scans will be performed" v-if="list.enable_scans && list.scan_type === 'mail'">📨 {{ list.scan_type }}</span>
                    <span title="Web scans will be performed" v-if="list.enable_scans && list.scan_type === 'web'">🌐 {{ list.scan_type }}</span>
                    <span title="No scans will be performed" v-if="!list.enable_scans">🚫 {{ list.scan_type }}</span><br>
                    {{ $t("domain_management.about_this_list.scan_frequency") }}: {{ list.automated_scan_frequency }} <br>
                    <div v-if="list.automated_scan_frequency !== 'disabled'">
                        {{ $t("domain_management.about_this_list.next_scheduled_scan") }}: {{ humanize_date(list.scheduled_next_scan) }} <br>
                    </div>
                </div>
                <div v-if="!list.enable_scans">
                    {{ $t("domain_management.about_this_list.scanning_disabled") }}
                </div>
            </div>
            <span v-if="list.last_report_id">
                 {{ $t("domain_management.about_this_list.latest_report") }}: {{ humanize_date(list.last_report_date) }}
                (<a :href="'/reports/' + list.last_report_id" target="_blank">{{ $t("domain_management.about_this_list.open") }}</a>)<br>
            </span>
            <br>

            <h4>{{ $t("domain_management.domains.header") }}</h4>
            <br>
            <div v-if="!urls.length">
                <button @click="start_bulk_add_new()">💖 {{ $t("domain_management.button_labels.add_domains") }}</button>
            </div>
            <div style="column-count: 2;">
                <div v-for="url in urls" class="url-in-managed-list">

                    <span v-if="url.has_mail_endpoint === true" :title="$t('domain_management.domains.eligeble_mail')">
                        <a :href="'https://www.internet.nl/mail/' + url.url + '/'" target="_blank">📨</a>
                    </span>
                    <span v-if="url.has_mail_endpoint === 'unknown'" :title="$t('domain_management.domains.unknown_eligeble_mail')">❓</span>
                    <span v-if="url.has_mail_endpoint === false" :title="$t('domain_management.domains.not_eligeble_mail')">🚫</span>
                    <span v-if="url.has_web_endpoint === true" :title="$t('domain_management.domains.not_eligeble_web')">
                        <a :href="'https://www.internet.nl/site/' + url.url + '/'" target="_blank">🌐</a>
                    </span>
                    <span v-if="url.has_web_endpoint === 'unknown'" :title="$t('domain_management.domains.unknown_eligeble_web')">❓</span>
                    <span v-if="url.has_web_endpoint === false" :title="$t('domain_management.domains.not_eligeble_web')">🚫</span>

                    <span title="Edit this domain" @click="start_url_editing(list.id, url.url)">🖊</span>
                    <a v-if="!url_is_edited(list.id, url.url)" @click="start_url_editing(list.id, url.url)">{{ url.url }}</a>

                    <span class="inline-edit" v-if="url_is_edited(list.id, url.url)">
                            <input autofocus :placeholder="url.url" :value="url.url" :id="'' + list.id + url.url">
                            <button @click="save_edit_url({'list_id': list.id,'url_id': url.id, 'new_url_string': get_url_edit_value()})">{{ $t("domain_management.domains.button_labels.save") }}</button>
                            <button @click="cancel_edit_url()">{{ $t("domain_management.domains.button_labels.cancel") }}</button>
                            <!-- The remove is real, as it will only remove 1 items -->
                            <button @click="remove_edit_url(list.id, url.id)">{{ $t("domain_management.domains.button_labels.remove") }}</button>
                    </span>
                </div>
            </div>
            <br>
            <button v-if="urls.length" @click="toggle_view_csv()" value="load">📋 {{ $t("domain_management.button_labels.view_csv") }}</button><br>
            <textarea v-if="view_csv" class="view-csv" :value="csv_value"></textarea>
        </div>

        <!-- modal dialogs are below the content to make sure the tab order stays working. -->
        <modal v-if="show_list_settings" @close="cancel_editing_settings()">
            <h3 slot="header">🖊 {{ $t("domain_management.edit_form.title") }}</h3>
            <div slot="body">

                <server-response :response="settings_update_response"></server-response>

                <label for="name">{{ $t("urllist.field_label_name") }}:</label><br>
                <input id="name" type="text" maxlength="120" v-model="list.name"><br><br>

                <label for="enable_scans">{{ $t("urllist.field_label_enable_scans") }}:</label><br>
                <input id="enable_scans" type="checkbox" v-model="list.enable_scans">
                <span v-if="list.enable_scans">Enabled</span>
                <span v-if="!list.enable_scans">Disabled</span>
                <br><br>

                <label for="scan_type">{{ $t("urllist.field_label_scan_type") }}:</label><br>
                <select id="scan_type" v-model="list.scan_type">
                    <option value="web">{{ $t("urllist.scan_type_web") }}</option>
                    <option value="mail">{{ $t("urllist.scan_type_mail") }}</option>
                </select><br><br>

                <label for="automated_scan_frequency">{{ $t("urllist.field_label_automated_scan_frequency") }}:</label><br>
                <select id="automated_scan_frequency" v-model="list.automated_scan_frequency">
                    <option value="disabled">{{ $t("urllist.automated_scan_frequency_disabled") }}</option>
                    <option value="every half year">{{ $t("urllist.automated_scan_frequency_every_half_year") }}</option>
                    <option value="at the start of every quarter">{{ $t("urllist.automated_scan_frequency_every_quarter") }}</option>
                    <option value="every 1st day of the month">{{ $t("urllist.automated_scan_frequency_every_month") }}</option>
                    <option value="twice per month">{{ $t("urllist.automated_scan_frequency_twice_per_month") }}</option>
                </select>

            </div>
            <div slot="footer">
                <button @click="cancel_editing_settings()">{{ $t("domain_management.edit_form.cancel") }}</button>
                <button class="modal-default-button" @click="update_list_settings()">{{ $t("domain_management.edit_form.ok") }}</button>
            </div>
        </modal>

        <modal v-if="show_deletion" @close="stop_deleting()">
            <h3 slot="header">{{ $t("domain_management.delete_form.title") }}</h3>
            <div slot="body">

                <server-response :response="delete_response"></server-response>

                <p class="warning">{{ $t("domain_management.delete_form.message") }}</p>

                <label for="name">{{ $t("urllist.field_label_name") }}:</label><br>
                {{ list.name }}<br>
                <br>

                <label for="enable_scans">{{ $t("urllist.field_label_enable_scans") }}:</label><br>
                {{ list.enable_scans }}<br>
                <br>

                <label for="scan_type">{{ $t("urllist.field_label_scan_type") }}:</label><br>
                {{ list.scan_type }}<br>
                <br>

                <label for="automated_scan_frequency">{{ $t("urllist.field_label_automated_scan_frequency") }}:</label><br>
                {{ list.automated_scan_frequency }}<br>
                <br>

            </div>
            <div slot="footer">
                <button @click="stop_deleting()">{{ $t("domain_management.delete_form.cancel") }}</button>
                <button class="modal-default-button" @click="confirm_deletion()">{{ $t("domain_management.delete_form.ok") }}</button>
            </div>
        </modal>

        <modal v-if="show_scan_now" @close="stop_scan_now()">
            <h3 slot="header">{{ $t("domain_management.scan_now_form.title") }}</h3>
            <div slot="body">

                <server-response :response="scan_now_server_response"></server-response>

                <p v-html='$t("domain_management.scan_now_form.message")'></p>

            </div>
            <div slot="footer">
                <button @click="stop_scan_now()">{{ $t("domain_management.scan_now_form.cancel") }}</button>
                <button class="modal-default-button" @click="confirm_scan_now()">{{ $t("domain_management.scan_now_form.ok") }}</button>
            </div>
        </modal>

        <modal v-if="show_bulk_add_new" @close="stop_bulk_add_new()">
            <h3 slot="header">{{ $t("domain_management.bulk_add_form.title") }}</h3>
            <div slot="body">

                <server-response :response="bulk_add_new_server_response"></server-response>

                <p>{{ $t("domain_management.bulk_add_form.message") }}</p>

                <select2-tags-widget v-model="bulk_add_new_urls"></select2-tags-widget>

                <div v-if="bulk_add_new_server_response">
                    <span v-if="bulk_add_new_server_response.success === true">
                        {{ $t("domain_management.bulk_add_form.status") }}:
                        {{ $t("domain_management.bulk_add_form.added_n_to_list", [bulk_add_new_server_response.data.added_to_list]) }}

                        <span v-if="bulk_add_new_server_response.data.already_in_list">
                            {{ $t("domain_management.bulk_add_form.ignored_n", [bulk_add_new_server_response.data.already_in_list]) }}<br>
                        </span>
                        <span v-if="bulk_add_new_server_response.data.incorrect_urls.length">
                            <br><b>{{ $t("domain_management.bulk_add_form.warning") }}</b><br>
                            {{ $t("domain_management.bulk_add_form.warning_message") }}
                            {{ bulk_add_new_server_response.data.incorrect_urls.join(', ') }}<br>
                        </span>
                    </span>
                </div>
                <div v-if="!bulk_add_new_server_response.message">
                    <p>{{ $t("domain_management.bulk_add_form.status") }}: {{ $t("domain_management.bulk_add_form.nothing_added") }}.</p>
                </div>
                <br>
                <button class="modal-default-button" @click="bulk_add_new()">{{ $t("domain_management.bulk_add_form.ok") }}</button>

            </div>
            <div slot="footer">
            </div>
        </modal>
    </article>
</template>
{% endverbatim %}

<script>
Vue.component('managed-url-list', {
    i18n,
    template: '#managed-url-list',
    mixins: [humanize_mixin, http_mixin],

    data: function () {
        return {
            urls: [],
            is_opened: false,

            loading: false,

            // contains all known list data, should not be needed to individually fetch the list (again), only
            // after update.
            list: this.initial_list,

            // everything to do with settings.
            show_list_settings: false,
            settings_loading: false,
            settings_update_response: {},
            old_list_settings: {},

            // everything to do with deleting this list
            show_deletion: false,
            delete_response: {},

            // everything to do with editing urls in the list:
            url_edit: '',
            original_url_value: '',

            // everything that has to do with adding urls:
            show_bulk_add_new: false,
            bulk_add_new_urls: [],
            bulk_add_new_server_response: {},

            // everything to do with csv:
            view_csv: false,

            // scan now feature:
            show_scan_now: false,
            scan_now_server_response: {}
        }
    },
    props: {
        // Avoid mutating a prop directly since the value will be overwritten whenever the parent component re-renders.
        // Instead, use a data or computed property based on the prop's value. Prop being mutated: "list".
        // This is updated via a watch below. This allows for adding to the top of the list / real reactivity.
        initial_list: Object,
    },
    watch: {
        initial_list: function(new_value){
            this.list = new_value;
        }
    },
    mounted: function(){
        if (window.location.href.split('/').length > 3) {
            let get_id = window.location.href.split('/')[4];
            console.log(get_id);
            // can we change the select2 to a certain value?

            if (this.list.id === parseInt(get_id)){
                this.open_list();
            }
        }
    },
    methods: {
        open_list: function(){
            this.get_urls();
            this.is_opened = true;
        },
        close_list: function(){
          this.is_opened = false;
        },
        get_urls: function(){
            this.loading = true;
            fetch(`/data/urllist_content/get/${this.list.id}/`, {credentials: 'include'}).then(response => response.json()).then(data => {
                this.urls = data.urls;
                this.loading = false;
            }).catch((fail) => {console.log('A loading error occurred: ' + fail);});
        },
        update_list_settings: function(){
            this.settings_loading = true;

            this.asynchronous_json_post(
                '/data/urllist/update_list_settings/', this.list, (server_response) => {
                    this.settings_update_response = server_response;
                    this.settings_loading = false;

                    // The upcoming scan date has probably changed, and we want to reflect that in the UI.
                    this.list = server_response.data;
                    // make sure the cancel button goes to the last save.
                    this.old_list_settings = this.copy_values(this.list);

                    if (server_response.success){
                        this.stop_editing_settings();
                    }
                });
        },
        start_editing_settings: function(){
            // keep an old value in memory. If the editing is canceled, the old value should be used.
            // here a weakness is of js is showing:
            // https://stackoverflow.com/questions/728360/how-do-i-correctly-clone-a-javascript-object
            // luckily we can use the simple approach...
            this.old_list_settings = this.copy_values(this.list);
            this.settings_update_response = {};
            this.show_list_settings = true;
        },
        stop_editing_settings: function(){
            this.show_list_settings = false;
            this.settings_update_response = {};
        },
        cancel_editing_settings: function(){
            this.list = this.copy_values(this.old_list_settings);
            this.stop_editing_settings();
        },
        copy_values: function(obj){
            // does not copy methods.
            return JSON.parse(JSON.stringify(obj));
        },
        start_deleting: function(){
            this.show_deletion = true;
            this.delete_response = {};
        },
        stop_deleting: function(){
            this.show_deletion = false;
            this.delete_response = {};
        },
        confirm_deletion: function() {
            this.asynchronous_json_post(
                '/data/urllist/delete/', {'id': this.list.id}, (server_response) => {
                    this.delete_response = server_response;

                    if (server_response.success){
                        // remove / hide this thing...
                        this.$emit('removelist', this.list.id);
                        this.stop_deleting();
                    }
                }
            );
        },
        start_url_editing: function(list_id, url_id){
            this.url_edit = '' + list_id + url_id;
            this.original_url_value = url_id;
            // after the item is rendered.
            this.$nextTick(() => document.getElementById(this.url_edit).focus());
        },
        url_is_edited: function(list_id, url_id){
            return this.url_edit === '' + list_id + url_id
        },
        cancel_edit_url: function(){
            if (!this.url_edit)
                return;

            if (document.getElementById(this.url_edit)){
                document.getElementById(this.url_edit).value = this.original_url_value;
            }
            this.url_edit = '';
        },
        get_url_edit_value: function(){
            return document.getElementById(this.url_edit).value;
        },
        remove_edit_url: function(list_id, url_id){
            data = {'list_id': list_id, 'url_id': url_id};
            this.asynchronous_json_post(
                '/data/urllist/url/delete/', data, (server_response) => {
                    this.delete_response = server_response;

                    if (server_response.success) {
                        this.urls.forEach(function (item, index, object) {
                            if (url_id === item.id) {
                                object.splice(index, 1)
                            }
                        });
                    }
                }
            );
        },
        save_edit_url: function(data){
            /*
            * This is not a real 'save' but an add to list and create if it doesn't exist operation.
            * The save does not 'alter' the existing URL in the database. It will do some list operations.
            * */
            this.asynchronous_json_post(
                '/data/urllist/url/save/', data, (server_response) => {
                    if (server_response.success === true){
                        this.url_edit = '';
                        // and make sure the current url list is updated as well. Should'nt this be data bound and
                        // such?
                        this.urls.forEach(function(item, index, object) {
                        if (server_response.data.removed.id === item.id) {
                            object[index] = server_response.data.created;
                            // object.splice(index, 1);
                            // object.push(server_response.data.created)
                        }
                    });
                    } else {
                        document.getElementById(this.url_edit).value=this.original_url_value;
                    }
                }
            );

        },

        start_bulk_add_new: function(){
            this.show_bulk_add_new = true;
        },
        stop_bulk_add_new: function(){
            this.show_bulk_add_new = false;
            this.bulk_add_new_server_response = {};

            // re-load the url list, as perhaps more information about endpoints is discovered.
            this.get_urls();
        },
        bulk_add_new: function(){
            data = {'urls': this.bulk_add_new_urls, 'list_id': this.list.id};

            this.asynchronous_json_post(
                '/data/urllist/url/add/', data, (server_response) => {
                    // {'incorrect_urls': [], 'added_to_list': int, 'already_in_list': int}
                    this.bulk_add_new_server_response = server_response;

                    // Update the list of urls accordingly.
                    if (server_response.success) {
                        this.get_urls();
                    }
                    // The select2 box is cleared when opened again. We don't need to clear it.
                }
            );
        },
        toggle_view_csv: function(){
            this.view_csv = !this.view_csv;
        },
        start_scan_now: function(){
            this.show_scan_now = true;
        },
        stop_scan_now: function(){
            this.show_scan_now = false;
            this.scan_now_server_response = {};
        },
        confirm_scan_now: function(){
            data = {'id': this.list.id};

            this.asynchronous_json_post(
                '/data/urllist/scan_now/', data, (server_response) => {
                    this.scan_now_server_response = server_response;

                    if (server_response.success) {
                        this.list.scan_now_available = false;
                        this.stop_scan_now()
                    }
                }
            );
        }
    },
    computed: {
       csv_value: function(){
           urls = [];
           this.urls.forEach(function(item) {
               urls.push(item.url);
           });
           return urls.join(', ');
       }
    },
});
</script>
