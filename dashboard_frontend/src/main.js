import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuex from 'vuex'
import VueI18n from 'vue-i18n'
import vSelect from 'vue-select'
import {Tabs, Tab} from 'vue-tabs-component';
import createPersistedState from "vuex-persistedstate";
import autorefresh from './components/autorefresh.vue'
import loading from './components/loading.vue'
import modal from './components/modal.vue'
import server_response from './components/server-response.vue'
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
import App from './App.vue'
// https://stackoverflow.com/questions/50925793/proper-way-of-adding-css-file-in-vue-js-application
import './assets/css/styles.scss';

Vue.component('v-select', vSelect);
Vue.component('tabs', Tabs);
Vue.component('tab', Tab);
Vue.use(VueI18n)
Vue.use(VueRouter)
Vue.use(require('vue-moment'));
Vue.use(Vuex);

Vue.component('autorefresh', autorefresh)
Vue.component('loading', loading)
Vue.component('modal', modal)
Vue.component('server-response', server_response)

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
        }
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
        // add some properties to each and every object.
        beforeMount: function () {
            // translate everything.
            this.$i18n.locale = this.locale;
        },
        methods: {
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
            }
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

