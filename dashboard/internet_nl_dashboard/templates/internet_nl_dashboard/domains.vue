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
Todo: what happens when the edited url is not valid?
Todo: Add new list to the top.
Todo: when scan now is clicked, disable scan now button.
Todo: pasting too many urls in the select2 causes an overflow. Size it properly.
Todo: translation
-->
{% verbatim %}
<template type="x-template" id="lists">
    <div>
        <modal v-if="show_new" @close="stop_adding_new()">
            <h3 slot="header">Add new list</h3>

            <div slot="body">

                <div v-if="add_new_response.error" class="server-response-error">
                    <h2>❌ Not saved</h2>
                    {{ add_new_response.message }}
                </div>
                <div v-if="add_new_response.success" class="server-response-success">
                    <h2>✅ Saved!</h2>
                    {{ add_new_response.message }}
                </div>

                <label for="name">List name:</label>
                <input id="name" type="text" maxlength="120" v-model="new_list.name"><br><br>

                <label for="enable_scans">Enable scans:</label>
                <input id="enable_scans" type="checkbox" v-model="new_list.enable_scans"><br><br>

                <label for="scan_type">What scan to run:</label>
                <select id="scan_type" v-model="new_list.scan_type">
                    <option value="web">Web</option>
                    <option value="mail">Mail</option>
                </select><br><br>

                <label for="automated_scan_frequency">How often should the scan run?:</label>
                <select id="automated_scan_frequency" v-model="new_list.automated_scan_frequency">
                    <option value="disabled">Disabled</option>
                    <option value="every half year">Every half year</option>
                    <option value="at the start of every quarter">At the start of every quarter</option>
                    <option value="every 1st day of the month">Every 1st day of the month</option>
                    <option value="twice per month">Twice per month</option>
                </select>

            </div>
            <div slot="footer">
                <button @click="stop_adding_new()">Close</button>
                <button class="modal-default-button" @click="create_list()">Create List</button>
            </div>
        </modal>

        <button @click="start_adding_new()">Add new list</button>

        <managed-url-list v-for="list in lists" :initial_list="list"></managed-url-list>

    </div>
</template>

<style>
.managed-url-list{
    border: 1px solid silver;
    border-radius: 5px;
    padding: 10px;
    margin-bottom: 20px;
    background-color: ghostwhite;
}

.inline-edit input {
    margin-bottom: 0px !important;
}

.inline-edit button {
    font-size: 0.7em !important;
    margin: 0px !important;
    height: 23px;
}

.url-in-managed-list{
    margin-bottom: 5px;
    width:100%;
}

.view-csv{
    width:100%;
    height: 200px;
}

.select2-selection--multiple{
    height: 200px;
    width: 100%;
}

