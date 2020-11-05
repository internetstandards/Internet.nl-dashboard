// Note that there is a little hate going on with multiple vue instances.
// See here: https://github.com/LinusBorg/portal-vue/issues/201#issuecomment-484452281
// This explains why there are some extra definitions in the bundler thingies.
import Vue from 'vue'
import Vuex from 'vuex'
import createPersistedState from "vuex-persistedstate";
import VueRouter from 'vue-router'
import VueI18n from 'vue-i18n'
import vSelect from 'vue-select'
import {Tabs, Tab} from 'vue-tabs-component';
import autorefresh from './components/autorefresh'
import loading from './components/loading'
import internet_nl_modal from './components/modal'
import server_response from './components/server-response'
import Login from './components/Login'
import DomainListManager from './components/domains/DomainListManager'
import SpreadsheetUpload from './components/domains/SpreadsheetUpload'
import ScanMonitor from './components/scans/ScanMonitor'
import Report from './components/reports/Report'
import SwitchAccount from './components/admin/SwitchAccount'
import InstantAddAccount from './components/admin/InstantAddAccount'
import Account from './components/account/Account'
import Demo from './components/Demo'
import Unsubscribe from './components/mail/Unsubscribe'
import collapse_panel from './components/collapse_panel'
import App from './App'
import Beta from './components/beta'
// https://stackoverflow.com/questions/50925793/proper-way-of-adding-css-file-in-vue-js-application
import './assets/css/styles.scss';
import PortalVue from 'portal-vue'
import { BootstrapVue } from 'bootstrap-vue'
// Requiring moment is a little bit evil:
// https://github.com/brockpetrie/vue-moment/issues/121
import VueMoment from 'vue-moment';
import moment from 'moment'
Vue.use(VueMoment, { moment });

Vue.component('v-select', vSelect);
Vue.component('tabs', Tabs);
Vue.component('tab', Tab);
Vue.use(PortalVue)
Vue.use(VueI18n)
Vue.use(VueRouter)

Vue.use(Vuex);
Vue.use(BootstrapVue)

Vue.component('autorefresh', autorefresh)
Vue.component('loading', loading)
Vue.component('internet_nl_modal', internet_nl_modal)
Vue.component('server-response', server_response)
Vue.component('collapse-panel', collapse_panel)

Vue.config.productionTip = false

var MatomoTracker = require('matomo-tracker');
var matomo = new MatomoTracker(2, '//matomo.internet.nl/matomo.php');
matomo.on('error', function (err) {
    console.log('error tracking request: ', err);
});

const i18n = new VueI18n({
    locale: 'en',
    fallbackLocale: 'en',
    silentFallbackWarn: true,
    // it's required this is called messages.
    messages: {
        en: {
            "title_domains": "Internet.nl Dashboard / Domains",
        },
        nl: {
            "title_domains": "Internet.nl Dashboard / Domeinen",
        }
    },
    sharedMessages: {}
});

const store = new Vuex.Store({
    state: {
        // -2 is used, to be able to distinct for the first upload and zero uploads.
        uploads_performed: -2,

        // the scan monitor is used to determine if lists of domains or the reports dropdowns need to be
        // updated. If the scan monitor is not loaded, a standard autorefresh strategy is used.
        scan_monitor_data: [],

        // active language:
        locale: 'en',

        // It's always port 8000.
        dashboard_endpoint: process.env.VUE_APP_DJANGO_PATH,

        // login states
        user: {
            is_authenticated: false,
            is_superuser: false,
        },

        // Visible metrics in report, report graphs and visible metrics configuration pane
        visible_metrics: {},
    },

    mutations: {
        // this.$store.commit('set_uploads_performed', 0)
        set_uploads_performed(state, value) {
            state.uploads_performed = value;
        },
        update_scan_monitor_data(state, value) {
            state.scan_monitor_data = value;
        },
        set_locale(state, value) {
            state.locale = value;
        },
        set_dashboard_endpoint(state, value) {
            state.dashboard_endpoint = value;
        },
        set_user(state, value) {
            state.user = value;
        },
        set_visible_metrics(state, value) {
            state.visible_metrics = value;
        }
    },

    plugins: [createPersistedState()],
});

