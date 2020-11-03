<template>
    <div>
        <p>{{ $t("intro") }}</p>
        <div v-for="scan_form in scan_methods" :key="scan_form.name">
            <template v-if="scan_form.name === report_type && Object.keys(issue_filters).length > 0">

                <tabs :options="{ useUrlFragment: false }">
                    <tab :name="$t('main_category')">
                        <h3>{{ $t("main_category") }}</h3>
                        <br>
                        <p>
                            <label :for="scan_form.name + '_show_dynamic_average'">
                                <input type="checkbox"
                                       v-model="issue_filters[scan_form.name].show_dynamic_average"
                                       :id="scan_form.name + '_show_dynamic_average'">
                                {{ $t("show_dynamic_average") }}
                            </label><br>
                            <!-- disabled as per #107
                            <label :for="scan_form.name + '_only_show_dynamic_average'">
                                <input type="checkbox"
                                       v-model="issue_filters[scan_form.name].only_show_dynamic_average"
                                       :id="scan_form.name + '_only_show_dynamic_average'"
                                        :disabled="!issue_filters[scan_form.name].show_dynamic_average">
                                {{ $t("only_show_dynamic_average") }}
                            </label>
                            -->

                            <template v-if="scan_form.additional_fields.length">
                                <div class="test-subsection">{{
                                        $t("fields.additional_fields.label")
                                    }}
                                </div>
                                <div v-for="field in scan_form.additional_fields"
                                     class="testresult_without_icon" :key="field">
                                    <label :for="field.name + '_visible'">
                                        <input type="checkbox"
                                               v-model="issue_filters[field.name].visible"
                                               :id="field.name + '_visible'">
                                        {{ $t(field.name) }}
                                    </label>
                                </div>
                            </template>
                        </p>

                        <div>
                            <button @click="reset_issue_filters()">{{
                                    $t("buttons.reset")
                                }}<span class="visuallyhidden"></span></button>
                            <button @click="save_visible_metrics()">{{ $t("buttons.save") }}<span
                                class="visuallyhidden"></span></button>
                            <br>
                            <template
                                v-if="issue_filters_response.success || issue_filters_response.error">
                                <div :class="'server-response-' + issue_filters_response.state">
                                                    <span>{{
                                                            $t(issue_filters_response.message)
                                                        }} on {{
                                                            humanize_date(issue_filters_response.timestamp)
                                                        }}.</span>
                                </div>
                            </template>
                        </div>

                    </tab>

                    <tab v-for="category in scan_form.categories" :name="category.label"
                         :key="category.label">
                        <section class="test-header">
                            <div class="test-title">
                                <h3>{{ category.label }}</h3>
                                <br>
                                <p>
                                    <span v-for="field in category.fields" :key="field.id">

                                        <label :for="field.name + '_show_dynamic_average'"
                                               :key="field.name">
                                            <input type="checkbox"
                                                   v-model="issue_filters[field.name].show_dynamic_average"
                                                   :onchange="visible_metrics_see_if_category_is_relevant(category)"
                                                   :id="field.name + '_show_dynamic_average'">
                                            {{ $t("show_dynamic_average") }}
                                        </label><br>
                                        <!-- Disabled as per #107
                                        <label :for="field.name + '_only_show_dynamic_average'">
                                            <input type="checkbox"
                                                   v-model="issue_filters[field.name].only_show_dynamic_average"
                                                   :id="field.name + '_only_show_dynamic_average'"
                                                    :disabled="!issue_filters[field.name].show_dynamic_average">
                                            {{ $t("only_show_dynamic_average") }}
                                        </label>
                                        -->
                                    </span>
                                </p>

                            </div>
                        </section>
                        <section class="testresults">
                            <span class="select-deselect-category"><a
                                @click="check_fields(all_field_names_from_categories(category))">{{
                                    $t("check")
                                }}</a> / <a
                                @click="uncheck_fields(all_field_names_from_categories(category))">{{
                                    $t("uncheck")
                                }}</a></span>

                            <div v-for="category in category.categories" :key="category.name">
                                <div class="test-subsection">{{ category.label }}<br></div>
                                <div v-for="field in category.fields" :key="field.name"
                                     class="testresult_without_icon">
                                    <label :for="field.name + '_visible'" :key="field.name">
                                        <input type="checkbox"
                                               v-model="issue_filters[field.name].visible"
                                               :id="field.name + '_visible'">
                                        {{ $t(field.name) }}
                                    </label>
                                    <template v-if="field.explanation">
                                        <p><i>{{ $t(field.name + "_explanation") }}</i></p>
                                    </template>
                                </div>

                                <template v-if="category.additional_fields.length">
                                    <div class="test-subsection">{{
                                            $t("fields.additional_fields.label")
                                        }}
                                    </div>
                                    <div v-for="field in category.additional_fields"
                                         class="testresult_without_icon" :key="field.name">
                                        <label :for="field.name + '_visible'" :key="field.name">
                                            <input type="checkbox"
                                                   v-model="issue_filters[field.name].visible"
                                                   :id="field.name + '_visible'">
                                            {{ $t(field.name) }}
                                        </label>
                                        <template v-if="field.explanation">
                                            <p><i>{{ $t(field.name + "_explanation") }}</i></p>
                                        </template>
                                    </div>
                                </template>

                            </div>
                        </section>

                        <div>
                            <button @click="reset_issue_filters()">{{ $t("buttons.reset") }}<span
                                class="visuallyhidden"></span></button>
                            <button @click="save_visible_metrics()">{{ $t("buttons.save") }}<span
                                class="visuallyhidden"></span></button>
                            <br>
                            <template
                                v-if="issue_filters_response.success || issue_filters_response.error">
                                <div :class="'server-response-' + issue_filters_response.state">
                                    <span>{{
                                            $t(issue_filters_response.message)
                                        }} on {{ humanize_date(issue_filters_response.timestamp) }}.</span>
                                </div>
                            </template>
                        </div>

                    </tab>
                </tabs>

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
                category.additional_fields.forEach((field) => {
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

            let fields = this.all_subcategory_fields_from_category(category_name);

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
            let fields = [];

            let i = 0;
            // hack to get the right stuff from the scan methods. Should be done differently.
            if (this.selected_category === 'mail')
                i = 1;


            this.scan_methods[i].categories.forEach((category) => {

                if (category.key !== category_name.key) {
                    return
                }

                category.categories.forEach((subcategory) => {
                    subcategory.fields.forEach((field) => {
                        fields.push(field.name);
                    });
                    subcategory.additional_fields.forEach((field) => {
                        fields.push(field.name);
                    });
                });

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


.tabs-component {
    margin: 1em 0;
}

.tabs-component-tabs {
    border: solid 1px #ddd;
    border-radius: 6px;
    margin-bottom: 5px;
}

@media (min-width: 700px) {
    .tabs-component-tabs {
        border: 0;
        align-items: stretch;
        display: flex;
        justify-content: flex-start;
        margin-bottom: -1px;
    }
}

.tabs-component-tab {
    color: #999;
    font-size: 14px;
    font-weight: 600;
    margin-right: 0;
    list-style: none;
}

.tabs-component-tab:not(:last-child) {
    border-bottom: dotted 1px #ddd;
}

.tabs-component-tab:hover {
    color: #666;
}

.tabs-component-tab.is-active {
    color: #000;
}

.tabs-component-tab.is-disabled * {
    color: #cdcdcd;
    cursor: not-allowed !important;
}

@media (min-width: 700px) {
    .tabs-component-tab {
        background-color: #fff;
        border: solid 1px #ddd;
        border-radius: 3px 3px 0 0;
        margin-right: .5em;
        transform: translateY(2px);
        transition: transform .3s ease;
    }

    .tabs-component-tab.is-active {
        border-bottom: solid 1px #fff;
        z-index: 2;
        transform: translateY(0);
    }
}

.tabs-component-tab-a {
    align-items: center;
    color: inherit;
    display: flex;
    padding: .75em 1em;
    text-decoration: none;
}

.tabs-component-panels {
    padding: 1em 0;
    margin-top: -22px;
}

@media (min-width: 700px) {
    .tabs-component-panels {
        border-top-left-radius: 0;
        background-color: #fff;
        border: solid 1px #ddd;
        border-radius: 0 6px 6px 6px;
        box-shadow: 0 0 10px rgba(0, 0, 0, .05);
        padding: 4em 2em;
        padding-top: 2em;
        padding-bottom: 2em;
        margin-top: -22px;
    }
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
        "restored_from_database": "Settings restored from database",
        "updated": "Settings updated",
        "show_category": "Show this category",
        "show_dynamic_average": "Show the average of selected fields",
        "only_show_dynamic_average": "Only show dynamic average"
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
        "restored_from_database": "Zichtbare meetwaarden zijn teruggezet naar de waardes in de database",
        "updated": "Zichtbare meetwaarden opgeslagen",
        "show_category": "Toon deze categorie",
        "show_dynamic_average": "Toon het gemiddelde van de geselecteerde velden",
        "only_show_dynamic_average": "Toon alleen het dynamisch berekende gemiddelde"
    }
}
</i18n>