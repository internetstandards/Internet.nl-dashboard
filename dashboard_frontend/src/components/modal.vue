<style scoped>
/*
Vue Modal
@see https://vuejs.org/v2/examples/modal.html
*/
.modal-mask {
    position: fixed;
    z-index: 9998;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, .5);
    display: table;
    transition: opacity .3s ease;
}

.modal-wrapper {
    display: table-cell;
    vertical-align: middle;
}

.modal-container {
    max-height: 90vh;
    overflow: scroll;

    width: 600px;
    margin: 0px auto;
    padding: 20px 30px;
    background-color: #fff;
    border-radius: 2px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, .33);
    transition: all .3s ease;
    font-family: Helvetica, Arial, sans-serif;
}

.modal-body {
    margin: 20px 0;
}

.modal-default-button {
    float: right;
}

/*
 * The following styles are auto-applied to elements with
 * transition="modal" when their visibility is toggled
 * by Vue.js.
 *
 * You can easily play with the modal transition by editing
 * these styles.
 */

.modal-enter {
    opacity: 0;
}

.modal-leave-active {
    opacity: 0;
}

.modal-enter .modal-container,
.modal-leave-active .modal-container {
    -webkit-transform: scale(1.1);
    transform: scale(1.1);
}

.defaultbutton {
    display: block;
    margin: 0 auto .5em;
    background: #fff;
    border: solid .3em #ffab4c;
    font-family: arial, sans-serif;
    font-weight: bold;
    font-size: 100%;
    border-radius: 18px;
    padding: .2em .5em
}

.defaultbutton button:hover, .block button:focus, .block button:active {
    background: #ffab4c
}

.defaultbutton button:hover {
    cursor: pointer
}

.defaultbutton button:focus {
    outline: none
}

.altbutton {
    display: block;
    margin: 0 auto .5em;
    background: #fff;
    border: solid .3em #878f96;
    font-family: arial, sans-serif;
    font-weight: bold;
    font-size: 100%;
    border-radius: 18px;
    padding: .2em .5em
}

.altbutton button:hover, .block button:focus, .block button:active {
    background: #ffab4c
}

.altbutton button:hover {
    cursor: pointer
}

.altbutton button:focus {
    outline: none
}

.dialog_warning {
    font-weight: bold;
}

.inl-modal-header h1, .inl-modal-header h2, .inl-modal-header h3, .inl-modal-header h4 {
    font-size: 1.4em;
}

.inl-modal-header{
    color: white;
    padding-bottom: 0.5em;
}

.inl-modal-footer {
    text-align: right;
}
.modal-container {
    background-color: white;
    background: linear-gradient(180deg, #00BFD6 0%, #00BFD6 70px, white 70px, rgba(255,255,255,1) 100%);
    border-radius: 4px;
}
.inl-modal-body{
    padding-top: 20px;
}

.inl-modal-body label {
    font-weight: bold !important;
    margin-bottom: 0 !important;
}

</style>
<template>
    <transition name="modal">
        <div class="modal-mask" @keyup.esc="$emit('close');">
            <div class="modal-wrapper">
                <div class="modal-container">

                    <div class="inl-modal-header">
                        <button style="float:right;" type="button" class="close altbutton" data-dismiss="modal" aria-label="Close" @click="$emit('close')">
                            <span aria-hidden="true">&times;</span>
                        </button>
                        <slot name="header">
                            default header
                        </slot>

                    </div>

                    <div class="inl-modal-body">
                        <slot name="body">
                            default body
                        </slot>
                    </div>

                    <div class="inl-modal-footer">
                        <slot name="footer">
                            default footer
                            <button class="modal-default-button" @click="$emit('close')">
                                OK
                            </button>
                        </slot>
                    </div>
                </div>
            </div>
        </div>
    </transition>
</template>
<script>
export default {
    mounted: function () {
        // focus on the default button for keyboard users.
        // todo: should it be the first input, and how do you do that easily / sanely
        document.getElementsByClassName('modal-default-button')[0].focus();
    },
}
</script>
