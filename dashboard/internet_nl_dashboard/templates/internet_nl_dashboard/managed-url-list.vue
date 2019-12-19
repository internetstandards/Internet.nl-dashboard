{% verbatim %}
<template type="x-template" id="managed-url-list">
    <article class="managed-url-list block fullwidth">
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
                    {{ $t("button_labels.configure") }}</button>
                <button @click="start_bulk_add_new()">
                    <span role="img" :aria-label="$t('icons.bulk_add_new')">💖</span>
                    {{ $t("button_labels.add_domains") }}</button>
                <template v-if="urls.length">
                    <template v-if="list.enable_scans">
                        <button v-if="list.scan_now_available" @click="start_scan_now()">
                            <span role="img" :aria-label="$t('icons.scan')">🔬</span>
                            {{ $t("button_labels.scan_now") }}
                        </button>

                        <button v-if="!list.scan_now_available && !list.last_scan_finished" disabled="disabled"
                        :title='$t("button_labels.scan_now_scanning")'>
                            <img width="15" style="border-radius: 50%" src="/static/images/vendor/internet_nl/probe-animation.gif">
                            {{ $t("button_labels.scan_now_scanning") }}
                        </button>

                        <button v-if="!list.scan_now_available && list.last_scan_finished" disabled="disabled"
                        :title='$t("button_labels.timeout_for_24_hours")'>
                            <img width="15" style="border-radius: 50%" src="/static/images/vendor/internet_nl/probe-animation.gif">
                            {{ $t("button_labels.timeout_for_24_hours") }}
                        </button>
                    </template>
                    <button v-if="!list.enable_scans" disabled="disabled"
                    :title='$t("button_labels.scanning_disabled")'>
                        <span role="img" :aria-label="$t('icons.scan')">🔬</span>
                        {{ $t("button_labels.scanning_disabled") }}
                    </button>
                </template>
                <button @click="start_deleting()">🔪 {{ $t("button_labels.delete") }}</button>
            </div>
        </span>
        <br>

        <div v-if="is_opened">
            <h3>{{ $t("about_this_list.header") }}</h3>
            <p>
                <span v-if="list.last_scan">
                    {{ $t("about_this_list.last_scan_started") }}: {{ humanize_date(list.last_scan) }}.
                    <span v-if="!list.last_scan_finished">({{ $t("about_this_list.still_running") }})</span>
                    <span v-if="list.last_scan_finished">({{ $t("about_this_list.finished") }})</span>
                </span>
                <span v-if="!list.last_scan">
                    {{ $t("about_this_list.last_scan_started") }}: {{ $t("about_this_list.not_scanned_before") }}.
                </span>
                <template class="scan-configuration">
                    <div v-if="list.enable_scans">
                        {{ $t("about_this_list.type_of_scan_performed") }}:
                        <span title="Mail scans will be performed" v-if="list.enable_scans && list.scan_type === 'mail'">
                            <img src="/static/images/vendor/internet_nl/icon-emailtest.svg" style="height: 16px;">
                        {{ list.scan_type }}</span>
                        <span title="Web scans will be performed" v-if="list.enable_scans && list.scan_type === 'web'">
                            <img src="/static/images/vendor/internet_nl/icon-website-test.svg" style="height: 16px;">
                            {{ list.scan_type }}</span>
                        <span title="No scans will be performed" v-if="!list.enable_scans">🚫 {{ list.scan_type }}</span><br>
                        <span v-if="urls">
                            {{ $t("about_this_list.number_of_domains") }}: {{urls.length}}
                        </span>
                        <span v-if="!urls">
                            {{ $t("about_this_list.number_of_domains") }}: {{list.num_urls}}
                        </span><br>
                        {{ $t("about_this_list.scan_frequency") }}: {{ list.automated_scan_frequency }} <br>
                        <div v-if="list.automated_scan_frequency !== 'disabled'">
                            {{ $t("about_this_list.next_scheduled_scan") }}: {{ humanize_date(list.scheduled_next_scan) }} <br>
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
                    <span role="img" :aria-label="$t('icons.list_warning')">⚠️</span>{{ $t("warnings.domains_exceed_maximum", [this.maximum_domains]) }}
                </div>
            </template>
            <br>

            <div v-if="!urls.length">
                <button @click="start_bulk_add_new()">💖 {{ $t("button_labels.add_domains") }}</button>
            </div>

            <loading :loading="loading"></loading>

            <ul style="column-count: 2; list-style: none;">
                <li v-for="url in urls">

                    <template v-if="list.scan_type === 'mail'">
                        <span v-if="url.has_mail_endpoint === true" :title="$t('domains.eligeble_mail', [url.url])">
                            <span role="img" :aria-label="$t('domains.eligeble_mail', [url.url])">🌍</span>
                            <!-- <a :href="'https://www.internet.nl/mail/' + url.url + '/'" target="_blank"></a> -->
                        </span>
                        <span v-if="url.has_mail_endpoint === 'unknown'" :title="$t('domains.unknown_eligeble_mail', [url.url])">
                            <span role="img" :aria-label="$t('domains.unknown_eligeble_mail', [url.url])">❓</span>
                        </span>
                        <span v-if="url.has_mail_endpoint === false" :title="$t('domains.not_eligeble_mail', [url.url])">
                            <span role="img" :aria-label="$t('domains.not_eligeble_mail', [url.url])">🚫</span>
                        </span>
                    </template>

                    <template v-if="list.scan_type === 'web'">
                        <span v-if="url.has_web_endpoint === true" :title="$t('domains.not_eligeble_web', [url.url])">
                            <!-- <a :href="'https://www.internet.nl/site/' + url.url + '/'" target="_blank"></a> -->
                            <span role="img" :aria-label="$t('domains.not_eligeble_web', [url.url])">🌍</span>
                        </span>
                        <span v-if="url.has_web_endpoint === 'unknown'" :title="$t('domains.unknown_eligeble_web', [url.url])">
                            <span role="img" :aria-label="$t('domains.unknown_eligeble_web', [url.url])">❓</span>
                        </span>
                        <span v-if="url.has_web_endpoint === false" :title="$t('domains.not_eligeble_web', [url.url])">
                            <span role="img" :aria-label="$t('domains.not_eligeble_web', [url.url])">🚫</span>
                        </span>
                    </template>


                    <button style="font-size: 12px;" v-if="url_edit !== '' + list.id + url.url" class="inline-edit" :title="$t('domains.start_editing_url', [url.url])" @click="start_url_editing(list.id, url.url)" aria-expanded="false">
                        🖊
                        <span class="visuallyhidden">{{ $t('domains.start_editing_url', [url.url]) }}</span>
                    </button>
                    <button style="font-size: 12px;" v-if="url_edit === '' + list.id + url.url" class="inline-edit" :title="$t('domains.cancel_editing_url', [url.url])" @click="cancel_edit_url(list.id, url.url)" aria-expanded="true">
                        🖊
                        <span class="visuallyhidden">{{ $t('domains.cancel_editing_url', [url.url]) }}</span>
                    </button>

                    <template v-if="url.subdomain">
                        <a v-if="!url_is_edited(list.id, url.url)" @click="start_url_editing(list.id, url.url)">{{ url.subdomain }}.<b>{{ url.domain }}.{{ url.suffix }}</b></a>
                    </template>
                    <template v-if="!url.subdomain">
                        <a v-if="!url_is_edited(list.id, url.url)" @click="start_url_editing(list.id, url.url)"><b>{{ url.domain }}.{{ url.suffix }}</b></a>
                    </template>

                    <span class="inline-edit" v-if="url_is_edited(list.id, url.url)">
                            <input autofocus :placeholder="url.url" :value="url.url" :id="'' + list.id + url.url">
                            <button @click="save_edit_url({'list_id': list.id,'url_id': url.id, 'new_url_string': get_url_edit_value()})" :title="$t('domains.save_edited_url', [url.url])">
                                {{ $t("domains.button_labels.save") }}
                                <span class="visuallyhidden">{{ $t('domains.save_edited_url', [url.url]) }}</span>
                            </button>
                            <button @click="cancel_edit_url()" :title="$t('domains.cancel_editing_url', [url.url])">
                                {{ $t("domains.button_labels.cancel") }}
                                <span class="visuallyhidden">{{ $t('domains.cancel_editing_url', [url.url]) }}</span>
                            </button>
                            <!-- The remove is real, as it will only remove 1 items -->
                            <button @click="remove_edit_url(list.id, url.id)"  :title="$t('domains.delete_edited_url', [url.url])">
                                {{ $t("domains.button_labels.remove") }}
                                <span class="visuallyhidden">{{ $t('domains.delete_edited_url', [url.url]) }}</span>
                            </button>
                    </span>
                </li>
            </ul>
            <br>
            <button v-if="urls.length" @click="toggle_view_csv()" value="load">📋 {{ $t("button_labels.view_csv") }}</button><br>
            <textarea v-if="view_csv" class="view-csv" :value="csv_value"></textarea>
        </div>

        <!-- modal dialogs are below the content to make sure the tab order stays working. -->
        <modal v-if="show_list_settings" @close="cancel_editing_settings()">
            <h1 slot="header">🖊 {{ $t("edit_form.title") }}</h1>
            <div slot="body">

                <server-response :response="settings_update_response"></server-response>

                <label for="name">{{ $t("urllist.field_label_name") }}:</label><br>
                <input id="name" type="text" maxlength="120" v-model="list.name"><br><br>

                <label for="scan_type">{{ $t("urllist.field_label_scan_type") }}:</label><br>
                <select id="scan_type" v-model="list.scan_type">
                    <option value="web">{{ $t("urllist.scan_type_web") }}</option>
                    <option value="mail">{{ $t("urllist.scan_type_mail") }}</option>
                </select><br><br>

                <label for="automated_scan_frequency">{{ $t("urllist.field_label_automated_scan_frequency") }}:</label><br>
                <select id="automated_scan_frequency" v-model="list.automated_scan_frequency">
                    <option value="disabled">{{ $t("urllist.automated_scan_frequency.disabled") }}</option>
                    <option value="every half year">{{ $t("urllist.automated_scan_frequency.every_half_year") }}</option>
                    <option value="at the start of every quarter">{{ $t("urllist.automated_scan_frequency.every_quarter") }}</option>
                    <option value="every 1st day of the month">{{ $t("urllist.automated_scan_frequency.every_month") }}</option>
                    <option value="twice per month">{{ $t("urllist.automated_scan_frequency.twice_per_month") }}</option>
                </select>

            </div>
            <div slot="footer">
                <button @click="cancel_editing_settings()">{{ $t("edit_form.cancel") }}</button>
                <button class="modal-default-button" @click="update_list_settings()">{{ $t("edit_form.ok") }}</button>
            </div>
        </modal>

        <modal v-if="show_deletion" @close="stop_deleting()">
            <h1 slot="header">{{ $t("delete_form.title") }}</h1>
            <div slot="body">

                <server-response :response="delete_response"></server-response>

                <p class="dialog_warning">{{ $t("delete_form.message") }}</p>

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
                <button @click="stop_deleting()">{{ $t("delete_form.cancel") }}</button>
                <button class="modal-default-button" @click="confirm_deletion()">{{ $t("delete_form.ok") }}</button>
            </div>
        </modal>

        <modal v-if="show_scan_now" @close="stop_scan_now()">
            <h1 slot="header">{{ $t("scan_now_form.title") }}</h1>
            <div slot="body">

                <server-response :response="scan_now_server_response"></server-response>

                <p v-html='$t("scan_now_form.message")'></p>

            </div>
            <div slot="footer">
                <button @click="stop_scan_now()">{{ $t("scan_now_form.cancel") }}</button>
                <button class="modal-default-button"
                        :disabled="scan_now_confirmed"
                        @click="confirm_scan_now()">
                    <template v-if="!scan_now_confirmed">{{ $t("scan_now_form.ok") }}</template>
                    <template v-if="scan_now_confirmed">{{ $t("scan_now_form.starting") }}</template>
                </button>
            </div>
        </modal>

        <modal v-if="show_bulk_add_new" @close="stop_bulk_add_new()">
            <h1 slot="header">{{ $t("bulk_add_form.title") }}</h1>
            <div slot="body">

                <server-response :response="bulk_add_new_server_response"></server-response>

                <p>{{ $t("bulk_add_form.message") }}</p>

                <select2-tags-widget v-model="bulk_add_new_urls"></select2-tags-widget>

                <div v-if="bulk_add_new_server_response">
                    <span v-if="bulk_add_new_server_response.success === true">
                        {{ $t("bulk_add_form.status") }}:
                        {{ $t("bulk_add_form.added_n_to_list", [bulk_add_new_server_response.data.added_to_list]) }}

                        <span v-if="bulk_add_new_server_response.data.already_in_list">
                            {{ $t("bulk_add_form.ignored_n", [bulk_add_new_server_response.data.already_in_list]) }}<br>
                        </span>
                        <br>
                        <span v-if="bulk_add_new_server_response.data.incorrect_urls.length">
                            <br><b>{{ $t("bulk_add_form.warning") }}</b><br>
                            <span v-html='$t("bulk_add_form.warning_message")'></span>
                            {{ bulk_add_new_server_response.data.incorrect_urls.join(', ') }}<br>
                        </span>
                    </span>
                </div>
                <div v-if="!bulk_add_new_server_response.message">
                    <p>{{ $t("bulk_add_form.status") }}: {{ $t("bulk_add_form.nothing_added") }}.</p>
                </div>
                <br>
                <button class="modal-default-button" @click="bulk_add_new()">{{ $t("bulk_add_form.ok") }}</button>

            </div>
            <div slot="footer">
            </div>
        </modal>
    </article>
