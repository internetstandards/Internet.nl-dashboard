<template>
    <div id="switch-account" class="block fullwidth" style="min-height: 600px;">
        <h2>{{ $t("title") }}</h2>
        <p> {{ $t('intro') }}</p>
        <p><b>{{ $t('reload_page_warning') }}</b></p>

        <template v-if="server_response.success">
            <server-response :response="server_response"
                             :message="$t('switched_account', [server_response.data.account_name])"></server-response>
        </template>
        <template v-else>
            <server-response :response="server_response"></server-response>
        </template>

        <p>
            <button role="link" @click="get_accounts">{{ $t("reload_list") }}</button>
            <br><br>
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
        </p>
    </div>
</template>

<script>
export default {
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
            fetch(`${this.$store.state.dashboard_endpoint}/data/powertools/get_accounts/`, {credentials: 'include'})
                .then(response => response.json()).then(data => {
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
<i18n>
{
    "en": {
        "title": "Switch Account",
        "intro": "This feature allows you to switch to another account, and use this site as them.",
        "reload_page_warning": "Important: refresh the page after choosing an account!",
        "select": "Select account to use, the account is instantly switched",
        "reload_list": "Reload account list",
        "switched_account": "Switched to account {0}. Refresh the page to use this account."
    },
    "nl": {
        "title": "Wissel van account",
        "intro": "Hiermee is te wisselen van account. Na een wissel voer je bijvoorbeeld scans uit vanuit die organisatie.",
        "reload_page_warning": "Let op: herlaad de pagina na het wisselen van account!",
        "select": "Selecteer het account om te gebruiken, wisselen gebeurd direct",
        "reload_list": "Lijst met accounts verversen",
        "switched_account": "Geswitched naar account {0}. Ververs de pagina om dit account te gebruiken."
    }
}
</i18n>