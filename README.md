### AWS Route 53

Boto3 documentation: [https://boto3.amazonaws.com/](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/route53.html#route53)


### File white-domains-auto-reg.py
Automate registration and zone creation in AWS-route53 for WHITE-group domains.
If the wildcard option is set, both will be created (simple-GEO and wildcard-GEO)

Syntax: `white-domains-auto-reg.py [file]`

Example:
```
# python3 white-domains-auto-reg.py example.txt

devtest1.com available, continue... 
devtest1.com ns-1517.awsdns-61.org 
ns-1552.awsdns-02.co.uk ns-764.awsdns-31.net ns-334.awsdns-41.com 
Registration for devtest1.com started 
1. devtest1.com
NS change done 
```

File syntax example.txt: `domain_name|us_ip|eu_ip|as_ip|oc_ip  or  *.domain_name|us_ip|eu_ip|as_ip|oc_ip`
```
devtest1.com|10.0.0.1|10.0.0.2|10.0.0.3|10.0.0.4
*.devtestapi3.io|127.0.0.1|127.0.0.1|127.0.0.1|127.0.0.1
```


### File route53-create-new-domain.py
Create domain zone with GEO records. 
If the wildcard option is set, both will be created (simple-GEO and wildcard-GEO)

Syntax: `route53-create-new-domain.py [file]`

Example:
```
# python3 route53-create-new-domain.py example.txt
test.domain-geo01.com ns-1253.awsdns-28.org ns-1818.awsdns-35.co.uk ns-697.awsdns-23.net ns-421.awsdns-52.com
*.devtestapi3.io ns-1155.awsdns-16.org ns-808.awsdns-37.net ns-1672.awsdns-17.co.uk ns-264.awsdns-33.com
Wildcard added for devtestapi3.io
```

File syntax example.txt: `domain_name|us_ip|eu_ip|as_ip  or  *.domain_name|us_ip|eu_ip|as_ip`
```
test.domain-geo01.com|10.0.0.1|20.0.0.1|30.0.0.1|40.0.0.1
*.devtestapi3.io|127.0.0.1|127.0.0.1|127.0.0.1|127.0.0.1
```


### File route53-update-geo-records.py
Update GEO records by code US/EU/AS
If the wildcard option is set, both will be updated (simple-GEO and wildcard-GEO)

Syntax: `route53-update-geo-records.py [file]`

Example:
```
# python3 route53-update-geo-records.py example.txt
UPDATE FOR DOMAIN: test.domain-geo01.com ZONE_ID: Z0600171CB5W3U0RNIBS
```

File syntax example.txt: `domain_name|geo_code|eu_ip  or  *.domain_name|geo_code|eu_ip`
```
testi.domain-geo-us.com|US|10.0.0.1
*.domain-geo-eu.com|EU|20.0.0.1
testas.domain-geo-as.com|AS|30.0.0.1
*.domain-geo-oc.com|OC|40.0.0.1
```

GEO Codes:

| Code | Real location |
| :---: | --- |
| EU | AF - Africa<br/>AN - Antarctica<br/>EU - Europe<br/>RU - Russia<br/>UA - Ukraine |
| US | NA - North America<br/>SA - South America |
| AS | AS - Asia |
| OC | OC - Oceania |


### File route53-set-localhost.py
Set domain GEO-records to localhost (127.0.0.1). 
If the wildcard option is set, both will be change (simple-GEO and wildcard-GEO)

Syntax: `route53-set-localhost.py [file]`

Example:
```
# python3 route53-set-localhost.py example.txt
UPDATE FOR DOMAIN: devtestapi.io ZONE_ID: Z06033502BYSSALTU7I
```

File syntax example.txt: `domain_name`
```
devtestapi.io
domain-geo01.com
domain-geo02.com
```