</style>
<template type="x-template" id="managed-url-list">
    <article class="managed-url-list" v-if="!is_deleted">
        <h3>
            <button v-if="!is_opened" @click="open_list()" value="load">📘 {{ list.name }}</button>
            <button v-if="is_opened" @click="close_list()" value="load">📖 {{ list.name }}</button>

            <div v-if="is_opened" style="float:right;">
                <button @click="start_editing_settings()">📝 Configure</button>
                <button @click="start_bulk_add_new()">💖 Add domains</button>
                <button @click="start_scan_now()" v-if="list.scan_now_available">🔬 Scan Now</button>
                <button @click="alert('The scan now option is available only once a day, when no scan is running.')" v-if="!list.scan_now_available" disabled="disabled"
                title="The scan now option is available only once a day.">🔬 Scan Now</button>
                <button @click="start_deleting()">🔪 Delete</button>
            </div>
        </h3>
        <br>

        <div v-if="is_opened">
            <h4>About this list</h4>
            <span v-if="list.last_scan">
                Last scan started: {{ humanize_date(list.last_scan) }}.
                <span v-if="!list.last_scan_finished">(still running)</span>
                <span v-if="list.last_scan_finished">(finished)</span>
            </span>
            <span v-if="!list.last_scan">
                Last scan started: Not scanned before.
            </span>
            <div class="scan-configuration">
                <div v-if="list.enable_scans">
                    Type of scan performed:
                    <span title="Web scans will be performed" v-if="list.enable_scans && list.scan_type === 'mail'">📨</span>
                    <span title="Web scans will be performed" v-if="list.enable_scans && list.scan_type === 'web'">🌐</span>
                    <span title="No scans will be performed" v-if="!list.enable_scans">🚫</span>
                    {{ list.scan_type }} <br>
                    Scan frequency: {{ list.automated_scan_frequency }} <br>
                    <div v-if="list.automated_scan_frequency !== 'disabled'">
                        Next scheduled scan: {{ humanize_date(list.scheduled_next_scan) }} <br>
                    </div>
                </div>
                <div v-if="!list.enable_scans">
                    Scanning of this list is disabled.
                </div>
            </div>
            <br>

            <h4>Domains</h4>
            <br>
            <div style="column-count: 2;">
                <div v-for="url in urls" class="url-in-managed-list">

                    <span v-if="url.has_mail_endpoint === true" title="Is eligeble for e-mail scans">
                        <a :href="'https://www.internet.nl/mail/' + url.url + '/'" target="_blank">📨</a>
                    </span>
                    <span v-if="url.has_mail_endpoint === 'unknown'" title="Not yet known if scanable for mail">❓</span>
                    <span v-if="url.has_mail_endpoint === false" title="Is not eligeble for e-mail scans">🚫</span>
                    <span v-if="url.has_web_endpoint === true" title="Is eligeble for web scans">
                        <a :href="'https://www.internet.nl/site/' + url.url + '/'" target="_blank">🌐</a>
                    </span>
                    <span v-if="url.has_web_endpoint === 'unknown'" title="Not yet known if scannable for web">❓</span>
                    <span v-if="url.has_web_endpoint === false" title="Is not eligeble for web scans">🚫</span>

                    <span title="Edit this domain" @click="start_url_editing(list.id, url.url)">🖊</span>
                    <a v-if="!url_is_edited(list.id, url.url)" @click="start_url_editing(list.id, url.url)">{{ url.url }}</a>
                    <!-- (<a :href="'https://' + url.url" target="_blank" rel="noreferrer">open</a>) -->

                    <span class="inline-edit" v-if="url_is_edited(list.id, url.url)">
                            <input autofocus :placeholder="url.url" :value="url.url" :id="'' + list.id + url.url">
                            <button @click="save_edit_url({'list_id': list.id,'url_id': url.id, 'new_url_string': get_url_edit_value()})">Save</button>
                            <button @click="cancel_edit_url()">Cancel</button>
                            <!-- The remove is real, as it will only remove 1 items -->
                            <button @click="remove_edit_url(list.id, url.id)">Remove</button>
                    </span>
                </div>
            </div>
            <br>
            <button v-if="urls.length" @click="toggle_view_csv()" value="load">📋 view .csv</button><br>
            <textarea v-if="view_csv" class="view-csv" :value="csv_value"></textarea>
        </div>

        <!-- modal dialogs are below the content to make sure the tab order stays working. -->
        <modal v-if="show_list_settings" @close="cancel_editing_settings()">
            <h3 slot="header">🖊 Edit list settings</h3>
            <div slot="body">
                <div v-if="settings_update_response.error" class="server-response-error">
                    <h2>❌ Not saved</h2>
                    {{ settings_update_response.message }}
                </div>
                <div v-if="settings_update_response.success"  class="server-response-success">
                    <h2>✅ Saved!</h2>
                    {{ settings_update_response.message }}
                </div>

                <label for="name">List name:</label><br>
                <input id="name" type="text" maxlength="120" v-model="list.name"><br><br>

                <label for="enable_scans">Enable scans:</label><br>
                <input id="enable_scans" type="checkbox" v-model="list.enable_scans">
                <span v-if="list.enable_scans">Enabled</span>
                <span v-if="!list.enable_scans">Disabled</span>
                <br><br>

                <label for="scan_type">What scan to run:</label><br>
                <select id="scan_type" v-model="list.scan_type">
                        <option value="web">Web</option>
                        <option value="mail">Mail</option>
                </select><br><br>

                <label for="automated_scan_frequency">How often should the scan run?:</label><br>
                <select id="automated_scan_frequency" v-model="list.automated_scan_frequency">
                    <option value="disabled">Disabled</option>
                    <option value="every half year">Every half year</option>
                    <option value="at the start of every quarter">At the start of every quarter</option>
                    <option value="every 1st day of the month">Every 1st day of the month</option>
                    <option value="twice per month">Twice per month</option>
                </select>

            </div>
            <div slot="footer">
                <button @click="cancel_editing_settings()">Close</button>
                <button class="modal-default-button" @click="update_list_settings()">Update</button>
            </div>
        </modal>

        <modal v-if="show_deletion" @close="stop_deleting()">
            <h3 slot="header">Delete list</h3>
            <div slot="body">
                <div v-if="delete_response.error" class="server-response-error">
                    <h2>❌ Could not delete</h2>
                    {{ delete_response.message }}
                </div>
                <div v-if="delete_response.success" class="server-response-success">
                    <h2>✅ Deleted!</h2>
                    {{ delete_response.message }}
                </div>

                <p class="warning">Are you sure you want to
                delete this list? Deleting this list cannot be undone.</p>

                <label for="name">List name:</label><br>
                {{ list.name }}<br>
                <br>

                <label for="enable_scans">Enable scans:</label><br>
                {{ list.enable_scans }}<br>
                <br>

                <label for="scan_type">What scan to run:</label><br>
                {{ list.scan_type }}<br>
                <br>

                <label for="automated_scan_frequency">How often should the scan run?:</label><br>
                {{ list.automated_scan_frequency }}<br>
                <br>

            </div>
            <div slot="footer">
                <button @click="stop_deleting()">Cancel</button>
                <button class="modal-default-button" @click="confirm_deletion()">Delete</button>
            </div>
        </modal>

        <modal v-if="show_scan_now" @close="stop_scan_now()">
            <h3 slot="header">Confirm to scan now</h3>
            <div slot="body">
                <div v-if="scan_now_server_response.error" class="server-response-error">
                    <h2>❌ Could not scan</h2>
                    {{ delete_response.message }}
                </div>
                <p>Todo: tekst...</p>

                <p>To start a scan now, please take the following in consideration:</p>
                <p>A scan can only be started once a day, and only when no scan is already running. Note that a scan cannot be cancelled.</p>

            </div>
            <div slot="footer">
                <button @click="stop_scan_now()">Cancel</button>
                <button class="modal-default-button" @click="confirm_scan_now()">Scan now</button>
            </div>
        </modal>

        <modal v-if="show_bulk_add_new" @close="stop_bulk_add_new()">
            <h3 slot="header">Bulk add domains</h3>
            <div slot="body">
                <div v-if="bulk_add_new_server_response.error" class="server-response-error">
                    <h2>❌ Error</h2>
                    {{ bulk_add_new_server_response.message }}
                </div>

                <p>You can add many domains in one go. To do this, seperate each domain with a comma.</p>
                <select2 v-model="bulk_add_new_urls"></select2>

                <div v-if="bulk_add_new_server_response">
                    <span v-if="bulk_add_new_server_response.success === true">
                        Status: Added {{ bulk_add_new_server_response.data.added_to_list }} domains to this list.
                        <span v-if="bulk_add_new_server_response.data.already_in_list">
                            Additionally, {{ bulk_add_new_server_response.data.already_in_list }} domains have been
                            ignored as they are already in this list.<br>
                        </span>
                        <span v-if="bulk_add_new_server_response.data.incorrect_urls.length">
                            <br><b>Warning!</b><br>
                            Some domains where not added because they are in an incorrect format. <br>
                            The following domains where not added:
                                {{ bulk_add_new_server_response.data.incorrect_urls.join(', ') }}<br>
                        </span>
                    </span>
                    <span v-if="bulk_add_new_server_response.error === true">
                        An error happened while trying to add these domains to the list. The server responded with
                        the following message: {{ bulk_add_new_server_response.message }}.
                    </span>
                </div>
                <div v-if="!bulk_add_new_server_response.message">
                    <p>Status: nothing added yet.</p>
                </div>
                <br>
                <button @click="bulk_add_new()">Add the above domains to the list</button>

            </div>
            <div slot="footer">
            </div>
        </modal>
    </article>
