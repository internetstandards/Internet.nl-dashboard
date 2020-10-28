<script>
export default {
    methods: {
        // this can probably be replaced with axio or whatever. Or not if we want tos ave on dependencies.
        asynchronous_json_post: function (url, data, callback) {
            // the context parameter is somewhat dangerous, but this allows us to say 'self.' in the callback.
            // which could be done somewhat better.
            // https://stackoverflow.com/questions/20279484/how-to-access-the-correct-this-inside-a-callback
            let server_response = {};
            // console.log(`Posting to ${url}, with data ${data}`)
            (async () => {
                const rawResponse = await fetch(url, {
                    method: 'POST',
                    credentials: 'include',
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.get_cookie('csrftoken')
                    },
                    body: JSON.stringify(data)
                });
                try {
                    // here is your synchronous part.
                    server_response = await rawResponse.json();
                } catch (e) {
                    // SyntaxError: JSON.parse: unexpected character at line 1 column 1 of the JSON data
                    server_response = {'error': true, 'message': 'Server error'}
                }
                callback(server_response)
            })();
        },
        get_cookie: function (name) {
            let value = "; " + document.cookie;
            let parts = value.split("; " + name + "=");
            if (parts.length === 2) return parts.pop().split(";").shift();
        }
    }
};
</script>
