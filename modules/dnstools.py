import re
import dns.resolver
import dns.reversename
from xbotpp import modules

__xbotpp_module__ = 'dnstools'

def lookitup(domain, type):
    if type == "A" or type == "AAAA":
        if re.search("^(?:[\w.-]+)(?<!\.)(?:\.[a-zA-Z]{2,6})+\.?$", domain):
            try:
                return dns.resolver.query(domain, type)
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                return False
    elif type == "PTR":
        if re.search("^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$", domain) or re.search("^\s*((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))(%.+)?\s*$", domain):
                try:
                    return dns.resolver.query(dns.reversename.from_address(domain), type)
                except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                    return False
    elif type:
        try:
            return dns.resolver.query(domain, type)
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            return False
    return -1

@modules.on_command('lookup')
def lookup(info, args, buf):
    if len(args) in [1, 2]:
        addresses = None
        
        if len(args) == 1:
            host = args[0]
            addresses = lookitup(host, "A")
        elif len(args) == 2:
            host = args[1]
            if args[0] == "-6":
                addresses = lookitup(host, "AAAA")
            elif args[0] == "-r":
                addresses = lookitup(host, "PTR")
            else:
                return "Usage: lookup [-6 (IPv6), -r (rDNS)] <server>"
            
        if addresses != -1:
            if addresses:
                plural = "others" if len(addresses) > 2 else "other"
                others = " (%s %s)" % (len(addresses), plural) if len(addresses) > 1 else ''
                return "Address: %s%s" % (addresses[0] if not str(addresses[0]).endswith(".") else str(addresses[0])[:-1], others)
            else:
                util.answer(bot, "%s: NXDOMAIN" % host)
        else:
            answer("Invalid host for this type of lookup.")
    else:
        return "Usage: lookup [-6 (IPv6), -r (rDNS)] <server>"

