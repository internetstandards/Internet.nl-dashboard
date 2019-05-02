<!--
This can do:

Done: create new lists
Done: configure lists
Done: add domains
Done: delete lists
Done: edit url
Done: delete url
Done: cancel what you're doing using escape
Done: support scan types
Done: show lists, including last scan moment
Done: Sorting of urls by domain and then subdomains.
Done: support 'scan now' button.
Done: what happens when the edited url is not valid?
Done: Add new list to the top.
Done: when scan now is clicked, disable scan now button.
Done: pasting too many urls in the select2 causes an overflow. Size it properly.
Done: Show link to last report
Todo: translation
Todo: Bulk add has a bug when only adding 1 to the list, the list of submitted domains is not updated often enough / not reactive.
Todo: When a list is added, the urls of each list are not moved to the next list. This is not reactive and might case issues.
Todo: when deleting a list, it is re-added to the list of lists when adding a new list, this is not reactive and causes issues.
 (most of the above errors would be solved if we would only add things to the end of the list?). Adding the "add new" button to the bottom would quickfix this.
-->
{% verbatim %}
<template type="x-template" id="lists">
    <div>
        <modal v-if="show_add_new" @close="stop_adding_new()">
            <h3 slot="header">{{ $t("domains.add_new_list") }}</h3>

            <div slot="body">

                <server-response :response="add_new_server_response"></server-response>

                <label for="name">{{ $t("urllist.field_label_name") }}:</label><br>
                <input id="name" type="text" maxlength="120" v-model="add_new_new_list.name"><br><br>

                <label for="enable_scans">{{ $t("urllist.field_label_enable_scans") }}:</label><br>
                <input id="enable_scans" type="checkbox" v-model="add_new_new_list.enable_scans"><br><br>

                <label for="scan_type">{{ $t("urllist.field_label_scan_type") }}:</label><br>
                <select id="scan_type" v-model="add_new_new_list.scan_type">
                    <option value="web">{{ $t("urllist.scan_type_web") }}</option>
                    <option value="mail">{{ $t("urllist.scan_type_mail") }}</option>
                </select><br><br>

                <label for="automated_scan_frequency">{{ $t("urllist.field_label_automated_scan_frequency") }}:</label><br>
                <select id="automated_scan_frequency" v-model="add_new_new_list.automated_scan_frequency">
                    <option value="disabled">{{ $t("urllist.automated_scan_frequency_disabled") }}</option>
                    <option value="every half year">{{ $t("urllist.automated_scan_frequency_every_half_year") }}</option>
                    <option value="at the start of every quarter">{{ $t("urllist.automated_scan_frequency_every_quarter") }}</option>
                    <option value="every 1st day of the month">{{ $t("urllist.automated_scan_frequency_every_month") }}</option>
                    <option value="twice per month">{{ $t("urllist.automated_scan_frequency_twice_per_month") }}</option>
                </select>

            </div>
            <div slot="footer">
                <button @click="stop_adding_new()">{{ $t("domains.button_close_label") }}</button>
                <button class="modal-default-button" @click="create_list()">{{ $t("domains.button_create_list_label") }}</button>
            </div>
        </modal>

        <button @click="start_adding_new()">{{ $t("domains.add_new_list") }}</button>

        <div v-for="list in lists" >
            <managed-url-list :initial_list="list"></managed-url-list>
        </div>

    </div>
</template>
{% endverbatim %}

<script>
vueListManager = new Vue({
    i18n,
    name: 'list_manager',
    el: '#list_manager',
    template: '#lists',
    mixins: [http_mixin],
    data: {
        loading: false,
        lists: [],

        // everything that has something to do with adding a new list:
        show_add_new: false,
        add_new_server_response: {},
        add_new_new_list: {}
    },
    mounted: function () {
        this.get_lists();
    },
    methods: {
        get_lists: function(){
            this.loading = true;
            fetch(`/data/urllists/get/`).then(response => response.json()).then(data => {
                this.lists = data;
                this.loading = false;
            }).catch((fail) => {console.log('A loading error occurred: ' + fail);});
        },
        start_adding_new: function(){
            this.add_new_new_list = {'id': -1, 'name': '', 'enable_scans': false, 'scan_type': 'web',
                'automated_scan_frequency': 'disabled', 'scheduled_next_scan': '1'};
            this.show_add_new = true;
            this.add_new_server_response = {};
        },
        stop_adding_new: function() {
            this.show_add_new = false;
        },
        create_list: function() {
            this.asynchronous_json_post(
                '/data/urllist/create_list/', this.add_new_new_list, (server_response) => {
                    this.add_new_server_response = server_response;
                    // if we get data back, the addition was succesful.
                    if (!jQuery.isEmptyObject(this.add_new_server_response.data)){

                        // The managed url list has a property and internal list object. This internal list object is
                        // updated using a watch. This pattern is required to retain reactivity of the 'lists' object
                        // in this manager.

                        // If we would not do this, it's not possible to add to the top of the list, as the list is
                        // not truely reactive. You could then only add to the bottom of the list. Otherwise the last
                        // item of the lists was cloned.
                        // Doing it properly retains reactivity such as unshifting and reversing the list.
                        this.lists.unshift(this.add_new_server_response.data);
                        this.show_add_new = false;
                    }
                });
        }
    }
});
</script>
