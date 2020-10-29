<template type="x-template" id="switch-account-template">
    <div id="switch-account" class="block fullwidth">
        <h2>{{ $t("title") }}</h2>
        <p v-html="$t('intro')"></p>

        <server-response :response="server_response"></server-response>

        <label for="account_selection">{{ $t("select") }}:</label>

        <v-select
            id="account_selection"
            v-model="current_account"
            placeholder="Select account..."
            :options="accounts"
            code="id"
            label="label"
            :multiple="false"
            :size="accounts.length"
            @input="set_account"
        >
            <slot name="no-options">No options...</slot>
        </v-select>

    </div>
</template>

<script>

export default {

    i18n: {
        messages: {
            en: {
                title: "Switch Account",
                intro: "This feature allows you to switch to another account, and use this site as them. " +
                    "<br><b>Important: refresh the page after choosing an account!</b>",
                select: "Select account to use"
            }
        }
    },
    template: 'switch-account-template',

    data: function () {
        return {
            accounts: [],
            current_account: 0,
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
                this.current_account = data['current_account'];

                // create options for nice accounts.

            }).catch((fail) => {
                console.log('A loading error occurred: ' + fail);
            });
        },

        set_account: function () {
            let data = {'id': this.current_account.id};

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