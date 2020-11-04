<style>
.server-response-error {
    border: 1px solid silver;
    border-radius: 5px;
    padding: 10px;
    margin-bottom: 10px;
    background-color: #f9e0e4;
    color: darkred;
}

.server-response-success{
    border: 1px solid silver;
    border-radius: 5px;
    padding: 10px;
    margin-bottom: 10px;
    background-color: #daffda;
    color: #004f00;
}
</style>
<template>
    <div role="alert">
        <div v-if="response.error" class="server-response-error">
            <h2>❌ {{ $t('error') }}</h2>
            <p>
                <span v-if="!message">{{ response.message }}</span>
                <span v-if="message">{{ message }}</span>
            </p>
        </div>
        <div v-if="response.success" class="server-response-success">
            <h2>✅ {{ $t('success') }}</h2>
            <p>
                <span v-if="!message">{{ response.message }}</span>
                <span v-if="message">{{ message }}</span>
            </p>
        </div>
    </div>
</template>
<script>
export default {
    props: {
        response: {
            type: Object,
            default: null,
        },
        // This compponent does not have access to it's parent. To keep it simple, just allow a direct translation.
        message: {
            type: String,
            default: ""
        }
    }
}
</script>
<i18n>
{
    "en": {
        "error": "An error occurred",
        "success": "Success!"
    },
    "nl": {
        "error": "Er is iets mis gegaan",
        "success": "Gelukt!"
    }
}
</i18n>