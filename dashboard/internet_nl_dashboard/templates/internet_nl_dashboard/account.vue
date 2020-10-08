{% verbatim %}
<template type="text/x-template" id="account_template">
  <div>
    <div class="block fullwidth">
      <h1>{{ $t("title") }}</h1>

      <loading :loading="loading"></loading>

      <div v-if="null">
        <div class="server-response-success">
          <span>✅ {{ $t("success") }}</span>
        </div>
      </div>

      <div v-if="null">
        <div class="server-response-error">
          <span>❌ {{ $t("error") }}</span>
        </div>
      </div>

      <a href="/account/two_factor/">Setup / Change Two Factor Authentication</a>

    </div>
  </div>
</template>
{% endverbatim %}
<script>
const Account = Vue.component('account', {
  i18n: {
    messages: {
      en: {
        title: 'Account',
        intro: "Manage your account.",
      },
      nl: {
        title: 'Account',
        intro: "Beheer je account.",
      }
    }
  },
  data: function () {
    return {
      loading: false,
    }
  },
  mounted: function () {
      this.get_account_data()
  },
  methods: {
    get_account_data: function () {
      this.loading = true;
      fetch(`/data/account/`).then(response => response.json()).then(data => {

        this.loading = false;
      }).catch((fail) => {
        this.error_occurred = true;
        console.log('A loading error occurred: ' + fail);
      });
    },
  },
  name: 'account',
  template: '#account_template',
});
</script>
