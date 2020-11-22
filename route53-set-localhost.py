#!/usr/bin/env python3

import sys
import boto3
import json
import datetime

r53client = boto3.client('route53')
localhost = "127.0.0.1"
counter = 0
# File format: domain
domain_file = open(sys.argv[1], 'r').read().splitlines()

# Fix datetime for JSON
def default(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()

# Def for record create
def update_record(zone, domain):
    if zone == 'RU':
        zone_json={
            'Comment': 'UPDATE ZONE '+zone+' DOMAIN '+domain+ localhost,
            'Changes': [
                {
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': domain,
                        'Type': 'A',
                        'SetIdentifier': zone,
                        'GeoLocation': {
                            'CountryCode': zone
                        },
                        'TTL': 60,
                        'ResourceRecords': [
                            {
                                'Value': localhost
                            }
                        ]
                    }
                }
            ]
        }
    elif zone == 'UA':
        zone_json={
            'Comment': 'UPDATE ZONE '+zone+' DOMAIN '+domain+ localhost,
            'Changes': [
                {
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': domain,
                        'Type': 'A',
                        'SetIdentifier': zone,
                        'GeoLocation': {
                            'CountryCode': zone
                        },
                        'TTL': 60,
                        'ResourceRecords': [
                            {
                                'Value': localhost
                            }
                        ]
                    }
                }
            ]
        }
    else:
        zone_json={
            'Comment': 'UPDATE ZONE '+zone+' DOMAIN '+domain+ localhost,
            'Changes': [
                {
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': domain,
                        'Type': 'A',
                        'SetIdentifier': zone,
                        'GeoLocation': {
                            'ContinentCode': zone
                        },
                        'TTL': 60,
                        'ResourceRecords': [
                            {
                                'Value': localhost
                            }
                        ]
                    }
                }
            ]
        }

    return zone_json


# Read domain list
for domain in domain_file:
    counter += 1
    # Search domain and set zone_id
    list_hosted_zones_by_name = r53client.list_hosted_zones_by_name(DNSName=domain, MaxItems='1')
    list_hosted_zones_by_name_json = json.loads(json.dumps(list_hosted_zones_by_name, sort_keys=True, default=default))
    zone_id=str(list_hosted_zones_by_name_json["HostedZones"][0]['Id'].replace('/hostedzone/', ''))
    print('UPDATE FOR DOMAIN: '+domain+' ZONE_ID: '+zone_id)

    # Create/update records
    # EU - AF : Africa
    # EU - AN : Antarctica
    # EU - EU : Europe
    # EU - RU : Russia
    # EU - UA : Ukraine
    # AS - AS : Asia
    # OC - OC : Oceania
    # US - NA : North America
    # US - SA : South America
    try:
        update_record_af = r53client.change_resource_record_sets(
            HostedZoneId=zone_id,
            ChangeBatch=update_record('AF', domain)
        )
        update_record_an = r53client.change_resource_record_sets(
            HostedZoneId=zone_id,
            ChangeBatch=update_record('AN', domain)
        )
        update_record_eu = r53client.change_resource_record_sets(
            HostedZoneId=zone_id,
            ChangeBatch=update_record('EU', domain)
        )
        update_record_ru = r53client.change_resource_record_sets(
            HostedZoneId=zone_id,
            ChangeBatch=update_record('RU', domain)
        )
        update_record_ua = r53client.change_resource_record_sets(
            HostedZoneId=zone_id,
            ChangeBatch=update_record('UA', domain)
        )
        update_record_oc = r53client.change_resource_record_sets(
            HostedZoneId=zone_id,
            ChangeBatch=update_record('OC', domain)
        )
        update_record_na = r53client.change_resource_record_sets(
            HostedZoneId=zone_id,
            ChangeBatch=update_record('NA', domain)
        )
        update_record_sa = r53client.change_resource_record_sets(
            HostedZoneId=zone_id,
            ChangeBatch=update_record('SA', domain)
        )
        update_record_as = r53client.change_resource_record_sets(
            HostedZoneId=zone_id,
            ChangeBatch=update_record('AS', domain)
        )
    except r53client.exceptions.InvalidChangeBatch as error:
        print("\tInput ERROR on line {0}. {1} not exist!\n{2}".format(str(counter), domain, str(error)))
