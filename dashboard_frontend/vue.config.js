// The syntax and complexity in this file is in unacceptable condition.
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
    }
}