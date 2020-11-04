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

                            @click="toggleHamburgerMenuExpand"
                            class="menu-button">
                        <i>≡</i><b>&nbsp;menu</b>
                    </button>

                    <div id="language-switch-header-container" aria-hidden="true">
                        <ul class="language-switch-list">
                            <li v-for="(language_code, index) in supported_languages" :key="index">
                                <button v-if="language_code === locale" class="active-language" disabled>
                                    {{ $t(language_code) }}
                                </button>
                                <a v-if="language_code !== locale"
                                   @click="set_locale(language_code)">{{ $t(language_code) }}</a>
                            </li>
                        </ul>
                    </div>

                    <nav id="sitenav" aria-hidden="true" aria-labelledby="menu-button">
                        <SiteMenu :is_authenticated="user.is_authenticated"
                                  :is_superuser="user.is_superuser"></SiteMenu>
                    </nav>
                </template>
                <template v-else>

                    <div id="language-switch-header-container">
                        <ul class="language-switch-list">
                            <li v-for="(language_code, index) in supported_languages" :key="index">
                                <button v-if="language_code === locale" class="active-language" disabled>
                                    {{ $t(language_code) }}
                                </button>
                                <a v-if="language_code !== locale"
                                   @click="set_locale(language_code)">{{ $t(language_code) }}</a>
                            </li>
                        </ul>
                    </div>

                    <nav id="sitenav">
                        <SiteMenu :is_authenticated="user.is_authenticated"
                                  :is_superuser="user.is_superuser"></SiteMenu>
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
                            {{ $t('report_issues.thank_you') }}
                            {{ $t('report_issues.report_issues') }}
                            <a href="https://github.com/internetstandards/Internet.nl-dashboard/issues" target="_blank">{{
                                    $t('report_issues.link_text')
                                }}</a>.
                        </p>
                    </div>
                </section>
            </div>

        </main>

        <footer id="footer">
            <img id="flag" src="static/images/vendor/internet_nl/clear.gif" alt="">
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
import Headroom from "headroom.js";
// todo make sure the menu works
import SiteMenu from './components/site-menu.vue'
import {mapState} from 'vuex'

export default {
    i18n: {
        locale: 'en',
        fallbackLocale: 'en',
        silentFallbackWarn: true,
    },
    mounted: function () {
        this.login_status();
        // set default locale
        this.$moment.locale(this.locale);

        this.$nextTick(function () {


            // give some headroom, just like in the original...
            let theHeader = document.querySelector("header");
            let fixedHeaderbody = document.querySelector("body");
            fixedHeaderbody.classList.add("body-with-semifixed-header");
            let fixedHeader = new Headroom(theHeader, {
                "offset": 205,
                "tolerance": 5,
                "classes": {"initial": "header-js-animated", "pinned": "header-pinned", "unpinned": "header-unpinned"}
            });
            fixedHeader.init();

            // and make sure the hamburger menu shows when the window gets too small...
            if (matchMedia) {
                var mq = window.matchMedia('(min-width: 740px)');
                mq.addEventListener('change', this.WidthChange);
                this.WidthChange(mq);
            }
        })

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
        }
    },
    methods: {
        set_locale: function (locale) {
            console.log(`Switching app to language: ${locale}.`);
            if (!this.supported_languages.includes(locale)) {
                console.log(`Language ${locale} not supported`)
                return
            }

            // todo: moment does not yet switch locale live.
            // there is no way to set it to locale, it always says 'en', even though NL is being required.
            this.$store.commit("set_locale", locale);
            this.$moment.locale(locale);

            // Using this cookie Django knows what language translations need to be (if still applicable)
            // this should not matter in the future though.
            document.cookie = "dashboard_language=" + (locale || "en") + "; path=/; SameSite=Lax;";
        },
        WidthChange: function (mq) {
            this.show_hamburgermenu = !mq.matches;
            // reset the menu state after resizing while the menu is open. So the next click it can be opened again.
            if (!this.show_hamburgermenu) {
                this.hamburgermenu_expanded = false;
            }
        },
        login_status: function () {
            this.server_response = {};
            this.loading = true;
            fetch(`${this.$store.state.dashboard_endpoint}/session/status/`, {
                    method: 'GET',
                    credentials: 'include',
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.get_cookie('csrftoken')
                    }
                }
            ).then(response => response.json()).then(data => {
                this.$store.commit("set_user", data);
                this.loading = false;
            }).catch((fail) => {
                this.error_occurred = true;
                console.log('A loading error occurred: ' + fail);
            });
        },
        toggleHamburgerMenuExpand: function () {
            this.hamburgermenu_expanded = !this.hamburgermenu_expanded;

            // this code was taken from menu-min.js
            var header = document.querySelector('header .wrap'),
                menu = document.querySelector('#sitenav'),
                langswitch = document.querySelector('#language-switch-header-container'),
                menuButton = document.querySelector('.menu-button');

            if (this.hamburgermenu_expanded) {
                header.classList.add('active');
                menu.classList.add('active');
                menu.setAttribute('aria-hidden', 'false');
                langswitch.classList.add('active');
                langswitch.setAttribute('aria-hidden', 'false');
                menuButton.setAttribute('aria-expanded', 'true');
            } else {
                header.classList.remove('active');
                menu.classList.remove('active');
                menu.setAttribute('aria-hidden', 'true');
                langswitch.classList.remove('active');
                langswitch.setAttribute('aria-hidden', 'true');
                menuButton.setAttribute('aria-expanded', 'false');
            }
        }
    },
    components: {
        SiteMenu
    },
    computed: mapState(['user']),
}
</script>

