<template>
    <div>
        <p>{{ $t("intro") }}</p>
        <div v-for="scan_form in scan_methods" :key="scan_form.name">
            <b-tabs v-if="scan_form.name === report_type && Object.keys(issue_filters).length > 0">
                <b-tab :title="$t('main_category')">
                    <h4>{{ $t("main_category") }}</h4>

                    <b-form-checkbox v-model="issue_filters[scan_form.name].show_dynamic_average" switch>
                        {{ $t("show_dynamic_average") }}
                    </b-form-checkbox>
                    <br><br>
                </b-tab>

                <b-tab v-for="category in scan_form.categories" :title="category.label" :key="category.label">
                    <section class="test-header">
                        <div class="test-title">
                            <h4>{{ category.label }}</h4>
                            <p>
                                <span v-for="field in category.fields" :key="field.id">
                                    <b-form-checkbox v-model="issue_filters[field.name].show_dynamic_average"
                                                     @change="visible_metrics_see_if_category_is_relevant(category)"
                                                     switch>
                                        {{ $t("show_dynamic_average") }}
                                    </b-form-checkbox>
                                    <br>
                                </span>
                            </p>
                        </div>
                    </section>
                    <section class="testresults">
                        <span class="select-deselect-category">
                            <a @click="check_fields(all_field_names_from_categories(category))"> {{ $t("check") }} </a>
                            /
                            <a @click="uncheck_fields(all_field_names_from_categories(category))">
                                {{ $t("uncheck") }}
                            </a>
                        </span>

                        <div v-for="category in category.categories" :key="category.name">
                            <div class="test-subsection">{{ category.label }}<br></div>
                            <div v-for="field in category.fields" :key="field.name" class="testresult_without_icon">

                                <b-form-checkbox
                                    v-model="issue_filters[field.name].visible" :id="field.name + '_visible'"
                                    switch>
                                    {{ $t(field.name) }}
                                </b-form-checkbox>

                                <template v-if="field.explanation">
                                    <p><i>{{ $t(field.name + "_explanation") }}</i></p>
                                </template>
                            </div>
                        </div>
                    </section>
                </b-tab>
            </b-tabs>
        </div>
        <div>
            <button @click="reset_issue_filters()">{{ $t("buttons.reset") }}</button>
            <button @click="save_visible_metrics()">{{ $t("buttons.save") }}</button>
            <br>
            <template v-if="issue_filters_response.success || issue_filters_response.error">
                <div :class="'server-response-' + issue_filters_response.state">
                        <span>
                            {{ $t(issue_filters_response.message) }}
                            on {{ humanize_date(issue_filters_response.timestamp) }}.
                        </span>
                </div>
            </template>
        </div>
    </div>
</template>

<script>
import field_translations from './../field_translations'
import {mapState} from 'vuex'

