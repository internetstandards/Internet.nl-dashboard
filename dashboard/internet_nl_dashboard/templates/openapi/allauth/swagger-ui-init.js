const csrfSettings = document.querySelector("body").dataset;
const configObject = {
    url: csrfSettings.openapiUrl,
    dom_id: "#swagger-ui",
    layout: "BaseLayout",
    deepLinking: true,
    presets: [
        SwaggerUIBundle.presets.apis,
        SwaggerUIBundle.SwaggerUIStandalonePreset,
    ],
};

if (csrfSettings.apiCsrf && csrfSettings.csrfToken) {
    configObject.requestInterceptor = (req) => {
        req.headers["X-CSRFToken"] = csrfSettings.csrfToken;
        return req;
    };
}

SwaggerUIBundle(configObject);
