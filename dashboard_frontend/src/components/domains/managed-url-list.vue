<style>

.managed-url-list h2 {
    display: inline;
    font-size: 1.2em;
}
.view-csv {
    width: 100%;
    height: 200px;
}
.inline-edit input {
    margin-bottom: 0 !important;
}

.inline-edit button {
    font-size: 0.7em !important;
    margin: 0 !important;
    height: 23px;
}
</style>

<template>
    <article class="managed-url-list block fullwidth" :id="list.id">
        <span>
            <a :name="list.id"></a>
            <h2>
                <button v-if="!is_opened" @click="open_list()" aria-expanded="false">
                    <span role="img" v-if="list_contains_warnings" :aria-label="$t('icons.list_warning')">⚠️</span>
                    <span role="img" :aria-label="$t('icons.list_closed')">📘</span>
                    {{ list.name }}
                </button>
            </h2>
            <h2>
                <button v-if="is_opened" @click="close_list()" aria-expanded="true">
                    <span role="img" v-if="list_contains_warnings" :aria-label="$t('icons.list_warning')">⚠️</span>
                    <span role="img" :aria-label="$t('icons.list_opened')">📖</span>
                    {{ list.name }}
                </button>
            </h2>

            <div v-if="is_opened" style="float:right;">
                <button @click="start_editing_settings()">
                    <span role="img" :aria-label="$t('icons.settings')">📝</span>
                    {{ $t("button_labels.configure") }}</button> &nbsp;
                <button @click="start_bulk_add_new()">
                    <span role="img" :aria-label="$t('icons.bulk_add_new')">💖</span>
                    {{ $t("button_labels.add_domains") }}</button> &nbsp;
                <template v-if="urls.length">
                    <template v-if="list.enable_scans">
                        <button v-if="list.scan_now_available" @click="start_scan_now()">
                            <span role="img" :aria-label="$t('icons.scan')">🔬</span>
                            {{ $t("button_labels.scan_now") }}
                        </button> &nbsp;
                        <button v-if="!list.scan_now_available" disabled="disabled"
                                :title='$t("button_labels.scan_now_scanning")'>
                            <img width="15" style="border-radius: 50%"
                                 src="/static/images/vendor/internet_nl/probe-animation.gif">
                            {{ $t("button_labels.scan_now_scanning") }}
                        </button>
                    </template> &nbsp;
                    <button v-if="!list.enable_scans" disabled="disabled"
                            :title='$t("button_labels.scanning_disabled")'>
                        <span role="img" :aria-label="$t('icons.scan')">🔬</span>
                        {{ $t("button_labels.scanning_disabled") }}
                    </button> &nbsp;
                </template>
                <button @click="start_deleting()">🗑️ {{ $t("button_labels.delete") }}</button>
            </div>
        </span>
        <br>

        <div v-if="is_opened">
            <h3>{{ $t("about_this_list.header") }}</h3>
            <p>
                <span v-if="list.last_scan">
                    {{ $t("about_this_list.last_scan_started") }}: {{ humanize_date(list.last_scan) }}.
                    ({{ list.last_scan_state }})
                </span>
                <span v-if="!list.last_scan">
                    {{ $t("about_this_list.last_scan_started") }}: {{ $t("about_this_list.not_scanned_before") }}.
                </span>
                <template class="scan-configuration">
                    <div v-if="list.enable_scans">
                        {{ $t("about_this_list.type_of_scan_performed") }}:
                        <span title="Mail scans will be performed"
                              v-if="list.enable_scans && list.scan_type === 'mail'">
                            <img src="/static/images/vendor/internet_nl/icon-emailtest.svg" style="height: 16px;">
                        {{ list.scan_type }}</span>
                        <span title="Web scans will be performed" v-if="list.enable_scans && list.scan_type === 'web'">
                            <img src="/static/images/vendor/internet_nl/icon-website-test.svg" style="height: 16px;">
                            {{ list.scan_type }}</span>
                        <span title="No scans will be performed" v-if="!list.enable_scans">🚫 {{
                                list.scan_type
                            }}</span><br>
                        <span v-if="urls">
                            {{ $t("about_this_list.number_of_domains") }}: {{ urls.length }}
                        </span>
                        <span v-if="!urls">
                            {{ $t("about_this_list.number_of_domains") }}: {{ list.num_urls }}
                        </span><br>
                        {{ $t("about_this_list.scan_frequency") }}: {{ $t(`about_this_list.${list.automated_scan_frequency}`) }} <br>
                        <div v-if="list.automated_scan_frequency !== 'disabled'">
                            {{ $t("about_this_list.next_scheduled_scan") }}: {{
                                humanize_date(list.scheduled_next_scan)
                            }} <br>
                        </div>
                    </div>
                    <div v-if="!list.enable_scans">
                        {{ $t("about_this_list.scanning_disabled") }}
                    </div>
                </template>
                <span v-if="list.last_report_id">
                    <router-link :to="{ name: 'numbered_report', params: { report: list.last_report_id }}">
                        <span role="img" :aria-label="$t('icons.report')">📊</span>
                        {{ $t("about_this_list.latest_report") }}: {{ humanize_date(list.last_report_date) }}
                    </router-link>
                    <br>
                </span>
            </p>
            <br>

            <h3>{{ $t("domains.header") }}</h3>
            <p v-html="$t('domains.intro')"></p>

            <template v-if="this.list.list_warnings.indexOf('WARNING_DOMAINS_IN_LIST_EXCEED_MAXIMUM_ALLOWED') > -1">
                <div class="server-response-error">
                    <span role="img" :aria-label="$t('icons.list_warning')">⚠️</span>{{
                        $t("warnings.domains_exceed_maximum", [this.maximum_domains])
                    }}
                </div>
            </template>
            <br>

            <div v-if="!urls.length">
                <button @click="start_bulk_add_new()">💖 {{ $t("button_labels.add_domains") }}</button>
            </div>

            <loading :loading="loading"></loading>

            <ul style="column-count: 2; list-style: none;">
                <li v-for="url in urls" :key="url.id">

                    <template v-if="list.scan_type === 'mail'">
                        <span v-if="url.has_mail_endpoint === true" :title="$t('domains.eligeble_mail', [url.url])">
                            <span role="img" :aria-label="$t('domains.eligeble_mail', [url.url])">🌍</span>
                            <!-- <a :href="'https://www.internet.nl/mail/' + url.url + '/'" target="_blank"></a> -->
                        </span>
                        <span v-if="url.has_mail_endpoint === 'unknown'"
                              :title="$t('domains.unknown_eligeble_mail', [url.url])">
                            <span role="img" :aria-label="$t('domains.unknown_eligeble_mail', [url.url])">❓</span>
                        </span>
                        <span v-if="url.has_mail_endpoint === false"
                              :title="$t('domains.not_eligeble_mail', [url.url])">
                            <span role="img" :aria-label="$t('domains.not_eligeble_mail', [url.url])">🚫</span>
                        </span>
                    </template>

                    <template v-if="list.scan_type === 'web'">
                        <span v-if="url.has_web_endpoint === true" :title="$t('domains.not_eligeble_web', [url.url])">
                            <!-- <a :href="'https://www.internet.nl/site/' + url.url + '/'" target="_blank"></a> -->
                            <span role="img" :aria-label="$t('domains.not_eligeble_web', [url.url])">🌍</span>
                        </span>
                        <span v-if="url.has_web_endpoint === 'unknown'"
                              :title="$t('domains.unknown_eligeble_web', [url.url])">
                            <span role="img" :aria-label="$t('domains.unknown_eligeble_web', [url.url])">❓</span>
                        </span>
                        <span v-if="url.has_web_endpoint === false" :title="$t('domains.not_eligeble_web', [url.url])">
                            <span role="img" :aria-label="$t('domains.not_eligeble_web', [url.url])">🚫</span>
                        </span>
                    </template>
                    &nbsp;
                    <button style="font-size: 12px;" v-if="url_edit !== '' + list.id + url.url" class="inline-edit"
                            :title="$t('domains.start_editing_url', [url.url])"
                            @click="start_url_editing(list.id, url.url)" aria-expanded="false">
                        🖊
                        <span class="visuallyhidden">{{ $t('domains.start_editing_url', [url.url]) }}</span>
                    </button>
                    <button style="font-size: 12px;" v-if="url_edit === '' + list.id + url.url" class="inline-edit"
                            :title="$t('domains.cancel_editing_url', [url.url])"
                            @click="cancel_edit_url(list.id, url.url)" aria-expanded="true">
                        🖊
                        <span class="visuallyhidden">{{ $t('domains.cancel_editing_url', [url.url]) }}</span>
                    </button>
                    &nbsp;
                    <template v-if="url.subdomain">
                        <a v-if="!url_is_edited(list.id, url.url)"
                           @click="start_url_editing(list.id, url.url)">{{ url.subdomain }}.<b>{{
                                url.domain
                            }}.{{ url.suffix }}</b></a>
                    </template>
                    <template v-if="!url.subdomain">
                        <a v-if="!url_is_edited(list.id, url.url)"
                           @click="start_url_editing(list.id, url.url)"><b>{{ url.domain }}.{{ url.suffix }}</b></a>
                    </template>

                    <span class="inline-edit" v-if="url_is_edited(list.id, url.url)">
                            <input autofocus :placeholder="url.url" :value="url.url" :id="'' + list.id + url.url">&nbsp;
                            <button
                                @click="save_edit_url({'list_id': list.id,'url_id': url.id, 'new_url_string': get_url_edit_value()})"
                                :title="$t('domains.save_edited_url', [url.url])">
                                {{ $t("domains.button_labels.save") }}
                                <span class="visuallyhidden">{{ $t('domains.save_edited_url', [url.url]) }}</span>
                            </button>&nbsp;
                            <button @click="cancel_edit_url()" :title="$t('domains.cancel_editing_url', [url.url])">
                                {{ $t("domains.button_labels.cancel") }}
                                <span class="visuallyhidden">{{ $t('domains.cancel_editing_url', [url.url]) }}</span>
                            </button>&nbsp;
                        <!-- The remove is real, as it will only remove 1 items -->
                            <button @click="remove_edit_url(list.id, url.id)"
                                    :title="$t('domains.delete_edited_url', [url.url])">
                                {{ $t("domains.button_labels.remove") }}
                                <span class="visuallyhidden">{{ $t('domains.delete_edited_url', [url.url]) }}</span>
                            </button>
                    </span>
                </li>
            </ul>
            <br>
            <button v-if="urls.length" @click="toggle_view_csv()" value="load">📋 {{
                    $t("button_labels.view_csv")
                }}
            </button>
            <br>
            <textarea v-if="view_csv" class="view-csv" :value="csv_value"></textarea>
        </div>

        <!-- modal dialogs are below the content to make sure the tab order stays working. -->
        <internet_nl_modal v-if="show_list_settings" @close="cancel_editing_settings()">
            <h3 slot="header">📝 {{ $t("edit_form.title") }}</h3>
            <div slot="body">

                <server-response :response="settings_update_response"></server-response>

                <label for="name">{{ $t("urllist.field_label_name") }}:</label><br>
                <input id="name" type="text" maxlength="120" v-model="list.name"><br><br>

                <label for="scan_type">{{ $t("urllist.field_label_scan_type") }}:</label><br>
                <select id="scan_type" v-model="list.scan_type">
                    <option value="web">{{ $t("urllist.scan_type_web") }}</option>
                    <option value="mail">{{ $t("urllist.scan_type_mail") }}</option>
                </select><br><br>

                <label for="automated_scan_frequency">{{
                        $t("urllist.field_label_automated_scan_frequency")
                    }}:</label><br>
                <select id="automated_scan_frequency" v-model="list.automated_scan_frequency">
                    <option value="disabled">{{ $t("urllist.automated_scan_frequency.disabled") }}</option>
                    <option value="every half year">{{
                            $t("urllist.automated_scan_frequency.every_half_year")
                        }}
                    </option>
                    <option value="at the start of every quarter">
                        {{ $t("urllist.automated_scan_frequency.every_quarter") }}
                    </option>
                    <option value="every 1st day of the month">{{
                            $t("urllist.automated_scan_frequency.every_month")
                        }}
                    </option>
                    <option value="twice per month">{{
                            $t("urllist.automated_scan_frequency.twice_per_month")
                        }}
                    </option>
                </select>

            </div>
            <div slot="footer">
                <button class='altbutton' @click="cancel_editing_settings()">{{ $t("edit_form.cancel") }}</button>
                &nbsp;
                <button class="modal-default-button defaultbutton" @click="update_list_settings()">{{
                        $t("edit_form.ok")
                    }}
                </button>
            </div>
        </internet_nl_modal>

        <internet_nl_modal v-if="show_deletion" @close="stop_deleting()">
            <h3 slot="header">🗑️ {{ $t("delete_form.title") }}</h3>
            <div slot="body">

                <server-response :response="delete_response"></server-response>

                <p class="dialog_warning">{{ $t("delete_form.message") }}</p>

                <label for="name">{{ $t("urllist.field_label_name") }}:</label><br>
                {{ list.name }}<br>
                <br>

                <label>{{ $t("urllist.field_label_enable_scans") }}:</label><br>
                {{ list.enable_scans }}<br>
                <br>

                <label for="scan_type">{{ $t("urllist.field_label_scan_type") }}:</label><br>
                {{ list.scan_type }}<br>
                <br>

                <label for="automated_scan_frequency">{{
                        $t("urllist.field_label_automated_scan_frequency")
                    }}:</label><br>
                {{ list.automated_scan_frequency }}<br>
                <br>

            </div>
            <div slot="footer">
                <button class="altbutton" @click="stop_deleting()">{{ $t("delete_form.cancel") }}</button>
                &nbsp;
                <button class="defaultbutton modal-default-button" @click="confirm_deletion()">{{
                        $t("delete_form.ok")
                    }}
                </button>
            </div>
        </internet_nl_modal>

        <internet_nl_modal v-if="show_scan_now" @close="stop_scan_now()">
            <h3 slot="header">🔬 {{ $t("scan_now_form.title") }}</h3>
            <div slot="body">

                <server-response :response="scan_now_server_response"></server-response>

                <p v-html='$t("scan_now_form.message")'></p>

            </div>
            <div slot="footer">
                <button class="altbutton" @click="stop_scan_now()">{{ $t("scan_now_form.cancel") }}</button>
                &nbsp;
                <button class="defaultbutton modal-default-button"
                        :disabled="scan_now_confirmed"
                        @click="confirm_scan_now()">
                    <template v-if="!scan_now_confirmed">{{ $t("scan_now_form.ok") }}</template>
                    <template v-if="scan_now_confirmed">{{ $t("scan_now_form.starting") }}</template>
                </button>
            </div>
        </internet_nl_modal>

        <internet_nl_modal v-if="show_bulk_add_new" @close="stop_bulk_add_new()">
            <h3 slot="header">💖 {{ $t("bulk_add_form.title") }}</h3>
            <div slot="body">

                <server-response :response="bulk_add_new_server_response"
                                 :message="$t('bulk_add_form.' + bulk_add_new_server_response.message)"></server-response>

                <div v-if="bulk_add_new_server_response.success === true">
                    <ul>
                        <li v-if="bulk_add_new_server_response.data.duplicates_removed">{{
                                $t("bulk_add_form.removed_n_duplicates", [bulk_add_new_server_response.data.duplicates_removed])
                            }}
                        </li>
                        <li v-if="bulk_add_new_server_response.data.already_in_list">
                            {{ $t("bulk_add_form.ignored_n", [bulk_add_new_server_response.data.already_in_list]) }}
                        </li>
                        <li>{{
                                $t("bulk_add_form.added_n_to_list", [bulk_add_new_server_response.data.added_to_list])
                            }}
                        </li>
                    </ul>
                </div>

                <template v-if="bulk_add_new_server_response.data">
                    <span v-if="bulk_add_new_server_response.data.incorrect_urls.length">
                        ⚠️ <b>{{ $t("bulk_add_form.warning") }}</b><br>
                        <span v-html='$t("bulk_add_form.warning_message")'></span>:
                        <div style="width: 100%; background-color: #ffd9d9; height: 60px; overflow: scroll;">{{
                                bulk_add_new_server_response.data.incorrect_urls.join(', ')
                            }}</div>
                    </span>
                    <br>
                </template>

                <label for="edited_domains">{{ $t("bulk_add_form.domains_label") }}:</label>
                <textarea id="edited_domains" v-model="bulk_add_new_urls" style="width: 100%; height: 150px;"
                          :placeholder="$t('bulk_add_form.message')"></textarea>

                <br>
                <br>

            </div>
            <div slot="footer">
                <button class="altbutton" @click="stop_bulk_add_new()">{{ $t("bulk_add_form.cancel") }}</button>
                &nbsp;
                <template v-if="!bulk_add_new_loading">
                    <button class="defaultbutton modal-default-button" @click="bulk_add_new()">
                        {{ $t("bulk_add_form.ok") }}
                    </button>
                </template>
                <template v-else>
                    <button disabled="disabled" class="defaultbutton modal-default-button"><img
                        width="15" style="border-radius: 50%" src="/static/images/vendor/internet_nl/probe-animation.gif">
                        {{ $t("bulk_add_form.loading") }}
                    </button>
                </template>
            </div>
        </internet_nl_modal>
        <!-- This is already auto-refreshed by a watch, but we keep this as a backup solution for edge cases like
         the monitor page not loading or the used did not open the monitor page. -->
        <autorefresh :visible="false" :callback="get_scan_status_of_list" :refresh_per_seconds="600"></autorefresh>
    </article>