export default {
    i18n: {
        sharedMessages: field_translations,
    },
    name: "VisibleMetrics",
    props: {
        scan_methods: {
            type: Array
        },
        report_type: {
            type: String,
            default: "web",
        }
    },
    data: function () {
        return {
            issue_filters_response: {},
            issue_filters: {}
        }
    },
    mounted: function () {
        this.load_visible_metrics();
    },
    methods: {
        reset_issue_filters: function () {
            fetch(`${this.$store.state.dashboard_endpoint}/data/account/report_settings/get/`, {credentials: 'include'}).then(response => response.json()).then(data => {
                if (!this.isEmptyObject(data)) {
                    this.issue_filters = data.data;
                    this.issue_filters_response = data;
                }
            });
            this.load_issue_filters();

        },

        all_field_names_from_categories(categories) {
            let fields = [];
            categories.categories.forEach((category) => {
                category.fields.forEach((field) => {
                    fields.push(field.name);
                });
            });
            return fields;
        },

        save_visible_metrics: function () {
            /*
            * This overrides the account level issue filters. Filters are saved per account and this is done by
            * design. This prevents the 'having to reset for each report or for each user' dilemma, which results
            * in some kind of hierarchical settings mess that results in incomparable reports over several users.
            * And then the users need to sync the settings and so on. Knowing this limitation would probably remove
            * a lot of time of development while end users can still have an organization wide consistent experience
            * on what they are focussing on. Humans > tech.
            * */
            this.asynchronous_json_post(
                `${this.$store.state.dashboard_endpoint}/data/account/report_settings/save/`, {'filters': this.issue_filters}, (server_response) => {
                    this.issue_filters_response = server_response;
                    if (server_response.success) {
                        // load the metrics into the application
                        this.load_visible_metrics();
                    }
                }
            );
        },
        check_fields: function (list_of_fields) {
            list_of_fields.forEach((field) => {
                this.issue_filters[field].visible = true;
            })
        },

        uncheck_fields: function (list_of_fields) {
            list_of_fields.forEach((field) => {
                this.issue_filters[field].visible = false;
            })
        },
        visible_metrics_see_if_category_is_relevant: function (category_name) {
            // if all fields in the category are deselected, deselect the category, otherwise, select it.
            // console.log(category_name);

            let fields = this.all_subcategory_fields_from_category(category_name);
            // console.log(fields)

            let should_be_visible = false;
            for (let i = 0; i < fields.length; i++) {

                // alerting if fields are missing:
                if (this.issue_filters[fields[i]] === undefined) {
                    console.log(`Missing field ${fields[i]} in issue filters.`)
                }

                if (this.issue_filters[fields[i]].visible) {
                    should_be_visible = true;
                    break;
                }
            }

            this.issue_filters[category_name.key].visible = should_be_visible;
        },
        all_subcategory_fields_from_category(category_name) {
            const mail = 1;
            const web = 0;
            let fields = [];
            let method = (this.report_type === 'mail') ? mail : web;

            this.scan_methods[method].categories.forEach((category) => {
                // console.log(`Comparing ${category.key} to ${category_name.key}.`)
                if (category.key === category_name.key) {
                    category.categories.forEach((subcategory) => {
                        subcategory.fields.forEach((field) => {
                            fields.push(field.name);
                        });
                    });
                }
            });
            return fields;
        },
    },
    computed: mapState(['visible_metrics']),
    watch: {
        visible_metrics: function (new_value) {
            this.issue_filters = new_value;
        }
    }
}
</script>

<style>
.select-deselect-category {
    font-size: 0.9em;
    display: block;
    width: 100%;
    text-align: right;
    padding-top: 5px;
    padding-bottom: 10px;
}
</style>
<i18n>
{
    "en": {
        "check": "Select all",
        "uncheck": "Deselect all",
        "title": "Select visible metrics",
        "main_category": "Average adoption of standards",
        "intro": "To retain focus, select the fields that are relevant to your organization.",
        "buttons": {
            "reset": "Reset",
            "reset_label": "Resets all values to their original status.",
            "save": "Save",
            "save_label": "Save the changes made in this form."
        },
        "show_category": "Show this category",
        "show_dynamic_average": "Show the average of selected fields",
        "only_show_dynamic_average": "Only show dynamic average",
        "settings": {
            "restored_from_database": "Settings restored from database",
            "updated": "Settings updated"
        }
    },
    "nl": {
        "check": "Selecteer alle",
        "uncheck": "Deselecteer alle",
        "title": "Selecteer zichtbare meetwaarden",
        "main_category": "Adoptie van standaarden",
        "intro": "Selecteer de velden die relevant zijn voor uw organisatie.",
        "buttons": {
            "reset": "Reset",
            "reset_label": "Zet de originele waardes terug naar de waardes in de database",
            "save": "Opslaan",
            "save_label": "Sla de wijzigingen in de zichtbare meetwaarden op."
        },
        "show_category": "Toon deze categorie",
        "show_dynamic_average": "Toon het gemiddelde van de geselecteerde velden",
        "only_show_dynamic_average": "Toon alleen het dynamisch berekende gemiddelde",
        "settings": {
            "restored_from_database": "Zichtbare meetwaarden zijn teruggezet naar de waardes in de database",
            "updated": "Zichtbare meetwaarden opgeslagen"
        }
    }
}
</i18n>