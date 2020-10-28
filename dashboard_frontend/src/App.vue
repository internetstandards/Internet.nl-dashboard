<template>
    <div id="app">
        <div class="hidethis" aria-hidden="true">
            <span id="matomo-url">//matomo.internet.nl/</span>
            <span id="matomo-siteid">2</span>
            <span id="matomo-subdomain-tracking">*.internet.nl</span>
        </div>
        <div class="skiplink"><a href="#content">
            {% trans "page gotocontents" %}
        </a></div>
        <div class="skiplink" id="skiplink-sitenav"><a href="#sitenav">
            {% trans "page gotomainmenu" %}
        </a></div>
        <div class="skiplink"><a href="#footer">
            {% trans "page gotofooter" %}
        </a></div>

        <header>
            <div class="wrap">
                <div class="hidethis" aria-hidden="true">
                    <span id="panel-button-show">
                        Show details
                    </span>
                    <span id="panel-button-hide">
                        Hide details
                    </span>
                    <span id="panel-item-open">
                        open
                    </span>
                    <span id="panel-item-close">
                        close
                    </span>
                </div>

                <div id="masthead">
                    <p id="site-title"><a href="/"><span class="hidden">{{ $t('page.sitetitle') }}</span></a></p>
                    <p id="site-description"><span class="hidden">{{ $t('page.sitedescription') }}</span></p>
                </div>

                <template v-if="show_hamburgermenu">
                    <!-- This is duplicated because some javascript copies and mangles items around. This has to be done in a better, more vue-oriented way. -->
                    <button id="menu-button"
                            aria-label="Menu"
                            aria-expanded="false"
                            aria-controls="sitenav"
                            @click="toggleHamburgerMenuExpand"
                            class="menu-button">
                        <i>≡</i><b>&nbsp;menu</b>
                    </button>

                    <div id="language-switch-header-container" aria-hidden="true">
                        <ul class="language-switch-list">
                            <li v-for="(language_code, index) in supported_languages" :key="index">
                                <button v-if="language_code === activated_langauge" class="active-language" disabled>
                                    {{ $t(language_code) }}
                                </button>
                                <a v-if="language_code !== activated_langauge"
                                   onclick="set_language(language_code)">{{ $t(language_code) }}</a>
                            </li>
                        </ul>
                    </div>

                    <nav id="sitenav" aria-hidden="true" aria-labelledby="menu-button">
                        <site-menu :is_authenticated="user.is_authenticated"
                                   :is_superuser="user.is_superuser"></site-menu>
                    </nav>
                </template>
                <template v-else>

                    <div id="language-switch-header-container" aria-hidden="true">
                        <ul class="language-switch-list">
                            <li v-for="(language_code, index) in supported_languages" :key="index">
                                <button v-if="language_code === activated_langauge" class="active-language" disabled>
                                    {{ $t(language_code) }}
                                </button>
                                <a v-if="language_code !== activated_langauge"
                                   onclick="set_language(language_code)">{{ $t(language_code) }}</a>
                            </li>
                        </ul>
                    </div>

                    <nav id="sitenav">
                        <site-menu :is_authenticated="user.is_authenticated"
                                   :is_superuser="user.is_superuser"></site-menu>
                    </nav>
                </template>
            </div>
        </header>

        <main id="content" class="clearfix" tabindex="-1">
            <div class="mainwrap">

            </div>
            <div class="wrap">

                <div style="width: 100%;">
                    <!-- to support keep alive, you also need to rewrite the links between components to be updated -->
                    <!-- to support keep alive, your autorefresh functions need to triggered more frequently / smarter -->
                    <keep-alive>
                        <router-view></router-view>
                    </keep-alive>
                </div>

            </div>

            <div class="wrap">
                <section class="block do-not-print">
                    <div class="wrapper">
                        <p style="font-size: 0.9em; font-style: italic; margin-bottom: 0em;">
                            Thank you for using the internet.nl dashboard. Please report issues on <a
                            href="https://github.com/internetstandards/Internet.nl-dashboard/issues" target="_blank">this
                            GitHub page</a>.
                        </p>
                    </div>
                </section>
            </div>

        </main>

        <footer id="footer">
            <img id="flag" src="{% static 'images/vendor/internet_nl/clear.gif' %}" alt="">
            <div class="wrap">
                {{ $t('base.info') }}
                <hr>
                <ul>
                    <li><a class="footlink" href="https://www.internet.nl/disclosure/">
                        {{ $t('base.disclosure') }}
                    </a></li>
                    <li><a class="footlink" href="https://www.internet.nl/privacy/">
                        {{ $t('base.privacy') }}
                    </a></li>
                    <li><a class="footlink" href="https://www.internet.nl/copyright/">
                        {{ $t('base.copyright') }}
                    </a></li>
                    <li class="follow-us"><a class="footlink twitterfollow" href="https://twitter.com/internet_nl">
                        {{ $t('base.followtwitter') }}
                    </a></li>
                </ul>
            </div>
        </footer>
    </div>
