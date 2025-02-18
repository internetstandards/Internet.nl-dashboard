from dns.resolver import Resolver
from websecmap.app.constance import constance_cached_value


def check_dns_resolvers():
    # this checks the configured dns resolver and alerts if something does not resolve.
    # This is made for debugging purposes only.

    nameservers = constance_cached_value("SCANNER_NAMESERVERS")
    for server in nameservers:
        check_dns_resolver(server)


def check_dns_resolver(server) -> bool:
    resolver = Resolver()
    resolver.nameservers = [server]

    search_domain = constance_cached_value("CONNECTIVITY_TEST_DOMAIN")

    try:
        resolver.resolve(search_domain, "A", search=True)
        print(f"Resolved {search_domain} on {server}")
        return True
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Did not resolve {search_domain} on {server}. Error: {exc}")
        return False