const routes = [
    // todo: Make page title translations...
    {path: '/login', component: Login, name: "login", meta: {title: 'Internet.nl Dashboard / Login'}},
    {
        path: '/domains/list/:list',
        component: DomainListManager,
        name: 'numbered_lists',
        meta: {title: i18n.t("title_domains")}
    },
    {
        path: '/domains',
        component: DomainListManager,
        name: 'domains',
        meta: {title: i18n.t("title_domains")},
        alias: '/'
    },
    {
        path: '/domains/upload', component: SpreadsheetUpload,
        props: {
            max_lists: 200,
            max_urls: 5000,
        },
        meta: {title: 'Internet.nl Dashboard / Domains / Upload'}
    },
    {path: '/scans', component: ScanMonitor, meta: {title: 'Internet.nl Dashboard / Scan Monitor'}},
    {
        path: '/report/:report/:compare_with',
        component: Report,
        name: 'compared_numbered_report',
        meta: {title: 'Internet.nl Dashboard / Reports'}
    },
    {
        path: '/report/:report',
        component: Report,
        name: 'numbered_report',
        meta: {title: 'Internet.nl Dashboard / Reports'}
    },
    {path: '/report', component: Report, meta: {title: 'Internet.nl Dashboard / Reports'}},
    {path: '/switch-account', component: SwitchAccount, meta: {title: 'Internet.nl Dashboard / Switch Account'}},
    {path: '/add-user', component: InstantAddAccount, meta: {title: 'Internet.nl Dashboard / Add User'}},
    {path: '/tour', component: Demo, meta: {title: 'Internet.nl Dashboard / Tour'}},
    {path: '/demo', component: Demo, meta: {title: 'Internet.nl Dashboard / Tour'}},
    {path: '/unsubscribe', component: Unsubscribe, meta: {title: 'Internet.nl Dashboard / Unsubscribe'}},
    {path: '/profile', component: Account, meta: {title: 'Internet.nl Dashboard / Account'}},
    {path: '/account', component: Account, meta: {title: 'Internet.nl Dashboard / Account'}},
    {path: '/beta', component: Beta, meta: {title: 'Internet.nl Dashboard / Beta'}},
];

const router = new VueRouter({
    routes, // short for `routes: routes`
    props: true,
    // https://reactgo.com/scroll-to-anchor-tags-vue-router/
    // does not work, as nested anchors is not a thing (and not reliable). So do this in component.
    scrollBehavior: function (to) {
        if (to.hash) {
            return {selector: to.hash}
        }
    },
});

// https://www.digitalocean.com/community/tutorials/vuejs-vue-router-modify-head
router.beforeEach((to, from, next) => {
    const nearestWithTitle = to.matched.slice().reverse().find(r => r.meta && r.meta.title);
    if (nearestWithTitle) {
        document.title = nearestWithTitle.meta.title;
    }

    // https://router.vuejs.org/guide/advanced/navigation-guards.html#global-before-guards
    if (to.name !== 'login' && !store.state.user.is_authenticated) next({name: 'login'})
    else next()
});


