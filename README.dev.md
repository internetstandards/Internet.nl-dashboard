# Development readme

## NPM
Installing package: npm install --prefix dashboard/internet_nl_dashboard/static/js/ [package]
See outdated packages: npm --prefix dashboard/internet_nl_dashboard/static/js/ outdated
Security audit: npm --prefix dashboard/internet_nl_dashboard/static/js/ audit
Update package: npm --prefix dashboard/internet_nl_dashboard/static/js/ update [package]

Uninstalling package: npm --prefix dashboard/internet_nl_dashboard/static/js/ uninstall [package]

'''Do NOT EVER use npm remove, as it removed all deps without warning. Good luck installing everything again.'''

Can break things: 

Update insecure packages: npm --prefix dashboard/internet_nl_dashboard/static/js/ audit fix
Updating outdated packages: npm


### Used packages
* chart.js
* chartjs-plugin-datalabels
* dropzone
* jquery
* lodash
* moment
* patternomaly
* vue
* vue-i18n
* vue-multiselect
* vue-router
* vue-select
* vue-tabs-component
* All in one: chart.js chartjs-plugin-datalabels dropzone jquery lodash moment patternomaly vue vue-i18n vue-multiselect vue-router vue-select vue-tabs-component
