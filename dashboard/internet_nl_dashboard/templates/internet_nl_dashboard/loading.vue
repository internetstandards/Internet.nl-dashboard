{% verbatim %}
<script>
Vue.component('loading', {
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

    template: `
    <div v-if="loading" class="block fullwidth loading">
        <div class="loading">
             <div class="lds-dual-ring"><div></div><div></div></div> <span>{{ $t("loading") }}</span>
        </div>
    </div>`,

    data: function () {
        return {
            // loading: false,
        }
    },

    props:{
        loading: false,
    },
});
</script>
{% endverbatim %}
