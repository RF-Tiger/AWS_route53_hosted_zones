#!/usr/bin/env python3

import sys
import boto3

r53client = boto3.client('route53')

# File format: domain|geo|ip_addr
domain_file = sys.argv[1]


# Make a dict which contains 'domain_name':id to make queries faster
def get_all_zones():
    # Get first 100 zones and next query pointer
    completed_data = {}
    response = r53client.list_hosted_zones()
    for payload in response['HostedZones']:
        completed_data[payload['Name'].rstrip('.')] = payload['Id'].replace('/hostedzone/', '')
    # Main loop to get all another zones data
    while response['IsTruncated']:
        response = r53client.list_hosted_zones(Marker=response.get('NextMarker'))
        for payload in response['HostedZones']:
            completed_data[payload['Name'].rstrip('.')] = payload['Id'].replace('/hostedzone/', '')
    return completed_data


# Def for record create
def update_record(zone, domain, ipaddr):
    if zone == 'RU':
        zone_json = {
            'Comment': 'UPDATE ZONE ' + zone + ' DOMAIN ' + domain + ' IP ' + ipaddr,
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
                                'Value': ipaddr
                            }
                        ]
                    }
                }
            ]
        }
    elif zone == 'UA':
        zone_json = {
            'Comment': 'UPDATE ZONE ' + zone + ' DOMAIN ' + domain + ' IP ' + ipaddr,
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
                                'Value': ipaddr
                            }
                        ]
                    }
                }
            ]
        }
    else:
        zone_json = {
            'Comment': 'UPDATE ZONE ' + zone + ' DOMAIN ' + domain + ' IP ' + ipaddr,
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
                                'Value': ipaddr
                            }
                        ]
                    }
                }
            ]
        }

    return zone_json


# Read domain list and identify zone 'id'
with open(domain_file) as f:
    counter = 0
    cached_zones = get_all_zones()
    # Skip all blank strings and write output to line_file
    lines = (line.rstrip() for line in f)
    line_file = list(line for line in lines if line)
    for linez in line_file:
        counter += 1
        wildcard_flag = False
        domain_data = linez.split("|")
        # Check and apply wildcard option
        if domain_data[0].startswith("*."):
            wildcard_flag = True
            domain_name = domain_data[0].replace('*.', '')
        else:
            domain_name = domain_data[0]
        domain_geo = domain_data[1]
        domain_ip = domain_data[2]
        # Search zone_id by name in cached_zones dict
        for domain in cached_zones.keys():
            if domain_name == domain:
                zone_id = cached_zones[domain]
                print(str(counter) + '. DOMAIN: ' + domain_name + '\t GEO: ' + domain_geo + '\t IP: ' + domain_ip.rstrip())
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

                # Update record section
                if domain_geo == 'EU':
                    update_record_af = r53client.change_resource_record_sets(
                        HostedZoneId=zone_id,
                        ChangeBatch=update_record('AF', domain_name, domain_ip)
                    )
                    update_record_an = r53client.change_resource_record_sets(
                        HostedZoneId=zone_id,
                        ChangeBatch=update_record('AN', domain_name, domain_ip)
                    )
                    update_record_eu = r53client.change_resource_record_sets(
                        HostedZoneId=zone_id,
                        ChangeBatch=update_record('EU', domain_name, domain_ip)
                    )
                    update_record_ru = r53client.change_resource_record_sets(
                        HostedZoneId=zone_id,
                        ChangeBatch=update_record('RU', domain_name, domain_ip)
                    )
                    update_record_ua = r53client.change_resource_record_sets(
                        HostedZoneId=zone_id,
                        ChangeBatch=update_record('UA', domain_name, domain_ip)
                    )
                    if wildcard_flag:
                        update_record_af = r53client.change_resource_record_sets(
                            HostedZoneId=zone_id,
                            ChangeBatch=update_record('AF', f'*.{domain_name}', domain_ip)
                        )
                        update_record_an = r53client.change_resource_record_sets(
                            HostedZoneId=zone_id,
                            ChangeBatch=update_record('AN', f'*.{domain_name}', domain_ip)
                        )
                        update_record_eu = r53client.change_resource_record_sets(
                            HostedZoneId=zone_id,
                            ChangeBatch=update_record('EU', f'*.{domain_name}', domain_ip)
                        )
                        update_record_ru = r53client.change_resource_record_sets(
                            HostedZoneId=zone_id,
                            ChangeBatch=update_record('RU', f'*.{domain_name}', domain_ip)
                        )
                        update_record_ua = r53client.change_resource_record_sets(
                            HostedZoneId=zone_id,
                            ChangeBatch=update_record('UA', f'*.{domain_name}', domain_ip)
                        )

                if domain_geo in 'US':
                    update_record_na = r53client.change_resource_record_sets(
                        HostedZoneId=zone_id,
                        ChangeBatch=update_record('NA', domain_name, domain_ip)
                    )
                    update_record_sa = r53client.change_resource_record_sets(
                        HostedZoneId=zone_id,
                        ChangeBatch=update_record('SA', domain_name, domain_ip)
                    )
                    if wildcard_flag:
                        update_record_na = r53client.change_resource_record_sets(
                            HostedZoneId=zone_id,
                            ChangeBatch=update_record('NA', f'*.{domain_name}', domain_ip)
                        )
                        update_record_sa = r53client.change_resource_record_sets(
                            HostedZoneId=zone_id,
                            ChangeBatch=update_record('SA', f'*.{domain_name}', domain_ip)
                        )
                if domain_geo in 'AS':
                    update_record_as = r53client.change_resource_record_sets(
                        HostedZoneId=zone_id,
                        ChangeBatch=update_record('AS', domain_name, domain_ip)
                    )
                    if wildcard_flag:
                        update_record_as = r53client.change_resource_record_sets(
                            HostedZoneId=zone_id,
                            ChangeBatch=update_record('AS', f'*.{domain_name}', domain_ip)
                        )
                if domain_geo in 'OC':
                    update_record_oc = r53client.change_resource_record_sets(
                        HostedZoneId=zone_id,
                        ChangeBatch=update_record('OC', domain_name, domain_ip)
                    )
                    if wildcard_flag:
                        update_record_oc = r53client.change_resource_record_sets(
                            HostedZoneId=zone_id,
                            ChangeBatch=update_record('OC', f'*.{domain_name}', domain_ip)
                        )
 
