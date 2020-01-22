{% verbatim %}
<script>
Vue.component('server-response', {
    props: ['response'],
    template: '' +
        '<div>' +
        '    <div v-if="response.error" class="server-response-error">\n' +
        '        <h2>❌ An error occured</h2><br>\n' +
        '        <span>{{ response.message }}</span>\n' +
        '    </div>\n' +
        '    <div v-if="response.success" class="server-response-success">\n' +
        '        <h2>✅ Success!</h2><br>\n' +
        '        <span>{{ response.message }}</span>\n' +
        '    </div>' +
        '</div>',
});
</script>
{% endverbatim %}
