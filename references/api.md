# Official API and runtime notes

Reviewed 2026-10-08. Public documentation is authoritative for the target account/version.

## [Local API](https://localapi-doc-en.adspower.com/)

AdsPower desktop Local API is an external runtime requirement.

## [Create profile](https://localapi-doc-en.adspower.com/docs/XDhI2D)

POST /api/v1/user/create accepts proxy and fingerprint configuration.

## [Start browser](https://localapi-doc-en.adspower.com/docs/FFMFMf)

GET /api/v1/browser/start mutates browser state and must be gated.

## [Proxy configuration](https://localapi-doc-en.adspower.com/docs/Lb8pOg)

Official supported proxy types include http, https and socks5.

## Boundaries

Python 3.10+ and the AdsPower desktop application running with Local API access. Set `ADSPOWER_PROXY_URL` or `ADSPOWER_PROXY_URL_FILE` using a secret manager/private file. If Local API authentication is enabled, set `ADSPOWER_API_KEY` or `_FILE`. API default: `http://127.0.0.1:50325`.

Requires a compatible AdsPower installation, subscription/API access and installed browser kernel. Does not buy proxies, test exit geolocation, automate logins, guarantee anonymity or bypass access controls. Default fingerprint settings are minimal; no forced macOS user agent.

HTTP helpers do not follow redirects or automatically retry writes. A timeout can mean an unknown outcome; inspect the target before retrying. Secret-field redaction is defense in depth, not a guarantee that arbitrary free text is safe to publish.
