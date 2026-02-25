# Changelog
This is the changelog for the dashboard API.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## V1.0.1 - feb 2026
Added allauth endpoints for authentication using passkeys, oidc, recovery codes and all that. The endpoint is
/api/v1/allauth/openapi.html.

## V1.0.0 - 2 december 2025
Released the first version of the dashboard API. It tries to adhere to the [NLGov REST API standard](https://logius-standaarden.github.io/publicatie/api/adr/2.1.0/).

Note that while that our openapi.json file will not specify the API-Version in response headers due to a technical 
limitation. The API actually does send the version header in every response.

### Added
- First public API version release
- Using the ORJSON renderer for speed
- Added a contact.info section