</template>

<template type="text/x-template" id="select2-template">
  <select style="width: 95%" multiple="multiple">
    <slot></slot>
  </select>
</template>
{% endverbatim %}

<script>
Vue.component('modal', {
  template: '#modal-template'
});

Vue.component('select2', {
    // https://vuejs.org/v2/examples/select2.html
  props: ['options', 'value'],
  template: '#select2-template',
  mounted: function () {
    var vm = this;
    $(this.$el)
      // init select2
      .select2({
        placeholder: 'example.com, www.example.com, www.internet.nl, ...',
        tags: true,
        tokenSeparators: [',', ' '],
        // hides the no results box, as this is pure tagbox only
        // @see: https://stackoverflow.com/questions/18470917/disable-no-matches-found-text-and-autocomplete-on-select2
        "language":{
            "noResults" : function () { return ''; }
        },
          multiple: true,

        createTag: function (params) {
            // This is an extremely naive implementation of domain validation. On the server tldextract is
            // used which is much more complete as it uses the public suffixes list.
            // This is just a convenience check that something with a dot is entered.
            let term = $.trim(params.term);

            // use the most naive (fast) 'url' validator. All validation is done server side anyway, and
            // verifying that something is an url with unicode characters and such is not really a thing.
            var pattern = new RegExp('^.*\\..{2,}$'); // domain name
            if (!pattern.test(term)) {
                return null;
            }

            if (term === '') {
                return null;
            }

            return {
                id: term,
                text: term,
            }
        }
    }).val(
        this.value
      ).trigger('change')
      // emit event on change.
      .on('change', function () {
          console.log('change');
          // Ok, this was not easy to figure out. This is the most old school approach of getting all option values.
          // I would expect to run .val() or someething, but that didn't update etc..
          // this approach is not reactive, but it doesn't need to be.
          let my_data = [];
            for (let i = 0; i < this.options.length; i++) {
                my_data.push(this.options[i].text);
            }

          console.log(my_data);
          vm.$emit('input', my_data)  // can't get all...
      })
  },
    /* this does not update:
    computed: {
      // at least this works...
        all_options: function(){
            return $(this.$el).val();
        }
    },*/
  destroyed: function () {
    $(this.$el).off().select2('destroy')
  }
});

