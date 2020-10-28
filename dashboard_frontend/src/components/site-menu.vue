{% verbatim %}
<template type="text/x-template" id="menu_template">
    <ul>
        <template v-if="is_authenticated">
            <template v-if="is_superuser">
                <li><router-link to="/add-user">👤</router-link></li>
                <li><router-link to="/switch-account">🔀</router-link></li>
            </template>

            <li><router-link to="/domains" accesskey="d">{{ $t("domains") }}</router-link></li>
            <li><router-link to="/scans" accesskey="s">{{ $t("scans") }}</router-link></li>
            <li><router-link to="/report" accesskey="r">{{ $t("reports") }}</router-link></li>
            <li><router-link to="/account" accesskey="a">{{ $t("account") }}</router-link></li>

            <li class=""><a href="/logout/" accesskey="l">{{ $t("log_off") }}</a></li>
        </template>
        <template v-if="!is_authenticated">
            <li class="current"><a href="/account/login/" accesskey="l">{ $t("log_in") }}</a></li>
        </template>
    </ul>
</template>
{% endverbatim %}
<script>
export default {
    i18n: {
        messages: {
            en: {
                admin: 'Admin',
                domains: "Domains",
                scans: "Scans",
                reports: "Reports",
                account: "Account",
                log_off: "Log off",
                log_in: "Log in",
            },
            nl: {
                admin: 'Beheer',
                domains: "Domeinen",
                scans: "Scans",
                reports: "Rapporten",
                account: "Account",
                log_off: "Uitloggen",
                log_in: "Inloggen",
            }
        }
    },
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
    template: '#menu_template',
}
</script>
