<template type="x-template" id="switch-account-template">
    <div id="switch-account" class="block fullwidth">
        <h2>{{ $t("title") }}</h2>
        <p>{{ $t("intro") }}</p>

        <server-response :response="server_response"></server-response>

        <label for="account_selection">{{ $t("select") }}:</label>
        <select id="account_selection" v-model="selected_account" @change="set_account" :size="accounts.length">
            <option v-for="(account, index) in accounts" :key="index"
                    :value="account['id']" :selected="account['id'] === current_account">
                {{ account['id'] }}: {{ account['name'] }} (lists: {{ account['lists'] }}, scans: {{
                    account['scans']
                }}, users: {{ account['users'].length }})
            </option>
        </select>

    </div>
</template>

<script>
import http_mixin from './http_mixin.vue'

export default {

    i18n: {
        messages: {
            en: {
                title: "Switch Account",
                intro: "This feature allows you to switch to another account, and use this site as them." +
                    "Important: refresh the page after choosing an account!",
                select: "Select account to use"
            }
        }
    },
    template: '#switch-account-template',
    mixins: [http_mixin],

    data: function () {
        return {
            accounts: [],
            current_account: 0, // still doesn't work...
            selected_account: 0,
            server_response: {},
        }
    },
    mounted: function () {
        this.get_accounts();
    },
    methods: {
        get_accounts: function () {
            fetch(`${this.$store.state.dashboard_endpoint}/data/powertools/get_accounts/`, {credentials: 'include'}).then(response => response.json()).then(data => {
                this.accounts = data['accounts'];
                this.current_account = data['current_account'][0];
            }).catch((fail) => {
                console.log('A loading error occurred: ' + fail);
            });
        },

        set_account: function () {
            let data = {'id': this.selected_account};

            this.asynchronous_json_post(
                `${this.$store.state.dashboard_endpoint}/data/powertools/set_account/`, data, (server_response) => {
                    if (server_response) {
                        this.server_response = server_response;
                        this.get_accounts();
                        // destroy all components, as the other user is now active (or should be)
                    }
                }
            );

        }
    }
}
</script>