// these methods are used over and over.
Vue.mixin(
    {
        data: function () {
            return {
                metric_visibility: {
                    // contains all fields in the application and some default values
                    web: {visible: true, show_dynamic_average: true},
                    web_legacy: {visible: false, show_dynamic_average: true},
                    internet_nl_web_tls: {visible: true, show_dynamic_average: true},
                    internet_nl_web_dnssec: {visible: true, show_dynamic_average: true},
                    internet_nl_web_ipv6: {visible: true, show_dynamic_average: true},
                    internet_nl_web_appsecpriv: {visible: true, show_dynamic_average: true},
                    mail: {visible: true, show_dynamic_average: true},
                    mail_legacy: {visible: false, show_dynamic_average: true},
                    internet_nl_mail_dashboard_tls: {visible: true, show_dynamic_average: true},
                    internet_nl_mail_dashboard_auth: {visible: true, show_dynamic_average: true},
                    internet_nl_mail_dashboard_dnssec: {visible: true, show_dynamic_average: true},
                    internet_nl_mail_dashboard_ipv6: {visible: true, show_dynamic_average: true},
                    category_web_ipv6_name_server: {show_dynamic_average: true},
                    category_web_ipv6_web_server: {show_dynamic_average: true},
                    category_web_dnssec_dnssec: {show_dynamic_average: true},
                    category_web_tls_http: {show_dynamic_average: true},
                    category_web_tls_tls: {show_dynamic_average: true},
                    category_web_tls_certificate: {show_dynamic_average: true},
                    category_web_tls_dane: {show_dynamic_average: true},
                    category_web_security_options_appsecpriv: {show_dynamic_average: true},
                    category_web_forum_standardisation_magazine: {show_dynamic_average: true},
                    category_web_forum_standardisation_ipv6_monitor: {show_dynamic_average: true},
                    category_web_forum_standardisation_status_fields: {show_dynamic_average: true},
                    category_mail_ipv6_name_servers: {show_dynamic_average: true},
                    category_mail_ipv6_mail_servers: {show_dynamic_average: true},
                    category_mail_dnssec_email_address_domain: {show_dynamic_average: true},
                    category_mail_dnssec_mail_server_domain: {show_dynamic_average: true},
                    category_mail_dashboard_auth_dmarc: {show_dynamic_average: true},
                    category_mail_dashboard_aut_dkim: {show_dynamic_average: true},
                    category_mail_dashboard_aut_spf: {show_dynamic_average: true},
                    category_mail_starttls_tls: {show_dynamic_average: true},
                    category_mail_starttls_certificate: {show_dynamic_average: true},
                    category_mail_starttls_dane: {show_dynamic_average: true},
                    category_mail_forum_standardisation_magazine: {show_dynamic_average: true},
                    category_mail_forum_standardisation_ipv6_monitor: {show_dynamic_average: true},
                    internet_nl_web_https_cert_domain: {visible: true},
                    internet_nl_web_https_http_redirect: {visible: true},
                    internet_nl_web_https_cert_chain: {visible: true},
                    internet_nl_web_https_tls_version: {visible: true},
                    internet_nl_web_https_tls_clientreneg: {visible: true},
                    internet_nl_web_https_tls_ciphers: {visible: true},
                    internet_nl_web_https_http_available: {visible: true},
                    internet_nl_web_https_dane_exist: {visible: true},
                    internet_nl_web_https_http_compress: {visible: true},
                    internet_nl_web_https_http_hsts: {visible: true},
                    internet_nl_web_https_tls_secreneg: {visible: true},
                    internet_nl_web_https_dane_valid: {visible: true},
                    internet_nl_web_https_cert_pubkey: {visible: true},
                    internet_nl_web_https_cert_sig: {visible: true},
                    internet_nl_web_https_tls_compress: {visible: true},
                    internet_nl_web_https_tls_keyexchange: {visible: true},
                    internet_nl_web_https_tls_keyexchangehash: {visible: true},
                    internet_nl_web_https_tls_ocsp: {visible: true},
                    internet_nl_web_https_tls_0rtt: {visible: true},
                    internet_nl_web_https_tls_cipherorder: {visible: true},
                    internet_nl_web_dnssec_valid: {visible: true},
                    internet_nl_web_dnssec_exist: {visible: true},
                    internet_nl_web_ipv6_ws_similar: {visible: true},
                    internet_nl_web_ipv6_ws_address: {visible: true},
                    internet_nl_web_ipv6_ns_reach: {visible: true},
                    internet_nl_web_ipv6_ws_reach: {visible: true},
                    internet_nl_web_ipv6_ns_address: {visible: true},
                    internet_nl_mail_starttls_cert_domain: {visible: true},
                    internet_nl_mail_starttls_tls_version: {visible: true},
                    internet_nl_mail_starttls_cert_chain: {visible: true},
                    internet_nl_mail_starttls_tls_available: {visible: true},
                    internet_nl_mail_starttls_tls_clientreneg: {visible: true},
                    internet_nl_mail_starttls_tls_ciphers: {visible: true},
                    internet_nl_mail_starttls_dane_valid: {visible: true},
                    internet_nl_mail_starttls_dane_exist: {visible: true},
                    internet_nl_mail_starttls_tls_secreneg: {visible: true},
                    internet_nl_mail_starttls_dane_rollover: {visible: true},
                    internet_nl_mail_starttls_cert_pubkey: {visible: true},
                    internet_nl_mail_starttls_cert_sig: {visible: true},
                    internet_nl_mail_starttls_tls_compress: {visible: true},
                    internet_nl_mail_starttls_tls_keyexchange: {visible: true},
                    internet_nl_mail_auth_dmarc_policy: {visible: true},
                    internet_nl_mail_auth_dmarc_exist: {visible: true},
                    internet_nl_mail_auth_spf_policy: {visible: true},
                    internet_nl_mail_auth_dkim_exist: {visible: true},
                    internet_nl_mail_auth_spf_exist: {visible: true},
                    internet_nl_mail_dnssec_mailto_exist: {visible: true},
                    internet_nl_mail_dnssec_mailto_valid: {visible: true},
                    internet_nl_mail_dnssec_mx_valid: {visible: true},
                    internet_nl_mail_dnssec_mx_exist: {visible: true},
                    internet_nl_mail_ipv6_mx_address: {visible: true},
                    internet_nl_mail_ipv6_mx_reach: {visible: true},
                    internet_nl_mail_ipv6_ns_reach: {visible: true},
                    internet_nl_mail_ipv6_ns_address: {visible: true},
                    internet_nl_mail_legacy_dmarc: {visible: false},
                    internet_nl_mail_legacy_dkim: {visible: false},
                    internet_nl_mail_legacy_spf: {visible: false},
                    internet_nl_mail_legacy_dmarc_policy: {visible: false},
                    internet_nl_mail_legacy_spf_policy: {visible: false},
                    internet_nl_mail_legacy_start_tls: {visible: false},
                    internet_nl_mail_legacy_start_tls_ncsc: {visible: false},
                    internet_nl_mail_legacy_dnssec_email_domain: {visible: false},
                    internet_nl_mail_legacy_dnssec_mx: {visible: false},
                    internet_nl_mail_legacy_dane: {visible: false},
                    internet_nl_mail_legacy_ipv6_nameserver: {visible: false},
                    internet_nl_mail_legacy_ipv6_mailserver: {visible: false},
                    internet_nl_web_legacy_dnssec: {visible: false},
                    internet_nl_web_legacy_tls_available: {visible: false},
                    internet_nl_web_legacy_tls_ncsc_web: {visible: false},
                    internet_nl_web_legacy_https_enforced: {visible: false},
                    internet_nl_web_legacy_hsts: {visible: false},
                    internet_nl_web_legacy_ipv6_nameserver: {visible: false},
                    internet_nl_web_legacy_ipv6_webserver: {visible: false},
                    internet_nl_web_legacy_dane: {visible: false},
                    internet_nl_mail_auth_dmarc_policy_only: {visible: false},
                    internet_nl_mail_auth_dmarc_ext_destination: {visible: false},
                    internet_nl_mail_non_sending_domain: {visible: false},
                    internet_nl_mail_server_configured: {visible: false},
                    internet_nl_mail_servers_testable: {visible: false},
                    internet_nl_mail_starttls_dane_ta: {visible: false},
                    internet_nl_web_appsecpriv_csp: {visible: true},
                    internet_nl_web_appsecpriv_referrer_policy: {visible: true},
                    internet_nl_web_appsecpriv_x_content_type_options: {visible: true},
                    internet_nl_web_appsecpriv_x_frame_options: {visible: true},
                    internet_nl_mail_starttls_tls_cipherorder: {visible: false},
                    internet_nl_mail_starttls_tls_keyexchangehash: {visible: false},
                    internet_nl_mail_starttls_tls_0rtt: {visible: false},
                    internet_nl_web_legacy_tls_1_3: {visible: false},
                    internet_nl_mail_legacy_mail_non_sending_domain: {visible: false},
                    internet_nl_mail_legacy_mail_sending_domain: {visible: false},
                    internet_nl_mail_legacy_mail_server_testable: {visible: false},
                    internet_nl_mail_legacy_mail_server_reachable: {visible: false},
                    internet_nl_mail_legacy_domain_has_mx: {visible: false},
                    internet_nl_mail_legacy_tls_1_3: {visible: false},
                    internet_nl_mail_legacy_category_ipv6: {visible: false},
                    internet_nl_web_legacy_category_ipv6: {visible: false},
                }
            }
        },
        // add some properties to each and every object.
        beforeMount: function () {
            // translate everything.
            this.$i18n.locale = this.locale;
        },
        methods: {
            isEmptyObject: function (my_object) {
                // This replaces the jQuery.isEmptyObject(), which is not a good reason to include the entirity of jquery
                // Documentation: https://www.samanthaming.com/tidbits/94-how-to-check-if-object-is-empty/
                return Object.keys(my_object).length === 0 && my_object.constructor === Object
            },
            // this can probably be replaced with axios or whatever. Or not if we want tos ave on dependencies.
            asynchronous_json_post: function (url, data, callback) {
                // the context parameter is somewhat dangerous, but this allows us to say 'self.' in the callback.
                // which could be done somewhat better.
                // https://stackoverflow.com/questions/20279484/how-to-access-the-correct-this-inside-a-callback
                let server_response = {};
                // console.log(`Posting to ${url}, with data ${data}`)
                (async () => {
                    const rawResponse = await fetch(url, {
                        method: 'POST',
                        credentials: 'include',
                        headers: {
                            'Accept': 'application/json',
                            'Content-Type': 'application/json',
                            'X-CSRFToken': this.get_cookie('csrftoken'),
                        },
                        body: JSON.stringify(data)
                    });
                    try {
                        // here is your synchronous part.
                        server_response = await rawResponse.json();
                    } catch (e) {
                        // SyntaxError: JSON.parse: unexpected character at line 1 column 1 of the JSON data
                        server_response = {'error': true, 'message': 'Server error'}
                    }
                    callback(server_response)
                })();
            },
            get_cookie: function (name) {
                let value = "; " + document.cookie;
                let parts = value.split("; " + name + "=");
                if (parts.length === 2) return parts.pop().split(";").shift();
            },
            // https://stackoverflow.com/questions/14573223/set-cookie-and-get-cookie-with-javascript
            set_cookie: function (name, value, days) {
                let expires = "";
                if (days) {
                    let date = new Date();
                    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
                    expires = "; expires=" + date.toUTCString();
                }
                document.cookie = name + "=" + (value || "") + expires + "; path=/";
            },
            // humanize mixin:
            humanize_date: function (date) {
                // Uses localized date and time format with day name, which is pretty advanced and complete
                return this.$moment(date).format('LLLL');
            },
            humanize_date_date_only: function (date) {
                // Uses localized date and time format with day name, which is pretty advanced and complete
                return this.$moment(date).format('LL');
            },
            humanize_relative_date: function (date) {
                // says things like 'days ago'...
                return this.$moment(date).fromNow();
            },
            humanize_duration: function (duration_in_milliseconds) {
                return this.$moment.duration(duration_in_milliseconds).humanize()
            },
            humanize_filesize: function (size_in_bytes, decimals = 0) {
                if (size_in_bytes === 0) return '0 Bytes';
                let k = 1024,
                    dm = decimals <= 0 ? 0 : decimals || 2,
                    sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'],
                    i = Math.floor(Math.log(size_in_bytes) / Math.log(k));
                return parseFloat((size_in_bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
            },
            load_visible_metrics: function () {
                fetch(`${this.$store.state.dashboard_endpoint}/data/account/report_settings/get/`, {credentials: 'include'}).then(response => response.json()).then(data => {
                    if (!this.isEmptyObject(data.data)) {
                        // Get all possible issue fields before overwriting them with whatever is stored.
                        const all_possible_fields = Object.keys(this.metric_visibility);

                        // now overwrite with the custom settings
                        let issue_filters = data.data;

                        // upgrade the saved issue filters with all fields we know. In case of missing fields, those will
                        // be added with a default value (invisible).
                        all_possible_fields.forEach((field_name) => {
                            this.upgrade_issue_filter_with_new_field(issue_filters, field_name);
                        })
                        this.$store.commit("set_visible_metrics", issue_filters);
                    }
                });
            },
            upgrade_issue_filter_with_new_field: function (issue_filters, field_name) {
                if (!Object.keys(issue_filters).includes(field_name)) {

                    // web and mail and default categories are always visible by default.: otherwise we'd never see any categories when this data is malformed.
                    // in totally empty data, all fields are invisible, which is ok.
                    if (["web",
                        "mail",
                        "internet_nl_web_ipv6",
                        "internet_nl_web_dnssec",
                        "internet_nl_web_tls",
                        "internet_nl_web_appsecpriv",
                        "internet_nl_mail_dashboard_ipv6",
                        "internet_nl_mail_dashboard_dnssec",
                        "internet_nl_mail_dashboard_auth",
                        "internet_nl_mail_dashboard_tls",
                        "internet_nl_web_https_cert_domain",
                        "internet_nl_web_https_http_redirect",
                        "internet_nl_web_https_cert_chain",
                        "internet_nl_web_https_tls_version",
                        "internet_nl_web_https_tls_clientreneg",
                        "internet_nl_web_https_tls_ciphers",
                        "internet_nl_web_https_http_available",
                        "internet_nl_web_https_dane_exist",
                        "internet_nl_web_https_http_compress",
                        "internet_nl_web_https_http_hsts",
                        "internet_nl_web_https_tls_secreneg",
                        "internet_nl_web_https_dane_valid",
                        "internet_nl_web_https_cert_pubkey",
                        "internet_nl_web_https_cert_sig",
                        "internet_nl_web_https_tls_compress",
                        "internet_nl_web_https_tls_keyexchange",
                        "internet_nl_web_https_tls_keyexchangehash",
                        "internet_nl_web_https_tls_ocsp",
                        "internet_nl_web_https_tls_0rtt",
                        "internet_nl_web_https_tls_cipherorder",
                        "internet_nl_web_dnssec_valid",
                        "internet_nl_web_dnssec_exist",
                        "internet_nl_web_ipv6_ws_similar",
                        "internet_nl_web_ipv6_ws_address",
                        "internet_nl_web_ipv6_ns_reach",
                        "internet_nl_web_ipv6_ws_reach",
                        "internet_nl_web_ipv6_ns_address",
                        "internet_nl_mail_starttls_cert_domain",
                        "internet_nl_mail_starttls_tls_version",
                        "internet_nl_mail_starttls_cert_chain",
                        "internet_nl_mail_starttls_tls_available",
                        "internet_nl_mail_starttls_tls_clientreneg",
                        "internet_nl_mail_starttls_tls_ciphers",
                        "internet_nl_mail_starttls_dane_valid",
                        "internet_nl_mail_starttls_dane_exist",
                        "internet_nl_mail_starttls_tls_secreneg",
                        "internet_nl_mail_starttls_dane_rollover",
                        "internet_nl_mail_starttls_cert_pubkey",
                        "internet_nl_mail_starttls_cert_sig",
                        "internet_nl_mail_starttls_tls_compress",
                        "internet_nl_mail_starttls_tls_keyexchange",
                        "internet_nl_mail_auth_dmarc_policy",
                        "internet_nl_mail_auth_dmarc_exist",
                        "internet_nl_mail_auth_spf_policy",
                        "internet_nl_mail_auth_dkim_exist",
                        "internet_nl_mail_auth_spf_exist",
                        "internet_nl_mail_dnssec_mailto_exist",
                        "internet_nl_mail_dnssec_mailto_valid",
                        "internet_nl_mail_dnssec_mx_valid",
                        "internet_nl_mail_dnssec_mx_exist",
                        "internet_nl_mail_ipv6_mx_address",
                        "internet_nl_mail_ipv6_mx_reach",
                        "internet_nl_mail_ipv6_ns_reach",
                        "internet_nl_mail_ipv6_ns_address",
                        "internet_nl_web_appsecpriv_csp",
                        "internet_nl_web_appsecpriv_referrer_policy",
                        "internet_nl_web_appsecpriv_x_content_type_options",
                        "internet_nl_web_appsecpriv_x_frame_options",
                    ].includes(field_name)) {
                        issue_filters[field_name] = {
                            visible: true,
                            show_dynamic_average: true,
                            only_show_dynamic_average: false
                        }
                    } else {
                        // this is invisible because we don't want to tamper with existing settings when introducing new
                        // fields. Users will have to enable it themselves.
                        issue_filters[field_name] = {
                            visible: false,
                            show_dynamic_average: true,
                            only_show_dynamic_average: false
                        }
                    }
                }
            },
        },
        // make sure all components are also translated when the locale is switched.
        // see: https://github.com/kazupon/vue-i18n/issues/411,
        computed: {
            locale() {
                if (typeof this.$store !== 'undefined') {
                    return this.$store.state.locale;
                } else if (typeof store !== 'undefined') {
                    // on the root component 'this' is not available. But we can access store and everything directly.
                    // console.info(`Using store locale, set to ${store.state.locale}.`);
                    return store.state.locale;
                } else {
                    // fallback language
                    console.info('Using fallback locale.')
                    return 'en';
                }
            },
        },
        watch: {
            locale() {
                if (typeof this.$i18n !== 'undefined') {
                    this.$i18n.locale = this.locale;
                }
            },
        },
    }
);


new Vue({
    i18n,
    router,
    store,
    render: h => h(App),
}).$mount('#app')

