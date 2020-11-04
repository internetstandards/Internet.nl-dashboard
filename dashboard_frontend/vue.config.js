// The syntax and complexity in this file is in unacceptable condition.

// from https://bootstrap-vue.org/docs, Aliasing Vue import
const path = require('path')

module.exports = {
    chainWebpack: config => {
        config.module
            .rule("i18n")
            .resourceQuery(/blockType=i18n/)
            .type('javascript/auto')
            .use("i18n")
            .loader("@kazupon/vue-i18n-loader")
            .end();
        config
            .plugin('html')
            .tap(args => {
                args[0].title = "Internet.nl Dashboard";
                return args;
            })
        config.resolve.alias.set(
            'vue$',
            // If using the runtime only build
            path.resolve(__dirname, 'node_modules/vue/dist/vue.runtime.esm.js')
            // Or if using full build of Vue (runtime + compiler)
            // path.resolve(__dirname, 'node_modules/vue/dist/vue.esm.js')
        )
    }
}