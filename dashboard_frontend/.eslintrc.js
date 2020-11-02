// https://stackoverflow.com/questions/58742881/vuejs-vue-cli-how-can-i-use-console-log-without-getting-any-errors
module.exports = {
  root: true,
  env: {
    node: true
  },
  'extends': [
    'plugin:vue/essential',
    'eslint:recommended'
  ],
  rules: {
    /* The console can be purposefully used as part of the point and click adventure style of this site. */
    'no-console': process.env.NODE_ENV === 'production' ? 'off' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'off'
  },
  parserOptions: {
    parser: 'babel-eslint'
  },
}
