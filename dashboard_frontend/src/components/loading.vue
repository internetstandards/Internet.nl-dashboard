<template>
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
    props: {
        loading: {
            type: Boolean,
            default: false
        },
    },
}
</script>
<i18n>
{
    "en": {
        "loading": "Loading..."
    },
    "nl": {
        "loading": "Laden..."
    }
}
</i18n>