// todo: add new, remove, drag to other list(?)
vueListManager = new Vue({
    name: 'list_manager',
    el: '#list_manager',
    template: '#lists',
    mixins: [http_mixin],
    data: {
        loading: false,
        lists: [],

        // everything that has something to do with adding a new list:
        show_new: false,
        add_new_loading: false,
        add_new_response: {},
        new_list: {}
    },
    mounted: function () {
        this.load();
        document.addEventListener('keyup', this.close_all_windows_on_escape);
    },
    methods: {

        close_all_windows_on_escape (e) {
            // a naive escpe to close dialog option
            if (e.keyCode === 27) {
                this.show_new = false;
            }
        },

        load: function() {
            this.get_lists();
        },
        get_lists: function(){
            this.loading = true;
            fetch(`/data/urllists/get/`).then(response => response.json()).then(data => {
                this.lists = data;
                this.loading = false;
            }).catch((fail) => {console.log('A loading error occurred: ' + fail);});
        },
        start_adding_new: function(){
            this.new_list = {'id': -1, 'name': '', 'enable_scans': false, 'scan_type': 'web',
                'automated_scan_frequency': 'disabled', 'scheduled_next_scan': '1'};
            this.show_new = true;
            this.add_new_response = {};
        },
        stop_adding_new: function() {
            this.show_new = false;
        },
        create_list: function() {
            this.add_new_loading = true;
            this.asynchronous_json_post(
                '/data/urllist/create_list/', this.new_list, this, function(self, server_response){
                    self.add_new_response = server_response;
                    if (!jQuery.isEmptyObject(self.add_new_response.data)){
                        // todo: should we order the list alphabetically / or re-apply the orderering there is now?
                        // how do we scroll to the new list?
                        // is it possible to have a an animation on everything that is added to the list?

                        // add the item at the beginning, as it's the closest to the add button.
                        // could also add it alphabetically, but that doesn't really help as the list might get lost
                        // in the many lists out there. (doesn't work)
                        self.lists.push(self.add_new_response.data);

                        // todo: validate correct.
                        self.show_new = false;
                    }
                    self.add_new_loading = false;
                });
        }
    }
});

