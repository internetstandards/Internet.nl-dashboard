import Vue from 'vue'
import App from './App.vue'

Vue.config.productionTip = false

new Vue({
  render: h => h(App),
}).$mount('#app')

// https://stackoverflow.com/questions/50925793/proper-way-of-adding-css-file-in-vue-js-application
import './assets/css/styles.scss';
