<template>
    <div id="switch-account" class="block fullwidth">

        <h2>{{ $t("title") }}</h2>
        <p>{{ $t("intro") }}</p>

        <p>

        <server-response :response="server_response"></server-response>

        {{ $t("username") }}:<br>
        <input type="text" name="username" v-model="username">

        {{ $t("password") }}:<br>
        <input type="password" name="password" v-model="password">
        <button type="button" class="save btn btn-lg btn-primary" @click="save_instant_account()">{{ $t("save") }}</button>
        </p>

    </div>
</template>
<script>
export default {
    data: function () {
        return {
            username: "",
            password: "",
            server_response: {},
        }
    },
    methods: {
        save_instant_account: function () {
            let data = {'username': this.username, 'password': this.password};

            this.asynchronous_json_post(
                `${this.$store.state.dashboard_endpoint}/data/powertools/save_instant_account/`, data, (server_response) => {
                    if (server_response)
                        this.server_response = server_response;
                }
            );
        },
    }
}
</script>
<i18n>
{
    "en": {
        "title": "Instant User Creation Form",
        "intro": "This creates a standard user, an Account to internet.nl and the bridge between it (DashboardUser).\n There are minimal password checks on this form. This form is intended to quickly migrate API user accounts and\n give them access to the dashboard with the same username and password.",
        "username": "Username",
        "password": "Password",
        "save": "Save!"
    }
}
</i18n>