</template>

<script>
import Vue from 'vue'
import VueRouter from 'vue-router'
import Vuex from 'vuex'
import VueI18n from 'vue-i18n'

Vue.use(VueI18n)
Vue.use(VueRouter)

// https://stackoverflow.com/questions/10730362/get-cookie-by-name
function get_cookie(name) {
    let value = "; " + document.cookie;
    let parts = value.split("; " + name + "=");
    if (parts.length === 2) return parts.pop().split(";").shift();
}

// import Loading from './components/Loading.vue'
import DomainListManager from './components/DomainListManager.vue'
import SpreadsheetUpload from './components/SpreadsheetUpload.vue'
import ScanMonitor from './components/SpreadsheetUpload.vue'
import Report from './components/Report.vue'
import SwitchAccount from './components/SwitchAccount.vue'
import InstantAddAccount from './components/InstantAddAccount.vue'
import Account from './components/Account.vue'
import Demo from './components/Demo.vue'
import Unsubscribe from './components/Unsubscribe.vue'

const routes = [
    {path: '/', component: DomainListManager,},

    // refreshing the app on a control panel will lead to nothing, make sure it leads to something.
    {path: '/control-panel-:id', component: DomainListManager,},

    {path: '/domains/:list', component: DomainListManager, name: 'numbered_lists'},
    {path: '/domains', component: DomainListManager,},
    {
        path: '/upload', component: SpreadsheetUpload,
        props: {
            csrf_token: get_cookie('csrftoken'),
            max_lists: 200,
            max_urls: 5000,
        }
    },
    {path: '/scans', component: ScanMonitor},
    {path: '/report/:report/:compare_with', component: Report, name: 'compared_numbered_report'},
    {path: '/report/:report', component: Report, name: 'numbered_report'},
    {path: '/report', component: Report},
    {path: '/switch-account', component: SwitchAccount},
    {path: '/add-user', component: InstantAddAccount},
    {path: '/tour', component: Demo},
    {path: '/demo', component: Demo},
    {path: '/unsubscribe', component: Unsubscribe},
    {path: '/profile', component: Account},
    {path: '/account', component: Account},
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

Vue.use(Vuex);
const store = new Vuex.Store({
    state: {
        // -2 is used, to be able to distinct for the first upload and zero uploads.
        uploads_performed: -2,

        // the scan monitor is used to determine if lists of domains or the reports dropdowns need to be
        // updated. If the scan monitor is not loaded, a standard autorefresh strategy is used.
        scan_monitor_data: [],
    },

    mutations: {
        // this.$store.commit('set_uploads_performed', 0)
        set_uploads_performed(state, value) {
            state.uploads_performed = value;
        },
        update_scan_monitor_data(state, value) {
            state.scan_monitor_data = value;
        }
    },
});

export default {
    router,
    store,
    i18n: {
        messages: {
            en: {
                en: "English",
                nl: "Nederlands",
                page: {
                    sitetitle: 'Internet.nl',
                    sitedesscription: 'Test for modern Internet Standards like IPv6, DNSSEC, HTTPS, DMARC, STARTTLS\n' +
                        ' and DANE.',
                },
                base: {
                    info: "Internet.nl is an initiative of the Internet community and the Dutch government.",
                    disclosure: "Responsible disclosure",
                    privacy: "Privacy statement",
                    copyright: "Copyright",
                    followtwitter: "Folllow us on Twitter",
                },
            },
            nl: {}
        }
    },
    name: 'App',
    data: function () {
        return {
            show_hamburgermenu: false,
            hamburgermenu_expanded: false,

            // server-side config:
            supported_languages: ['en', 'nl'],
            maximum_lists_per_spreadsheet: 200,
            maximum_urls_per_spreadsheet: 5000,

            // user settings
            activated_language: 'en',  // todo: how to switch this, also post to server to set django language.
            user: {
                // This is only gui stuff, all open source. There is no security in gui's.
                is_authenticated: false,
                is_superuser: false,
            }
        }
    },
    methods: {
        set_language: function(language_code){

            this.$moment.locale(language_code)

            // old school.
            // todo: make a post to the django system to set the language. Probably a cookie value.
            // document.cookie = "dashboard_language=" + (language_code || "en") + "; path=/";
            //location.reload();
        }
    },
    components: {}
}
</script>

<style>
#app {
    font-family: Avenir, Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-align: center;
    color: #2c3e50;
    margin-top: 60px;
}
</style>
