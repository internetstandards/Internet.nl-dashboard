<style scoped>
.router-link-active {
    font-weight: bold;
    border-bottom: 3px solid #ffab4c;
}
</style>
<template>
    <ul>
        <template v-if="is_authenticated">
            <template v-if="is_superuser">
                <li>
                    <router-link to="/add-user">👤</router-link>
                </li>
                <li>
                    <router-link to="/switch-account">🔀</router-link>
                </li>
            </template>

            <li>
                <router-link to="/domains" accesskey="d">{{ $t("domains") }}</router-link>
            </li>
            <li>
                <router-link to="/scans" accesskey="s">{{ $t("scans") }}</router-link>
            </li>
            <li>
                <router-link to="/report" accesskey="r">{{ $t("reports") }}</router-link>
            </li>
            <li>
                <router-link to="/account" accesskey="a">{{ $t("account") }}</router-link>
            </li>

            <li class=""><a @click="logout" accesskey="l">{{ $t("log_off") }}</a></li>
        </template>
        <template v-if="!is_authenticated">
            <router-link to="/login" accesskey="a">{{ $t("log_in") }}</router-link>
        </template>
    </ul>
</template>
<script>
export default {
    props: {
        is_authenticated: {
            type: Boolean,
            default: false,
        },
        is_superuser: {
            type: Boolean,
            default: false,
        }
    },
    name: 'site-menu',
    methods: {
        logout: function () {
            this.loading = true;
            fetch(`${this.$store.state.dashboard_endpoint}/session/logout/`, {
                    method: 'GET',
                    credentials: 'include',
                }
            ).then(response => response.json()).then(() => {
                this.loading = false;
                this.status();
            }).catch((fail) => {
                this.error_occurred = true;
                console.log('A loading error occurred: ' + fail);
            });
        },
        status: function () {
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
                if (!this.$store.state.user.is_authenticated) {
                    this.$router.push({'name': 'login'});
                }
            }).catch((fail) => {
                this.error_occurred = true;
                console.log('A loading error occurred: ' + fail);
            });
        },
    }
}
</script>
<i18n>
{
	"en": {
		"account": "Account",
		"admin": "Admin",
		"domains": "Domains",
		"log_in": "Log in",
		"log_off": "Log off",
		"reports": "Reports",
		"scans": "Scans"
	},
	"nl": {
		"account": "Account",
		"admin": "Beheer",
		"domains": "Domeinen",
		"log_in": "Inloggen",
		"log_off": "Uitloggen",
		"reports": "Rapporten",
		"scans": "  Scans"
	}
}
</i18n>