Vue.component('managed-url-list', {
    mixins: [humanize_mixin, http_mixin],

    data: function () {
        return {
            urls: [],
            is_opened: false,

            loading: false,

            // contains all known list data, should not be needed to individually fetch the list (again), only
            // after update.
            list: this.initial_list,

            // everything to do with settings.
            show_list_settings: false,
            settings_loading: false,
            settings_update_response: {},
            old_list_settings: {},

            // everything to do with deleting this list
            show_deletion: false,
            delete_response: {},
            // is deleted is set to hide one of the managers. It will not be shown next load anyway and you can't
            // edit it anymore server side.
            is_deleted: false,

            // everything to do with editing urls in the list:
            url_edit: '',
            original_url_value: '',

            // everything that has to do with adding urls:
            show_bulk_add_new: false,
            bulk_add_new_urls: [],
            bulk_add_new_server_response: {},

            // everything to do with csv:
            view_csv: false,

            // scan now feature:
            show_scan_now: false,
            scan_now_server_response: {}
        }
    },
    mounted: function () {
        document.addEventListener('keyup', this.close_all_windows_on_escape);
    },
    props: {
        initial_list: Object,
    },
    methods: {
        close_all_windows_on_escape (e) {
            // a naive escpe to close dialog option
            if (e.keyCode === 27) {
                this.stop_editing_settings();
                this.stop_deleting();
                this.cancel_edit_url();
                this.show_bulk_add_new = false;
                this.view_csv = false;
                this.show_scan_now = false;
            }
        },

        open_list: function(){
            this.get_urls();
            this.is_opened = true;
        },
        close_list: function(){
          this.is_opened = false;
        },
        get_urls: function(){
            this.loading = true;
            fetch(`/data/urllist_content/get/${this.list.id}/`).then(response => response.json()).then(data => {
                this.urls = data.urls;
                this.loading = false;
            }).catch((fail) => {console.log('A loading error occurred: ' + fail);});
        },
        update_list_settings: function(){
            this.settings_loading = true;

            this.asynchronous_json_post(
                '/data/urllist/update_list_settings/', this.list, this, function (self, server_response) {
                    console.log(server_response);
                    self.settings_update_response = server_response;
                    self.settings_loading = false;

                    // The upcoming scan date has probably changed, and we want to reflect that in the UI.
                    self.list = server_response.data;
                    // make sure the cancel button goes to the last save.
                    self.old_list_settings = self.copy_values(self.list);

                    if (server_response.success){
                        self.stop_editing_settings();
                    }
                });
        },
        start_editing_settings: function(){
            // keep an old value in memory. If the editing is canceled, the old value should be used.
            // here a weakness is of js is showing:
            // https://stackoverflow.com/questions/728360/how-do-i-correctly-clone-a-javascript-object
            // luckily we can use the simple approach...
            this.old_list_settings = this.copy_values(this.list);
            this.settings_update_response = {};
            this.show_list_settings = true;
        },
        stop_editing_settings: function(){
            this.show_list_settings = false;
            this.settings_update_response = {};
        },
        cancel_editing_settings: function(){
            this.list = this.copy_values(this.old_list_settings);
            this.stop_editing_settings();
        },
        copy_values: function(obj){
            // does not copy methods.
            return JSON.parse(JSON.stringify(obj));
        },
        start_deleting: function(){
            this.show_deletion = true;
            this.delete_response = {};
        },
        stop_deleting: function(){
            this.show_deletion = false;
            this.delete_response = {};
        },
        confirm_deletion: function() {
            this.asynchronous_json_post(
                '/data/urllist/delete/', {'id': this.list.id}, this, function (self, server_response) {
                    self.delete_response = server_response;

                    if (server_response.success){
                        // remove / hide this thing...
                        self.is_deleted = true;
                        self.stop_deleting();
                    }
                }
            );
        },
        start_url_editing: function(list_id, url_id){
            this.url_edit = '' + list_id + url_id;
            this.original_url_value = url_id;
            // after the item is rendered.
            this.$nextTick(() => document.getElementById(this.url_edit).focus());
        },
        url_is_edited: function(list_id, url_id){
            return this.url_edit === '' + list_id + url_id
        },
        cancel_edit_url: function(){
            if (!this.url_edit)
                return;

            if (document.getElementById(this.url_edit)){
                document.getElementById(this.url_edit).value = this.original_url_value;
            }
            this.url_edit = '';
        },
        get_url_edit_value: function(){
            return document.getElementById(this.url_edit).value;
        },
        remove_edit_url: function(list_id, url_id){
            // todo
            data = {'list_id': list_id, 'url_id': url_id};
            this.asynchronous_json_post(
                '/data/urllist/url/delete/', data, this, function (self, server_response) {
                    self.delete_response = server_response;

                    // todo: check if deletion was succesful.
                    self.urls.forEach(function(item, index, object) {
                        if (url_id === item.id) {
                            object.splice(index, 1)
                        }
                    });
                }
            );
        },
        save_edit_url: function(data){
            /*
            * This is not a real 'save' but an add to list and create if it doesn't exist operation.
            * The save does not 'alter' the existing URL in the database. It will do some list operations.
            * */
            // todo
            this.asynchronous_json_post(
                '/data/urllist/url/save/', data, this, function (self, server_response) {
                    // self.url_redit_response = server_response;

                    // todo: if not succesful, then store the original value...
                    if (server_response['success'] === true){
                        self.url_edit = '';
                        // and make sure the current url list is updated as well. Should'nt this be data bound and
                        // such?
                        self.urls.forEach(function(item, index, object) {
                        if (server_response.data.removed.id === item.id) {
                            object[index] = server_response.data.created;
                            // object.splice(index, 1);
                            // object.push(server_response.data.created)
                        }
                    });
                    } else {
                        document.getElementById(self.url_edit).value=self.original_url_value;
                    }
                }
            );

        },

        start_bulk_add_new: function(){
            this.show_bulk_add_new = true;
        },
        stop_bulk_add_new: function(){
            this.show_bulk_add_new = false;

            // re-load the url list, as perhaps more information about endpoints is discovered.
            this.get_urls();
        },
        bulk_add_new: function(){
            // todo: edit new list doesn't work, no ID in this list?
            // todo: post bulk_add_new_urls and handle the response. It will have a number of added urls and some
            // feedback on what urls where not added. (just like import spreadsheet).
            // Getting bulk_add_new_urls to work was pretty difficult due to too many layers of abstractions.

            data = {'urls': this.bulk_add_new_urls, 'list_id': this.list.id};

            this.asynchronous_json_post(
                '/data/urllist/url/add/', data, this, function (self, server_response) {
                    // {'incorrect_urls': [], 'added_to_list': int, 'already_in_list': int}
                    self.bulk_add_new_server_response = server_response;

                    // Update the list of urls accordingly.
                    self.get_urls();
                    // clean the select2 box?
                }
            );
        },
        toggle_view_csv: function(){
            this.view_csv = !this.view_csv;
        },
        start_scan_now: function(){
            this.show_scan_now = true;
        },
        stop_scan_now: function(){
            this.show_scan_now = false;
        },
        confirm_scan_now: function(){
            data = {'id': this.list.id};

            this.asynchronous_json_post(
                '/data/urllist/scan_now/', data, this, function (self, server_response) {
                    self.scan_now_server_response = server_response;
                    self.stop_scan_now()
                }
            );
        }
    },
    computed: {
       csv_value: function(){
           urls = [];
           this.urls.forEach(function(item) {
               urls.push(item.url);
           });
           return urls.join(', ');
       }
    },
    template: '#managed-url-list'
});
</script>