<style>
@media (max-width: 499px) {
    #site-title a {
        background-image: url("/static/images/vendor/internet_nl/logo_en.svg") !important;
    }
}

@media (min-width: 500px) and (max-width: 739px) {
    #site-title a {
        background-image: url("/static/images/vendor/internet_nl/logo-tablet_en.svg") !important;
    }
}

@media (min-width: 740px) {
    #site-title a {
        background-image: url("/static/images/vendor/internet_nl/logo_en.svg") !important;
    }
}

@media print {
    #site-title a {
        background-image: url("/static/images/vendor/internet_nl/logo_en.png") !important;
        /* The SVG logo doesn't print correct
        background-image: url("/static/images/vendor/internet_nl/logo_en.svg") !important; */
    }
}

.twitterfollow {
    background: transparent url("/static/images/vendor/internet_nl/icon-twitterfollow.svg") no-repeat 5px center !important;
    background-size: 1.25em 1.25em !important;
    padding-left: 2em !important;
}
</style>
<i18n>
{
	"en": {
		"base": {
			"copyright": "Copyright",
			"disclosure": "Responsible disclosure",
			"followtwitter": "Folllow us on Twitter",
			"info": "Internet.nl is an initiative of the Internet community and the Dutch government.",
			"privacy": "Privacy statement"
		},
		"en": "English",
		"nl": "Nederlands",
		"page": {
			"sitedescription": "Test for modern Internet Standards like IPv6, DNSSEC, HTTPS, DMARC, STARTTLS and DANE.",
			"sitetitle": "Internet.nl"
		},
		"report_issues": {
			"link_text": "this GitHub page",
			"report_issues": "Please report issues on ",
			"thank_you": "Thank you for using the internet.nl dashboard."
		}
	},
	"nl": {
		"base": {
			"copyright": "Copyright",
			"disclosure": "Responsible disclosure",
			"followtwitter": "Volg ons op Twitter",
			"info": "Internet.nl is een initiatief van de internetgemeenschap en de Nederlandse overheid.",
			"privacy": "Privacyverklaring"
		},
		"en": "English",
		"nl": "Nederlands",
		"page": {
			"sitedescription": "Test voor moderne Internetstandaarden zoals IPv6, DNSSEC, HTTPS, DMARC, STARTTLS en DANE.",
			"sitetitle": "Internet.nl"
		},
		"report_issues": {
			"link_text": "onze GitHub pagina.",
			"report_issues": "Meld fouten of suggesties op",
			"thank_you": "Bedankt voor het gebruiken van het internet.nl Dashboard."
		}
	}
}
</i18n>