</template>

<script>
import sharedMessages from './../translations/dashboard.js'

export default {
    i18n: { // `i18n` option, setup locale info for component
        sharedMessages: sharedMessages,
        messages: {}
    },

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
            bulk_add_new_urls: "",
            bulk_add_new_server_response: {},
            bulk_add_new_loading: false,

            // everything to do with csv:
            view_csv: false,

            // scan now feature:
            show_scan_now: false,
            scan_now_server_response: {},
            scan_now_confirmed: false,
        }
    },
    props: {
        // Avoid mutating a prop directly since the value will be overwritten whenever the parent component re-renders.
        // Instead, use a data or computed property based on the prop's value. Prop being mutated: "list".
        // This is updated via a watch below. This allows for adding to the top of the list / real reactivity.
        initial_list: {type: Object, required: true},

        // To emulate and fix warnings that happen server side:
        maximum_domains: {type: Number, required: true, default: 10000},
    },
    watch: {
        initial_list: function (new_value) {
            this.list = new_value;
        },

        // support keep alive routing
        $route: function (to) {
            // https://router.vuejs.org/guide/essentials/dynamic-matching.html
            // If this param is set, and this list is the one requested, open this list.
            // todo: how to anchor-navigate to the part of the page where this list is?
            if (this.list.id === to.params.list) {
                this.open_list();

                // a little lesson in trickery
                location.hash = "#" + this.list.id;
            }
        },

        current_scan_status_from_scan_monitor: function (new_value, old_value) {
            // When the scan is cancelled via the UI, or another status update happens from the scan monitor
            // the scan state is updated automatically.

            // Do nothing when the state remains the same.
            if (new_value === old_value) {
                return
            }

            // various statusses that require a list update
            if (["finished", "cancelled", "requested"].includes(new_value)) {
                this.get_scan_status_of_list()
            }

        }
    },
    mounted: function () {
        if (window.location.href.split('/').length > 3) {
            // todo: this can be replaced by $route.params.report, which is much more readable.
            let get_id = window.location.href.split('/')[6];
            // can we change the select2 to a certain value?

            if (this.list.id === parseInt(get_id)) {
                this.open_list();
            }
        }
    },
    methods: {
        open_list: function () {
            this.get_urls();
            this.is_opened = true;
        },
        close_list: function () {
            this.is_opened = false;
        },
        get_urls: function () {
            this.loading = true;
            fetch(`${this.$store.state.dashboard_endpoint}/data/urllist_content/get/${this.list.id}/`, {credentials: 'include'}).then(response => response.json()).then(data => {
                this.urls = data.urls;
                this.loading = false;
                this.update_list_warnings();
            }).catch((fail) => {
                console.log('A loading error occurred: ' + fail);
            });
        },
        update_list_settings: function () {
            this.settings_loading = true;

            this.asynchronous_json_post(
                `${this.$store.state.dashboard_endpoint}/data/urllist/update_list_settings/`, this.list, (server_response) => {
                    this.settings_update_response = server_response;
                    this.settings_loading = false;

                    // The upcoming scan date has probably changed, and we want to reflect that in the UI.
                    this.list = server_response.data;
                    // make sure the cancel button goes to the last save.
                    this.old_list_settings = this.copy_values(this.list);

                    if (server_response.success) {
                        this.stop_editing_settings();
                    }
                });
        },
        // update the list with the most recent data regarding reports and scanning, not intruding on the UI experience
        // this can be autorefreshed to show the most current scanning and report information
        get_scan_status_of_list: function () {
            fetch(`${this.$store.state.dashboard_endpoint}/data/urllist/get_scan_status_of_list/${this.list.id}/`, {credentials: 'include'}).then(response => response.json()).then(data => {
                this.list['last_report_id'] = data['last_report_id'];
                this.list['scan_now_available'] = data['scan_now_available'];
                this.list['last_report_date'] = data['last_report_date'];
            }).catch((fail) => {
                console.log('A loading error occurred: ' + fail);
            });
        },
        start_editing_settings: function () {
            // keep an old value in memory. If the editing is canceled, the old value should be used.
            // here a weakness is of js is showing:
            // https://stackoverflow.com/questions/728360/how-do-i-correctly-clone-a-javascript-object
            // luckily we can use the simple approach...
            this.old_list_settings = this.copy_values(this.list);
            this.settings_update_response = {};
            this.show_list_settings = true;
        },
        stop_editing_settings: function () {
            this.show_list_settings = false;
            this.settings_update_response = {};
        },
        cancel_editing_settings: function () {
            this.list = this.copy_values(this.old_list_settings);
            this.stop_editing_settings();
        },
        copy_values: function (obj) {
            // does not copy methods.
            return JSON.parse(JSON.stringify(obj));
        },
        start_deleting: function () {
            this.show_deletion = true;
            this.delete_response = {};
        },
        stop_deleting: function () {
            this.show_deletion = false;
            this.delete_response = {};
        },
        confirm_deletion: function () {
            this.asynchronous_json_post(
                `${this.$store.state.dashboard_endpoint}/data/urllist/delete/`, {'id': this.list.id}, (server_response) => {
                    this.delete_response = server_response;

                    if (server_response.success) {
                        // remove / hide this thing...
                        this.$emit('removelist', this.list.id);
                        this.stop_deleting();
                    }
                }
            );
        },
        start_url_editing: function (list_id, url_id) {
            this.url_edit = '' + list_id + url_id;
            this.original_url_value = url_id;
            // after the item is rendered.
            this.$nextTick(() => document.getElementById(this.url_edit).focus());
        },
        url_is_edited: function (list_id, url_id) {
            return this.url_edit === '' + list_id + url_id
        },
        cancel_edit_url: function () {
            if (!this.url_edit)
                return;

            if (document.getElementById(this.url_edit)) {
                document.getElementById(this.url_edit).value = this.original_url_value;
            }
            this.url_edit = '';
        },
        get_url_edit_value: function () {
            return document.getElementById(this.url_edit).value;
        },
        remove_edit_url: function (list_id, url_id) {
            let data = {'list_id': list_id, 'url_id': url_id};
            this.asynchronous_json_post(
                `${this.$store.state.dashboard_endpoint}/data/urllist/url/delete/`, data, (server_response) => {
                    this.delete_response = server_response;

                    if (server_response.success) {
                        this.update_list_warnings();
                        this.urls.forEach(function (item, index, object) {
                            if (url_id === item.id) {
                                object.splice(index, 1)
                            }
                        });
                    }
                }
            );
        },
        save_edit_url: function (data) {
            /*
            * This is not a real 'save' but an add to list and create if it doesn't exist operation.
            * The save does not 'alter' the existing URL in the database. It will do some list operations.
            * */
            this.asynchronous_json_post(
                `${this.$store.state.dashboard_endpoint}/data/urllist/url/save/`, data, (server_response) => {
                    if (server_response.success === true) {
                        this.url_edit = '';
                        // and make sure the current url list is updated as well. Should'nt this be data bound and
                        // such?
                        this.urls.forEach(function (item, index, object) {
                            if (server_response.data.removed.id === item.id) {
                                object[index] = server_response.data.created;
                                // object.splice(index, 1);
                                // object.push(server_response.data.created)
                            }
                        });
                    } else {
                        document.getElementById(this.url_edit).value = this.original_url_value;
                    }
                }
            );

        },

        start_bulk_add_new: function () {
            this.show_bulk_add_new = true;
        },
        stop_bulk_add_new: function () {
            this.show_bulk_add_new = false;
            this.bulk_add_new_urls = "";

            this.bulk_add_new_server_response = {};

            // re-load the url list, as perhaps more information about endpoints is discovered.
            this.get_urls();
        },
        bulk_add_new: function () {
            let data = {'urls': this.bulk_add_new_urls, 'list_id': this.list.id};
            this.bulk_add_new_loading = true;

            this.asynchronous_json_post(
                `${this.$store.state.dashboard_endpoint}/data/urllist/url/add/`, data, (server_response) => {
                    // {'incorrect_urls': [], 'added_to_list': int, 'already_in_list': int}
                    this.bulk_add_new_server_response = server_response;
                    this.bulk_add_new_loading = false;

                    // Update the list of urls accordingly.
                    if (server_response.success) {
                        this.get_urls();
                    }

                    this.update_list_warnings()
                    // The select2 box is cleared when opened again. We don't need to clear it.
                }
            );
        },
        toggle_view_csv: function () {
            this.view_csv = !this.view_csv;
        },
        start_scan_now: function () {
            this.show_scan_now = true;
        },
        stop_scan_now: function () {
            this.show_scan_now = false;
            this.scan_now_server_response = {};
        },
        confirm_scan_now: function () {
            let data = {'id': this.list.id};

            // disable the button to prevent double scans (todo: api should fix this)
            this.scan_now_confirmed = true;

            this.asynchronous_json_post(
                `${this.$store.state.dashboard_endpoint}/data/urllist/scan_now/`, data, (server_response) => {
                    this.scan_now_server_response = server_response;

                    if (server_response.success) {
                        this.list.scan_now_available = false;
                        this.stop_scan_now();
                        this.scan_now_confirmed = false;
                    }

                    if (server_response.error) {
                        this.scan_now_confirmed = false;
                    }
                }
            );
        },

        update_list_warnings: function () {
            // The list warnings is not automatically updated. So we replicate the behavior here.
            if (this.urls.length > this.maximum_domains) {
                if (this.list.list_warnings.indexOf("WARNING_DOMAINS_IN_LIST_EXCEED_MAXIMUM_ALLOWED") === -1) {
                    this.list.list_warnings.push('WARNING_DOMAINS_IN_LIST_EXCEED_MAXIMUM_ALLOWED');
                }
            } else {
                let index = this.list.list_warnings.indexOf("WARNING_DOMAINS_IN_LIST_EXCEED_MAXIMUM_ALLOWED");
                if (index > -1) {
                    this.list.list_warnings.splice("WARNING_DOMAINS_IN_LIST_EXCEED_MAXIMUM_ALLOWED", 1);
                }
            }
        }
    },
    computed: {
        csv_value: function () {
            let urls = [];
            this.urls.forEach(function (item) {
                urls.push(item.url);
            });
            return urls.join(', ');
        },
        list_contains_warnings: function () {
            // As long as we don't have the urls loaded, the warnings as they are stand.
            // see update list warnings...
            if (!this.urls.length) {
                return this.list.list_warnings.length > 0;
            }

            return this.list.list_warnings.length > 0;
        },
        // can't seem to find the mapstate method the old school way:
        current_scan_status_from_scan_monitor: function () {
            if (this.$store.state.scan_monitor_data.length === 0)
                return "";

            // the first scan-monitor record where list_id is the same, is the one with the most recent state
            for (let i = 0; i < this.$store.state.scan_monitor_data.length; i++) {
                if (this.$store.state.scan_monitor_data[i].list_id === this.list.id) {
                    return this.$store.state.scan_monitor_data[i].state;
                }
            }

            // console.log("Probably no scan for this list...");
            return "";
        }
    },
}
</script>
<i18n>
{
    "en": {
        "button_labels": {
            "configure": "Configure",
            "add_domains": "Add domains",
            "scan_now": "Scan now",
            "scan_now_scanning": "Scanning",
            "scan_now_scanning_title": "The scan now option is available only once a day, when no scan is running.",
            "delete": "Delete",
            "view_csv": "View as .CSV file",
            "scanning_disabled": "Scanning disabled"
        },
        "about_this_list": {
            "header": "About this list",
            "number_of_domains": "Number of domains",
            "last_scan_started": "Last scan started",
            "still_running": "still running",
            "finished": "finished",
            "not_scanned_before": "Not scanned before",
            "type_of_scan_performed": "Type of scan performed",
            "scan_frequency": "Scan frequency",
            "next_scheduled_scan": "Next scheduled scan",
            "scanning_disabled": "Scanning of this list is disabled.",
            "latest_report": "Latest report",
            "disabled": "disabled",
            "every half year": "every half year",
            "at the start of every quarter": "at the start of every quarter",
            "every 1st day of the month": "every first day of the month",
            "twice per month": "every two weeks, from the first day of the month"
        },
        "domains": {
            "header": "Domains",
            "intro": "These domains will be included in the scan. Their eligibility for scanning is checked just before requesting the scan, the information shown here may be outdated.",
            "start_editing_url": "Edit {0}.",
            "cancel_editing_url": "Cancel editing and store the original value: {0}",
            "eligeble_mail": "{0} is eligeble for e-mail scans",
            "unknown_eligeble_mail": "Not yet known if {0} is scanable for mail",
            "not_eligeble_mail": "{0} is not eligeble for e-mail scans. Will be checked again when starting a scan.",
            "eligeble_web": "{0} is eligeble for web scans",
            "unknown_eligeble_web": "Not yet known if {0} is scannable for web",
            "not_eligeble_web": "{0} is not eligeble for web scans. Will be checked again when starting a scan.",
            "save_edited_url": "Save changes, the change will be applied to {0}.",
            "delete_edited_url": "Delete {0} from this list.",
            "button_labels": {
                "save": "Save",
                "cancel": "Cancel",
                "remove": "Remove"
            }
        },
        "warnings": {
            "domains_exceed_maximum": "The amount of domains in this list exceeds the maximum of {0}. Scanning is paused."
        },
        "edit_form": {
            "title": "Configure list settings",
            "cancel": "Cancel",
            "ok": "Update"
        },
        "delete_form": {
            "title": "Delete list",
            "message": "Are you sure you want to delete this list? Deleting this list cannot be undone.",
            "cancel": "No, take me back",
            "ok": "Yes, Delete"
        },
        "scan_now_form": {
            "title": "Confirm to scan",
            "message": "Your scan will start in a moment. You can cancel a running scan at any time in the scan monitor.",
            "cancel": "Cancel",
            "ok": "Scan now",
            "starting": "Starting..."
        },
        "bulk_add_form": {
            "title": "Add domains",
            "domains_label": "Add domains in the text field below",
            "message": "Domains are separated by a comma, space or new line. These can be mixed. For example: \n\ninternet.nl, dashboard.internet.nl\nexample.com www.example.com, \n\nhttps://my.example.com:80/index.html",
            "ok": "Add the above domains to the list",
            "cancel": "Close",
            "status": "Status",
            "nothing_added": "nothing added yet.",
            "added_n_to_list": "{0} domains added to this list.",
            "removed_n_duplicates": "{0} duplicates removed from the input.",
            "ignored_n": "{0} domains are already in this list.",
            "warning": "Warning!",
            "warning_message": "Some domains where not added because they are in an incorrect format. The following domains where not added",
            "loading": "Domains are being processed",
            "add_domains_valid_urls_added": "New domains have processed, see the status report for details.",
            "add_domains_list_does_not_exist": "This list does not exist."
        }
    },
    "nl": {
        "button_labels": {
            "configure": "Instellingen",
            "add_domains": "Domeinen toevoegen",
            "scan_now": "Nu scannen",
            "scan_now_scanning": "Aan het scannen",
            "scan_now_scanning_title": "Nu scannen is alleen beschikbaar als er geen scan draait, en kan maximaal 1x per dag worden aangeroepen.",
            "delete": "Verwijder",
            "view_csv": "Bekijk CSV bestand",
            "scanning_disabled": "Scans uitgeschakeld"
        },
        "about_this_list": {
            "header": "Over deze lijst",
            "number_of_domains": "Aantal domeinen",
            "last_scan_started": "Laatste scan gestart op",
            "still_running": "loopt nog",
            "finished": "afgerond",
            "not_scanned_before": "Niet eerder gescand",
            "type_of_scan_performed": "Soort scan",
            "scan_frequency": "Scan frequentie",
            "next_scheduled_scan": "Volgende ingeplande scan",
            "scanning_disabled": "Scannen van deze lijst is uitgeschakeld.",
            "latest_report": "Meest actuele rapportage",
            "disabled": "uitgeschakeld",
            "every half year": "ieder half jaar",
            "at the start of every quarter": "aan het begin van ieder kwartaal",
            "every 1st day of the month": "elke eerste dag van de maand",
            "twice per month": "om de twee weken, vanaf de 1e van de maand"
        },
        "domains": {
            "header": "Domeinen",
            "intro": "Deze domeinen worden meegenomen in een scan. De mogelijkheid om te scannen wordt voor aanvang van de scan bijgewerkt. De iconen geven een beeld van de bereikbaarheid van deze domeinen, maar deze status kan mogelijk anders zijn bij een scan.",
            "eligeble_mail": "E-mail scannen is mogelijk",
            "start_editing_url": "Bewerk {0}.",
            "unknown_eligeble_mail": "Onbekend of E-mail scannen mogelijk is",
            "not_eligeble_mail": "Kan geen E-mail scan uitvoeren (wordt opnieuw gecheckt bij het starten van de scan)",
            "eligeble_web": "Web scan is mogelijk",
            "unknown_eligeble_web": "Niet bekend of het mogelijk is een web scan uit te voeren",
            "not_eligeble_web": "Web scan kan niet worden uitgevoerd. Dit wordt opnieuw gecheckt bij het starten van de scan.",
            "button_labels": {
                "save": "Opslaan",
                "cancel": "Annuleren",
                "remove": "Verwijderen"
            }
        },
        "warnings": {
            "domains_exceed_maximum": "Het aantal domeinen in deze lijst is meer dan het maximum aantal van {0}. Scanning is gepauzeerd."
        },
        "edit_form": {
            "title": "Lijst instellingen",
            "cancel": "Annuleer",
            "ok": "Opslaan"
        },
        "delete_form": {
            "title": "Lijst verwijderen",
            "message": "Weet u zeker dat u deze lijst wil verwijderen? Dit kan niet ongedaan worden gemaakt.",
            "cancel": "Nee, niet verwijderen",
            "ok": "Ja, verwijder"
        },
        "scan_now_form": {
            "title": "Nu scannen?",
            "message": "De scan start binnen enkele ogenblikken en is te volgen op de scan monitor. In de scan monitor kan de scan alsnog worden gestopt.",
            "cancel": "Annuleer",
            "ok": "Nu scannen",
            "starting": "Opstarten..."
        },
        "bulk_add_form": {
            "title": "Domeinen toevoegen",
            "domains_label": "Voer nieuwe domeinen in:",
            "message": "Domeinen worden gescheiden door een komma, spatie, nieuwe regel. Deze mogen ook door elkaar worden gebruikt. Bijvoorbeeld: \n\ninternet.nl, dashboard.internet.nl\nexample.com www.example.com\n\nhttps://my.example.com:80/index.html",
            "ok": "Voeg bovenstaande domeinen toe aan de lijst",
            "status": "Status",
            "cancel": "Sluiten",
            "nothing_added": "nog niets toegevoegd.",
            "added_n_to_list": "{0} domeinen zijn aan de lijst toegevoegd.",
            "removed_n_duplicates": "{0} dubbel ingevoerde domeinen zijn overgeslagen.",
            "ignored_n": "{0} domeinen zitten al in de lijst.",
            "warning": "Waarschuwing!",
            "warning_message": "Sommige domeinen zijn niet in een geldig formaat. Controleer de volgende domeinen en probeer het opnieuw:",
            "loading": "Domeinen worden verwerkt",
            "add_domains_valid_urls_added": "Nieuwe domeinen zijn verwerkt, zie het statusoverzicht voor details.",
            "add_domains_list_does_not_exist": "Deze lijst bestaat niet."
        }
    }
}
</i18n>