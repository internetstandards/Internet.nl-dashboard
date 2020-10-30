<template id="account_template">
    <div class="account">

        <div class="block fullwidth">
            <h1>{{ $t("title") }}</h1>
            <p>{{ $t("intro") }}</p>
            <loading :loading="loading"></loading>
            <server-response :response="server_response" :message="$t(server_response.message)"></server-response>

            <div v-if="!user.is_authenticated">
                <form v-on:submit.prevent="login">
                <label class='first_name' for="first_name">{{ $t("username") }}</label>
                <input id="username" type="text" maxlength="120" v-model="username">
                <br>

                <label class='last_name' for="last_name">{{ $t("password") }}</label>
                <input id="password" type="password" maxlength="120" v-model="password">
                <br>
                <button id="login" type="submit" @click="login">{{ $t("login") }}</button>
                </form>
            </div>
            <div v-else>
                {{ $t('logged_in') }}
            </div>
        </div>

    </div>
</template>

<script>

import {mapState} from 'vuex'

export default {
    i18n: {
        messages: {
            en: {
                title: 'Login',
                intro: "Log into the dashboard.",
                username: "Username",
                password: "Password",
                login: "Log in",

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
                if (this.$store.state.user.is_authenticated) {
                    // don't keep the 'succesful login' message:
                    this.server_response = {};
                    
                    // This is not a solution to double navigation, but i think the error is weird and incorrect.
                    // https://stackoverflow.com/questions/62462276/how-to-solve-avoided-redundant-navigation-to-current-location-error-in-vue
                    if (this.$router.name !== 'domains') {
                        this.$router.push({'name': 'domains'}).catch(()=>{});
                    }
                }
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
                        // redirect to desired page? Or is that not possible anymore?
                        this.server_response = server_response;
                        this.loading = false;
                    }
                }
            );
        },
    },
    computed: mapState(['user']),
    name: 'account',
    template: '#account_template',
}
</script>
