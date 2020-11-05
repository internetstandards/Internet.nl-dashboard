<style scoped>
.panel-content {
    padding-bottom: 10px;
    padding-left: 20px;
}

.collapse_panel {
    border-top: 1px solid gray;
    border-bottom: 1px solid gray;
    margin-top: 10px;
    margin-bottom: 10px;
}

.panel-title {
    font-size: 1.0em;
    font-weight: normal;
}

.panel-title:hover {
    text-decoration: underline;
}

button {
    border: 0 !important;
    color: dimgray;
    font-weight: bold !important;
}

button:hover {
    background-color: inherit;
}

.animate_opening {
    transition: transform 300ms linear;
    transform: rotate(0deg);
    display: inline-block;
}

.animate_opening.open {
    transform: rotate(180deg);
    transition: transform 300ms linear;
}

.block button:hover, .block button:focus, .block button:active {
    background: white
}

.level_two {
  padding-left: 2em;
    font-size: 0.9em;
}

.level_three {
  padding-left: 3em;
    font-size: 0.8em;
}


</style>

<template>
    <div class="collapse_panel">
        <button
            :class="status_visible ? null : 'collapsed'"
            :aria-expanded="status_visible ? 'true' : 'false'"
            :aria-controls="'collapse-' + id"
            @click="status_visible = !status_visible"
        >
            <span :class="`panel-title ${custom_title_class}`">
               <div :class="status_visible ? 'animate_opening open' : 'animate_opening'">
                    <img src="/static/images/vendor/internet_nl/push-open.png" alt="open panel">
                </div>
                {{ title }}
            </span>
        </button>

        <b-collapse :id="'collapse-' + id" v-model="status_visible" class="panel-content">
            <slot name="content">
                default content
            </slot>
        </b-collapse>
    </div>
</template>

<script>
export default {
    name: "collapse_panel",
    mounted: function () {
        // generated random id for this thing to be collapsable. Chance to be the same is 1 in 1 000 000 000 000.
        this.id = Math.round((Math.random() * 1000000000000));

        // support being open on start using :visible.
        this.status_visible = this.visible;
    },
    data: function () {
        return {
            // random ID so the button knows what element to collapse or expand.
            id: 0,
            status_visible: false,
        }
    },
    props: {
        title: {
            type: String,
            default: ""
        },
        visible: {
            type: Boolean,
            default: false,
        },
        custom_title_class: {
            type: String,
            default: ""
        }
    }

}
</script>
