#!/usr/bin/env python3

import sys
import boto3
import botocore
import json
import datetime

r53client = boto3.client('route53')

# File format: domain|us_ip|eu_ip|as_ip|oc_ip
domain_file = sys.argv[1]


# Fix datetime for JSON
def default(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()


# Def for record create
def create_record(zone, domain, ipaddr):
    if zone == 'RU':
        zone_json = {
            'Comment': 'CREATE ZONE ' + zone + ' DOMAIN ' + domain + ' IP ' + ipaddr,
            'Changes': [
                {
                    'Action': 'CREATE',
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
            'Comment': 'CREATE ZONE ' + zone + ' DOMAIN ' + domain + ' IP ' + ipaddr,
            'Changes': [
                {
                    'Action': 'CREATE',
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
            'Comment': 'CREATE ZONE ' + zone + ' DOMAIN ' + domain + ' IP ' + ipaddr,
            'Changes': [
                {
                    'Action': 'CREATE',
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


# Read domain list
with open(domain_file) as f:
    counter = 0
    # Skip all blank strings and write output to line_file
    lines = (line.rstrip() for line in f)
    line_file = list(line for line in lines if line)
    for linez in line_file:
        counter += 1
        wildcard_flag = False
        domain_data = linez.split("|")
        if domain_data[0].startswith("*."):
            wildcard_flag = True
            domain_name = domain_data[0].replace('*.', '')
        else:
            domain_name = domain_data[0]
        domain_ip_US = domain_data[1]
        domain_ip_EU = domain_data[2]
        domain_ip_AS = domain_data[3]
        domain_ip_OC = domain_data[4]

        # Check and apply wildcard option

        if len(domain_data) == 5:
            prepare_timestamp = datetime.datetime.timestamp(datetime.datetime.now())
            timestamp = str(prepare_timestamp).replace('.', '')
            domain_zone = r53client.list_hosted_zones_by_name(
                DNSName=domain_name,
                MaxItems='1'
            )
            zone_keys = domain_zone.get('HostedZones')
            zone_name = zone_keys[0].get('Name')[:-1]
            if zone_name == domain_name:
                print("{} already exist!".format(zone_name))
            else:
                # Create zone
                create_zone = r53client.create_hosted_zone(
                    Name=domain_name,
                    CallerReference=timestamp,
                    HostedZoneConfig={
                        'PrivateZone': False
                    }
                )
                # Read JSON after create
                create_zone_json = json.loads(json.dumps(create_zone, sort_keys=True, default=default))
                zone_id = str(create_zone_json["HostedZone"]["Id"].replace('/hostedzone/', ''))
                # zone_ns=str(create_zone_json["DelegationSet"]["NameServers"])
                zone_ns = create_zone_json["DelegationSet"]["NameServers"]
                # print('DOMAIN: '+domain_ip[0]+' NS: '+zone_ns)
                print(domain_name + ' ' + ' '.join([str(ns) for ns in zone_ns]))

                # Create/update records
                # EU - AF : Africa
                # EU - AN : Antarctica
                # EU - RU : Russia
                # EU - UA : Ukraine
                # EU - EU : Europe
                # AS - AS : Asia
                # OC - OC : Oceania
                # US - NA : North America
                # US - SA : South America
                try:
                    ### example.com record set
                    create_record_af = r53client.change_resource_record_sets(
                        HostedZoneId=zone_id,
                        ChangeBatch=create_record('AF', domain_name, domain_ip_EU)
                    )
                    create_record_an = r53client.change_resource_record_sets(
                        HostedZoneId=zone_id,
                        ChangeBatch=create_record('AN', domain_name, domain_ip_EU)
                    )
                    create_record_eu = r53client.change_resource_record_sets(
                        HostedZoneId=zone_id,
                        ChangeBatch=create_record('EU', domain_name, domain_ip_EU)
                    )
                    create_record_ru = r53client.change_resource_record_sets(
                        HostedZoneId=zone_id,
                        ChangeBatch=create_record('RU', domain_name, domain_ip_EU)
                    )
                    create_record_ua = r53client.change_resource_record_sets(
                        HostedZoneId=zone_id,
                        ChangeBatch=create_record('UA', domain_name, domain_ip_EU)
                    )
                    create_record_as = r53client.change_resource_record_sets(
                        HostedZoneId=zone_id,
                        ChangeBatch=create_record('AS', domain_name, domain_ip_AS)
                    )
                    create_record_oc = r53client.change_resource_record_sets(
                        HostedZoneId=zone_id,
                        ChangeBatch=create_record('OC', domain_name, domain_ip_OC)
                    )
                    create_record_na = r53client.change_resource_record_sets(
                        HostedZoneId=zone_id,
                        ChangeBatch=create_record('NA', domain_name, domain_ip_US)
                    )
                    create_record_sa = r53client.change_resource_record_sets(
                        HostedZoneId=zone_id,
                        ChangeBatch=create_record('SA', domain_name, domain_ip_US)
                    )
                    if wildcard_flag:
                        # *.example.com wildcard record set
                        print(f'Wildcard added for {domain_name}')
                        create_record_af = r53client.change_resource_record_sets(
                            HostedZoneId=zone_id,
                            ChangeBatch=create_record('AF', f'*.{domain_name}', domain_ip_EU)
                        )
                        create_record_an = r53client.change_resource_record_sets(
                            HostedZoneId=zone_id,
                            ChangeBatch=create_record('AN', f'*.{domain_name}', domain_ip_EU)
                        )
                        create_record_eu = r53client.change_resource_record_sets(
                            HostedZoneId=zone_id,
                            ChangeBatch=create_record('EU', f'*.{domain_name}', domain_ip_EU)
                        )
                        create_record_ru = r53client.change_resource_record_sets(
                            HostedZoneId=zone_id,
                            ChangeBatch=create_record('RU', f'*.{domain_name}', domain_ip_EU)
                        )
                        create_record_ua = r53client.change_resource_record_sets(
                            HostedZoneId=zone_id,
                            ChangeBatch=create_record('UA', f'*.{domain_name}', domain_ip_EU)
                        )
                        create_record_as = r53client.change_resource_record_sets(
                            HostedZoneId=zone_id,
                            ChangeBatch=create_record('AS', f'*.{domain_name}', domain_ip_AS)
                        )
                        create_record_oc = r53client.change_resource_record_sets(
                            HostedZoneId=zone_id,
                            ChangeBatch=create_record('OC', f'*.{domain_name}', domain_ip_OC)
                        )
                        create_record_na = r53client.change_resource_record_sets(
                            HostedZoneId=zone_id,
                            ChangeBatch=create_record('NA', f'*.{domain_name}', domain_ip_US)
                        )
                        create_record_sa = r53client.change_resource_record_sets(
                            HostedZoneId=zone_id,
                            ChangeBatch=create_record('SA', f'*.{domain_name}', domain_ip_US)
                        )
                except r53client.exceptions.InvalidInput as error:
                    print("\tRecord Set ERROR on line " + str(counter) + '\n' + str(error))
                except r53client.exceptions.InvalidChangeBatch as error:
                    print("\tInput ERROR on line {0}\t{1}\tSome record's has not been set!".format(str(counter),
                                                                                                   domain_ip[0]))
        else:
            print("\tFile format ERROR on line {} \tAction aborted!".format(counter))

