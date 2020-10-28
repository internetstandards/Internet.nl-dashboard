<script>
import $ from 'jquery'

export default {
    methods: {
        // Creates accordeons in an old-school way
        // was taken from accordion-min.js and put in a function otherwise the accordions don't work.
        // todo: use new accordion system.
        accordinate: function () {
            $('.accordion').attr({role: 'tablist', multiselectable: 'true'});
            $('.panel-content').attr('id', function (IDcount) {
                return 'panel-' + IDcount;
            });
            $('.panel-content').attr('aria-labelledby', function (IDcount) {
                return 'control-panel-' + IDcount;
            });
            $('.panel-content').attr('aria-hidden', 'true');
            $('.accordion .panel-content').attr('role', 'tabpanel');
            $('.panel-title').each(function () {
                let target = $(this).next('.panel-content')[0].id;
                $('a', this).attr('href', '#' + 'control-' + target).attr('aria-controls', target).attr('id', 'control-' + target);
                let opentext = $('#panel-item-open').html();
                $('.pre-icon', this).text(opentext);
            });
            var hash = window.location.hash;
            // quick fix to prevent messing up loading SPA pages.
            if (hash != '' && hash.startsWith("control-panel")) {
                $(hash).attr('aria-expanded', true).addClass('active').parent().next('.panel-content').slideDown(200).attr('aria-hidden', 'false');
                this.setPanelItemFoldText($('.pre-icon', hash), 'close');
                this.refreshPanelButtonText($(hash), 'open');
            }

            // reset onclicks, because adding on-clicks stack: each one will be called causing the panel to open and close multiple times
            // after calling accordinate multiple times.
            $('.panel-title a').off("click").click(function () {
                let self = this;
                var stateObj = {foo: "bar"};
                if ($(this).attr('aria-expanded') == 'false') {
                    $(this).attr('aria-expanded', true).addClass('active').parent().next('.panel-content').slideDown(200).attr('aria-hidden', 'false');
                    self.setPanelItemFoldText($('.pre-icon', this), 'close');
                    self.refreshPanelButtonText($(this), 'open');
                    window.history.pushState(stateObj, null, "#" + $(this).attr('id'));
                } else {
                    $(this).attr('aria-expanded', false).removeClass('active').parent().next('.panel-content').slideUp(200).attr('aria-hidden', 'true');
                    history.pushState(stateObj, null, '#')
                    self.setPanelItemFoldText($('.pre-icon', this), 'open');
                    self.refreshPanelButtonText($(this), 'close');
                }
                return false;
            });
        },
        setPanelItemFoldText: function (panel_preicon, text) {
            if (text === 'open') {
                var openText = $('#panel-item-open').text();
                panel_preicon.text(openText);
            } else if (text === 'close') {
                var closeText = $('#panel-item-close').text();
                panel_preicon.text(closeText);
            }
        },
        refreshPanelButtonText: function (panel_a, action) {
            var testResults = panel_a.parents('.testresults');
            var testHeader = testResults.prev();
            var button = $('.panel-button-container button', testHeader);
            if (action === 'close' && $('.panel-title a', testResults).length === $('.panel-title', testResults).find('a[aria-expanded=false]').length) {
                button.addClass('panel-button-show').removeClass('panel-button-hide');
                var panelButtonShowText = $('#panel-button-show').text();
                button.text(panelButtonShowText);
            } else if (action === 'open' && $('.panel-title a', testResults).length === $('.panel-title', testResults).find('a[aria-expanded=true]').length) {
                button.addClass('panel-button-hide').removeClass('panel-button-show');
                var panelButtonHideText = $('#panel-button-hide').text();
                button.text(panelButtonHideText);
            }
        }
    }
};
</script>