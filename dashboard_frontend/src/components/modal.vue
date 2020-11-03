<template>
    <transition name="modal">
        <div class="modal-mask"  @keyup.esc="$emit('close');">
            <div class="modal-wrapper">
                <div class="modal-container">

                    <div class="modal-header">
                        <button style="float:right;" type="button" class="close altbutton" data-dismiss="modal"
                                aria-label="Close" @click="$emit('close')">
                            <span aria-hidden="true">&times;</span>
                        </button>
                        <slot name="header">
                            default header
                        </slot>

                    </div>

                    <div class="modal-body">
                        <slot name="body">
                            default body
                        </slot>
                    </div>

                    <div class="modal-footer">
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
