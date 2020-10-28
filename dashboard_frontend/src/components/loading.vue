<template type="x-template" id="loading_template">
    <div v-if="loading" class="fullwidth loading">
        <div class="loading">
            <div class="lds-dual-ring">
                <div></div>
                <div></div>
            </div>
            <span>{{ $t("loading") }}</span>
        </div>
    </div>
</template>

<script>
export default {
    i18n: {
        messages: {
            en: {
                loading: "Loading...",
            },
            nl: {
                loading: "Laden...",
            }
        }
    },

    template: 'loading_template',

    data: function () {
        return {
            // loading: false,
        }
    },

    props: {
        loading: {
            type: Boolean,
            default: false
        },
    },
}
</script>
