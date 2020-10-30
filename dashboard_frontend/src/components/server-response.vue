<template type="text/x-template" id="server_response_template">
    <div role="alert">
        <div v-if="response.error" class="server-response-error">
            <h2>❌ {{ $t('error') }}</h2><br>
            <span v-if="!message">{{ response.message }}</span>
            <span v-if="message">{{ message }}</span>
        </div>
        <div v-if="response.success" class="server-response-success">
            <h2>✅ {{ $t('success') }}</h2><br>
            <span v-if="!message">{{ response.message }}</span>
            <span v-if="message">{{ message }}</span>
        </div>
    </div>
</template>
<script>
export default {
    i18n: {
        messages: {
            en: {
                error: 'An error occurred',
                success: "Success!",
            },
            nl: {
                error: 'Er is een foutsituatie opgetreden',
                success: "Gelukt!",
            }
        }
    },
    // message was added as a prop as the parent translation / the component that uses this component does not share
    // its translated messages.
    props: {
        response: {
            type: Object,
            default: null,
        },
        message: {
            type: String,
            default: ""
        }
    },
    template: 'server_response_template',

    mounted: function(){
        this.$i18n.locale = this.locale;
    }
}
</script>
