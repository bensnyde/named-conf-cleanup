import dns.resolver
import os.path
import re

named_conf = "./named.conf"
self_nameserver_address = ['ns1.example.com.', 'ns2.example.com.']

fh = open(named_conf)

data = ""
for line in fh.readlines():
    data += line.strip()

fh.close()

start = data.find('directory "')+11
end = data.find('"', start)
directory = data[start:end]

to_remove = []
for domain in re.compile(r'zone "(?P<domain>.+?)" \{.+?file ".+?".+?\}\;', re.DOTALL).split(data):
    if domain[:1].isalpha() and not domain.startswith('options') and not domain.endswith('.ARPA'):
        if not os.path.isfile("%s/%s.db" % (directory, domain)):
            to_remove.append({"domain": domain, "reason": "Database not found."})
            continue

        try:
            ns_records = []
            for record in dns.resolver.query(domain, 'NS'):
                ns_records.append(record.to_text())

            if not len(set(ns_records).intersection(self_nameserver_address)):
                to_remove.append({"domain": domain, "reason": "Domain's NS record points elsewhere."})
        except:
            to_remove.append({"domain": domain, "reason": "Domain has no NS record."})

for domain in [x["domain"] for x in to_remove]:
    print '/^zone "%s" {/,/^};/d;' % domain

# python enumerate_named_conf.py > sedcmds
# sed -f sedcmds named.conf > named.temp
