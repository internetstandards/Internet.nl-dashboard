{% verbatim %}
<script>
Vue.component('server-response', {
    props: ['response'],
    template: '' +
        '<div>' +
        '    <div v-if="response.error" class="server-response-error">\n' +
        '        <h2>❌ An error occured</h2>\n' +
        '        {{ response.message }}\n' +
        '    </div>\n' +
        '    <div v-if="response.success" class="server-response-success">\n' +
        '        <h2>✅ Success!</h2>\n' +
        '        {{ response.message }}\n' +
        '    </div>' +
        '</div>',
});
</script>
{% endverbatim %}
