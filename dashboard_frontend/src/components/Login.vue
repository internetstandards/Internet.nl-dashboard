<template id="account_template">
    <div class="account">

        <div class="block fullwidth">
            <h1>{{ $t("title") }}</h1>
            <p>{{ $t("intro") }}</p>
            <loading :loading="loading"></loading>
            <server-response :response="server_response" :message="$t(server_response.message)"></server-response>

        </div>

        <div class="wrap" v-if="!user.is_authenticated">
            <div class="block">
                <label class='first_name' for="first_name">{{ $t("username") }}</label>
                <input id="username" type="text" maxlength="120" v-model="username"><br><br>
                <br>

                <label class='last_name' for="last_name">{{ $t("password") }}</label>
                <input id="password" type="text" maxlength="120" v-model="password"><br><br>
                <br>
                <button id="login" type="button" @click="login">{{ $t("login") }}</button>
            </div>
        </div>
        <div class="wrap" v-else>
            {{ $t('logged_in') }}
            <button id="logout" type="button" @click="logout">{{ $t("logout") }}</button>
        </div>
    </div>
</template>

<script>

import { mapState } from 'vuex'

export default {
    i18n: {
        messages: {
            en: {
                title: 'Login',
                intro: "Log into the dashboard.",
                username: "Username",
                password: "Password",
                login: "Log in",
                logout: "Log out",

                // messages:
                no_credentials_supplied: "Enter a username and password to log in.",
                invalid_credentials: "Username or password not correct.",
                user_not_active: "User is not active.",
                logged_in: "You have succesfully logged in.",
                logged_out: "You have succesfully logged out.",

                // todo: show two-factor stuff inside an iframe. It's a hack :))
            },
            nl: {
                title: 'Inloggen',
                intro: "Log in op het dashboard.",
                username: "gebruikersnaam",
                password: "wachtwoord",
            }
        }
    },
    data: function () {
        return {
            loading: false,
            username: "",
            password: "",
            server_response: {},
        }
    },
    mounted: function () {
        this.status();
    },
    methods: {
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
            }).catch((fail) => {
                this.error_occurred = true;
                console.log('A loading error occurred: ' + fail);
            });
        },
        login: function () {
            this.loading = true;
            let data = {
                'username': this.username,
                'password': this.password,
            };
            this.asynchronous_json_post(
                `${this.$store.state.dashboard_endpoint}/session/login/`, data, (server_response) => {
                    if (server_response) {
                        this.status();
                        this.server_response = server_response;
                        this.loading = false;
                    }
                }
            );
        },
        logout: function () {
            this.loading = true;
            fetch(`${this.$store.state.dashboard_endpoint}/session/logout/`, {
                    method: 'GET'
                }
            ).then(response => response.json()).then(data => {
                this.loading = false;
                console.log(data);
                this.status();
            }).catch((fail) => {
                this.error_occurred = true;
                console.log('A loading error occurred: ' + fail);
            });
        },
    },
    computed: mapState(['user']),
    name: 'account',
    template: '#account_template',
}
</script>
