<template type="text/x-template" id="unsubscribe_template">
    <div>
        <div class="block fullwidth">
            <h1>{{ $t("title") }}</h1>

            <loading :loading="loading"></loading>

            <div v-if="unsubscribed">
                <div class="server-response-success">
                    <span>✅ {{ $t("success") }}</span>
                </div>
            </div>

            <div v-if="error_occurred">
                <div class="server-response-error">
                    <span>❌ {{ $t("error") }}</span>
                </div>
            </div>

            <template v-if="show_unsubscribe_form">
                <p>{{ $t("intro") }}</p>

                <b>{{ $t("label_feed") }}</b><br>
                <input id="feed" type="text" maxlength="120" v-model="feed"><br><br>
                <br>
                <b>{{ $t("label_unsubscribe_code") }}</b><br>
                <input id="unsubscribe_code" type="text" maxlength="120" v-model="unsubscribe_code"><br><br>
                <template v-if="!unsubscribe_code || !feed">
                    <button class="defaultbutton modal-default-button" disabled>
                        {{ $t("perform_unsubscribe") }}
                    </button>
                </template>
                <template v-else>
                    <button class="defaultbutton modal-default-button" @click="unsubscribe()">
                        {{ $t("perform_unsubscribe") }}
                    </button>
                </template>
            </template>

        </div>
    </div>
</template>

<script>
export default {
    data: function () {
        return {
            feed: "",
            unsubscribe_code: "",
            unsubscribed: false,
            error_occurred: false,
            show_unsubscribe_form: false,
            loading: false,
        }
    },
    mounted: function () {
        // support: http://[]/spa/#/unsubscribe?feed=asdasd&unsubscribe_code=3819318
        if (this.$route.query.feed !== undefined) {
            this.feed = this.$route.query.feed;
        }
        if (this.$route.query.unsubscribe_code !== undefined) {
            this.unsubscribe_code = this.$route.query.unsubscribe_code;
        }

        // if both are set, just immediately unsubscribe.
        // and do not show the form to prevent confusion.
        if (this.feed && this.unsubscribe_code) {
            this.unsubscribe()
            this.show_unsubscribe_form = false;
        } else {
            this.show_unsubscribe_form = true;
        }
    },
    methods: {
        unsubscribe: function () {
            // credentials not needed
            // this will always take about a second to deter brute force / account guessing.
            this.loading = true;
            this.unsubscribed = false;
            this.error = false;
            fetch(`/mail/unsubscribe/${this.feed}/${this.unsubscribe_code}/`).then(response => response.json()).then(data => {
                if (data['unsubscribed']) {
                    this.unsubscribed = true;
                    this.error_occurred = false;
                }
                this.loading = false;
            }).catch((fail) => {
                this.error_occurred = true;
                console.log('A loading error occurred: ' + fail);
            });
        },
    },
    name: 'unsubscribe',
}
</script>
<i18n>
{
    "en": {
        "title": "Unsubscribe from alerts",
        "label_feed": "Feed",
        "label_unsubscribe_code": "Unsubscribe code (see e-mail)",
        "intro": "Using this form, you can unsubscribe from alerts. You can unsubscribe without being logged in. If you landed on this page from ",
        "error": "An error occured during unsubscribing. Try again below using the code and feed in your email.",
        "success": "Your subscription to this feed has been cancelled. You will no longer receive e-mails from this feed.",
        "perform_unsubscribe": "Unsubscribe from this feed"
    },
    "nl": {
        "title": "Geen meldingen ontvangen",
        "label_feed": "Meldingen",
        "label_unsubscribe_code": "Uitschrijfcode (zie e-mail)",
        "intro": "Met onderstaand formulier is het mogelijk om uit te schrijven voor meldingen. Het is niet nodig om in te loggen om je af te melden.",
        "error": "Er is een fout opgetreden bij het uitschrijven. Probeer het opnieuw met de code en feed uit de email.",
        "success": "Je bent succesvol afgemeld van deze meldingen. Je ontvangt deze meldingen niet meer per e-mail.",
        "perform_unsubscribe": "Afmelden van deze meldingen"
    }
}
</i18n>