</template>
{% endverbatim %}

<script>
Vue.component('managed-url-list', {
    i18n: { // `i18n` option, setup locale info for component
        messages: {
            en: {

                button_labels: {
                    configure: 'Configure',
                    add_domains: 'Add domains',
                    scan_now: 'Scan now',
                    scan_now_scanning: 'Scanning',
                    scan_now_scanning_title: 'The scan now option is available only once a day, when no scan is running.',
                    delete: 'Delete',
                    view_csv: 'View .csv',
                    timeout_for_24_hours: 'Max 1 scan/day',
                    scanning_disabled: 'Scanning disabled',
                },

                about_this_list: {
                    header: 'About this list',
                    number_of_domains: "Number of domains",
                    last_scan_started: 'Last scan started',
                    still_running: 'still running',
                    finished: 'finished',
                    not_scanned_before: 'Not scanned before',
                    type_of_scan_performed: 'Type of scan performed',
                    scan_frequency: 'Scan frequency',
                    next_scheduled_scan: 'Next scheduled scan',
                    scanning_disabled: 'Scanning of this list is disabled.',
                    latest_report: 'Latest report',
                },

                domains: {
                    header: 'Domains',
                    intro: "These domains will be included in the scan. Their eligibility for scanning is checked just " +
                        "before requesting the scan, the information shown here may be outdated.",
                    start_editing_url: 'Edit {0}.',
                    cancel_editing_url: 'Cancel editing and store the original value: {0}',
                    eligeble_mail: '{0} is eligeble for e-mail scans',
                    unknown_eligeble_mail: 'Not yet known if {0} is scanable for mail',
                    not_eligeble_mail: '{0} is not eligeble for e-mail scans. Will be checked again when starting a scan.',
                    eligeble_web: '{0} is eligeble for web scans',
                    unknown_eligeble_web: 'Not yet known if {0} is scannable for web',
                    not_eligeble_web: '{0} is not eligeble for web scans. Will be checked again when starting a scan.',
                    save_edited_url: 'Save changes, the change will be applied to {0}.',
                    delete_edited_url: 'Delete {0} from this list.',

                    button_labels: {
                        save: 'Save',
                        cancel: 'Cancel',
                        remove: 'Remove',
                    }
                },

                warnings: {
                    domains_exceed_maximum: 'The amount of domains in this list exceeds the maximum of {0}. Scanning is paused.',
                },

                edit_form: {
                    title: 'Edit list settings',
                    cancel: 'Cancel',
                    ok: 'Update'
                },

                delete_form: {
                    title: 'Delete list',
                    message: 'Are you sure you want to\n' +
                        '                delete this list? Deleting this list cannot be undone.',
                    cancel: 'No, take me back',
                    ok: 'Yes, Delete'
                },

                scan_now_form: {
                    title: 'Confirm to scan now',
                    message: 'To start a scan now, please take the following in consideration: <br>' +
                        'A scan can only be started once a day, and only when no scan is already running. Note that a scan cannot be cancelled.',
                    cancel: 'Cancel',
                    ok: 'Scan now',
                    starting: 'Starting...',
                },

                bulk_add_form: {
                    title: 'Bulk add domains',
                    message: 'You can add many domains in one go. To do this, seperate each domain with a comma.',
                    ok: 'Add the above domains to the list',
                    status: 'Status',
                    nothing_added: 'nothing added yet.',
                    added_n_to_list: 'Added {0} domains to this list.',
                    ignored_n: 'Additionally, {0} domains have been\n' +
                        '                            ignored as they are already in this list.',
                    warning: 'Warning!',
                    warning_message: 'Some domains where not added because they are in an incorrect format. <br>\n' +
                        '                            The following domains where not added',
                }
            },
            nl: {
                button_labels: {
                    configure: 'Instellingen',
                    add_domains: 'Domeinen toevoegen',
                    scan_now: 'Nu scannen',
                    scan_now_scanning: 'Aan het scannen',
                    scan_now_scanning_title: 'Nu scannen is alleen beschikbaar als er geen scan draait, en kan maximaal 1x per dag worden aangeroepen.',
                    delete: 'Verwijder',
                    view_csv: 'Bekijk.csv',
                    timeout_for_24_hours: 'Max 1 scan/dag',
                    scanning_disabled: 'Scans uitgeschakeld',
                },

                about_this_list: {
                    header: 'Over deze lijst',
                    number_of_domains: "Aantal domeinen",
                    last_scan_started: 'Laatste scan gestart op',
                    still_running: 'loopt nog',
                    finished: 'afgerond',
                    not_scanned_before: 'Niet eerder gescand',
                    type_of_scan_performed: 'Soort scan',
                    scan_frequency: 'Scan frequentie',
                    next_scheduled_scan: 'Volgende ingeplande scan',
                    scanning_disabled: 'Scannen van deze lijst is uitgeschakeld.',
                    latest_report: 'Meest actuele rapportage',
                },

                domains: {
                    header: 'Domeinen',
                    eligeble_mail: 'E-mail scannen is mogelijk',
                    unknown_eligeble_mail: 'Onbekend of E-mail scannen mogelijk is',
                    not_eligeble_mail: 'Kan geen E-mail scan uitvoeren (wordt opnieuw gecheckt bij het starten van de scan)',
                    eligeble_web: 'Web scan is mogelijk',
                    unknown_eligeble_web: 'Niet bekend of het mogelijk is een web scan uit te voeren',
                    not_eligeble_web: 'Web scan kan niet worden uitgevoerd. Dit wordt opnieuw gecheckt bij het starten van de scan.',

                    button_labels: {
                        save: 'Opslaan',
                        cancel: 'Annuleren',
                        remove: 'Verwijderen',
                    }
                },

                warnings: {
                    domains_exceed_maximum: 'Het aantal domeinen in deze lijst is meer dan het maximum aantal van {0}. Scanning is gepauzeerd.',
                },

                edit_form: {
                    title: 'Lijst instellingen',
                    cancel: 'Annuleer',
                    ok: 'Opslaan'
                },

                delete_form: {
                    title: 'Lijst verwijderen',
                    message: 'Weet u zeker dat u deze lijst wil verwijderen? Dit kan niet ongedaan worden gemaakt.',
                    cancel: 'Nee, niet verwijderen',
                    ok: 'Ja, verwijder'
                },

                scan_now_form: {
                    title: 'Bevestig om opnieuw te scannen',
                    message: 'Een scan die nu wordt gestart heeft de volgende eigenschappen: <br>' +
                        'Een handmatige scan kan eens per dag worden gestart, mits er nog geen scan wordt uitgevoerd op deze lijst.',
                    cancel: 'Annuleer',
                    ok: 'Nu scannen',
                    starting: 'Opstarten...',
                },

                bulk_add_form: {
                    title: 'Toevoegen van domeinen',
                    message: 'Voeg hieronder een of meerdere domeinen toe, gescheiden door een komma.',
                    ok: 'Voeg bovenstaande domeinen toe aan de lijst',
                    status: 'Status',
                    nothing_added: 'nog niets toegevoegd.',
                    added_n_to_list: 'Er zijn {0} domeinen aan de lijst toegevoegd.',
                    ignored_n: 'Verder zijn er {0} domeinen genegeerd omdat ze al in de lijst zaten.',
                    warning: 'Waarschuwing!',
                    warning_message: 'Sommige domeinen zijn niet in een geldig formaat. Controleer de volgende domeinen en' +
                        'probeer het opnieuw:',
                }
            }
        }
    },
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
        initial_list: function(new_value){
            this.list = new_value;
        }
    },
    mounted: function(){
        if (window.location.href.split('/').length > 3) {
            // todo: this can be replaced by $route.params.report, which is much more readable.
            let get_id = window.location.href.split('/')[6];
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

            // disable the button to prevent double scans (todo: api should fix this)
            this.scan_now_confirmed = true;

            this.asynchronous_json_post(
                '/data/urllist/scan_now/', data, (server_response) => {
                    this.scan_now_server_response = server_response;

                    if (server_response.success) {
                        this.list.scan_now_available = false;
                        this.stop_scan_now();
                        this.scan_now_confirmed = false;
                    }

                    if (server_response.error){
                        this.scan_now_confirmed = false;
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
        },
        list_contains_warnings: function(){
            // As long as we don't have the urls loaded, the warnings as they are stand.
            console.log("checking warnings");
            if (!this.urls.length){
                return this.list.list_warnings.length > 0;
            }

            //
            // The list warnings is not automatically updated. So we replicate the behavior here.
            if (this.urls.length > this.maximum_domains){
                console.log("adding WARNING_DOMAINS_IN_LIST_EXCEED_MAXIMUM_ALLOWED");
                if (this.list.list_warnings.indexOf("WARNING_DOMAINS_IN_LIST_EXCEED_MAXIMUM_ALLOWED") === -1) {
                    console.log("adding WARNING_DOMAINS_IN_LIST_EXCEED_MAXIMUM_ALLOWED really");
                    this.list.list_warnings.push('WARNING_DOMAINS_IN_LIST_EXCEED_MAXIMUM_ALLOWED');
                }
            } else {
                console.log("Removing WARNING_DOMAINS_IN_LIST_EXCEED_MAXIMUM_ALLOWED");
                let index = this.list.list_warnings.indexOf("WARNING_DOMAINS_IN_LIST_EXCEED_MAXIMUM_ALLOWED");
                if (index > -1) {
                    console.log("Removing WARNING_DOMAINS_IN_LIST_EXCEED_MAXIMUM_ALLOWED really");
                   this.list.list_warnings.splice("WARNING_DOMAINS_IN_LIST_EXCEED_MAXIMUM_ALLOWED", 1);
                }
            }

            return this.list.list_warnings.length > 0;
        }
    },
});
</script>
<!--
Todo: use vue-i18n-loader to support editing text in babeledit.
<i18n>
{
	"nl-NL": {
        "domain_management": {
            "button_labels": {
                "configure": "Configure",
                "add_domains": "Add domains",
                "scan_now": "Scan now",
                "scan_now_scanning": "Scanning",
                "scan_now_scanning_title": "The scan now option is available only once a day, when no scan is running.",
                "delete": "Delete",
                "view_csv": "View .csv",
                "timeout_for_24_hours": "Max 1 scan/day",
                "scanning_disabled": "Scanning disabled"
            }
        }
	}
}
</i18n>
-->