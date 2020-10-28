<script>

export default {
    methods: {
        // todo: can we change the locale for moment.js on the fly?
        humanize_date: function (date) {
            // Uses localized date and time format with day name, which is pretty advanced and complete
            return this.$moment(date).format('LLLL');
        },
        humanize_date_date_only: function (date) {
            // Uses localized date and time format with day name, which is pretty advanced and complete
            return this.$moment(date).format('LL');
        },
        humanize_relative_date: function (date) {
            // says things like 'days ago'...
            return this.$moment(date).fromNow();
        },
        humanize_duration: function (duration_in_milliseconds) {
            return this.$moment.duration(duration_in_milliseconds).humanize()
        },
        humanize_filesize: function (size_in_bytes, decimals = 0) {
            if (size_in_bytes === 0) return '0 Bytes';
            let k = 1024,
                dm = decimals <= 0 ? 0 : decimals || 2,
                sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'],
                i = Math.floor(Math.log(size_in_bytes) / Math.log(k));
            return parseFloat((size_in_bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
        }
    }
};
</script>
