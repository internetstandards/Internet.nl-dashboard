<style scoped>
.loading {
    padding: 17px;
    text-align: center;
}

.loading span {
    display: inline-block;
    font-size: 2em;
    color: dimgray;
}
</style>
<template>
    <div v-if="loading" class="fullwidth loading">
        <div class="loading">
            <b-spinner variant="info" label="Spinning" style="width: 2rem; height: 2rem;"></b-spinner>
            &nbsp;
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
