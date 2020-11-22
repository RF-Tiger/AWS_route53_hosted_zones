#!/usr/bin/env python3
import requests
import datetime
import boto3
import json
import time
import sys

start_time = time.time()
r53client = boto3.client('route53')

# Constants
_API_KEY = ""
_API_ENDPOINT: str = "https://reg-names.com/api/"
_DOMAIN_FILE = sys.argv[1]


# Reg-names SECTION #
# Reg-Names object for any API request
def request_obj(url: object = None, method: object = None, data: object = None,
                query_params: object = None) -> object:
    default_headers = {
        'accept': 'application/json',
        'X-AUTH-TOKEN': _API_KEY,
        'Content-Type': 'application/json'
    }
    response = requests.request(method, _API_ENDPOINT + url,
                                params=query_params,
                                data=json.dumps(data),
                                headers=default_headers)
    result = json.loads(response.text)
    status_code = response.status_code
    if status_code != 200:
        print(f'\tRequest error:\t{status_code}\t{method}:{url}\n\t{result}')
    else:
        return result


def check_availability(domain_name):
    response = request_obj(url=f'domain/check?domain={domain_name}',
                           method='GET')
    if response['result'][domain_name] == 'available':
        return True
    else:
        return False


def get_user_contact_id():
    response = request_obj(url='contact/', method='GET')
    u_id = response.get('result')[0]
    return u_id.get('id')


def register_new_domain(domain_name, ns1, ns2, ns3, ns4):
    contact = get_user_contact_id()
    payload = {
        'domain': domain_name,
        'years': 1,
        'autoRenew': False,
        'contact': contact,
        'ns1': ns1,
        'ns2': ns2,
        'ns3': ns3,
        'ns4': ns4
    }
    response = request_obj(url=f'domain/', method='POST', data=payload)
    if response['status'] == 'success':
        return True
    else:
        return False


def show_register_status(domain_name):
    response = request_obj(url=f'domain/show?domain={domain_name}', method='GET')
    if response['status'] == 'success':
        return True
    else:
        return False


def update_ns(domain, ns1, ns2, ns3, ns4):
    record = {
        "domain": domain,
        "nameServers": {
            "ns1": ns1,
            "ns2": ns2,
            "ns3": ns3,
            "ns4": ns4
        }
    }
    payload = request_obj(url="name-server", method="POST", data=record)
    return payload


# AWS SECTION #
# Fix datetime for JSON
def default(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()


# Def a model for record create
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


def aws_create_zone(domain_name, ipus, ipeu, ipas, ipoc, wildcard_flag):
    data_for_regnames = {}
    prepare_timestamp = datetime.datetime.timestamp(datetime.datetime.now())
    timestamp = str(prepare_timestamp).replace('.', '')
    domain_zone = r53client.list_hosted_zones_by_name(
        DNSName=domain_name,
        MaxItems='1'
    )
    zone_keys = domain_zone.get('HostedZones')
    zone_name = zone_keys[0].get('Name')[:-1]
    if zone_name == domain_name:
        print(f'{zone_name} already exist!')
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
        zone_ns = create_zone_json["DelegationSet"]["NameServers"]

        # Save dict 'domain-name': 'ns' for reg-names actions
        data_for_regnames[domain_name] = zone_ns
        """{'devtestapi2.io': [
        'ns-272.awsdns-34.com',
        'ns-1301.awsdns-34.org',
        'ns-556.awsdns-05.net', 
        'ns-1574.awsdns-04.co.uk']"""

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
            create_record_af = r53client.change_resource_record_sets(
                HostedZoneId=zone_id,
                ChangeBatch=create_record('AF', domain_name, ipeu)
            )
            create_record_an = r53client.change_resource_record_sets(
                HostedZoneId=zone_id,
                ChangeBatch=create_record('AN', domain_name, ipeu)
            )
            create_record_eu = r53client.change_resource_record_sets(
                HostedZoneId=zone_id,
                ChangeBatch=create_record('EU', domain_name, ipeu)
            )
            create_record_ru = r53client.change_resource_record_sets(
                HostedZoneId=zone_id,
                ChangeBatch=create_record('RU', domain_name, ipeu)
            )
            create_record_ua = r53client.change_resource_record_sets(
                HostedZoneId=zone_id,
                ChangeBatch=create_record('UA', domain_name, ipeu)
            )
            create_record_as = r53client.change_resource_record_sets(
                HostedZoneId=zone_id,
                ChangeBatch=create_record('AS', domain_name, ipas)
            )
            create_record_oc = r53client.change_resource_record_sets(
                HostedZoneId=zone_id,
                ChangeBatch=create_record('OC', domain_name, ipoc)
            )
            create_record_na = r53client.change_resource_record_sets(
                HostedZoneId=zone_id,
                ChangeBatch=create_record('NA', domain_name, ipus)
            )
            create_record_sa = r53client.change_resource_record_sets(
                HostedZoneId=zone_id,
                ChangeBatch=create_record('SA', domain_name, ipus)
            )
            if wildcard_flag:
                # *.example.com wildcard record set
                print(f'Wildcard added for {domain_name}')
                create_record_af = r53client.change_resource_record_sets(
                    HostedZoneId=zone_id,
                    ChangeBatch=create_record('AF', f'*.{domain_name}', ipeu)
                )
                create_record_an = r53client.change_resource_record_sets(
                    HostedZoneId=zone_id,
                    ChangeBatch=create_record('AN', f'*.{domain_name}', ipeu)
                )
                create_record_eu = r53client.change_resource_record_sets(
                    HostedZoneId=zone_id,
                    ChangeBatch=create_record('EU', f'*.{domain_name}', ipeu)
                )
                create_record_ru = r53client.change_resource_record_sets(
                    HostedZoneId=zone_id,
                    ChangeBatch=create_record('RU', f'*.{domain_name}', ipeu)
                )
                create_record_ua = r53client.change_resource_record_sets(
                    HostedZoneId=zone_id,
                    ChangeBatch=create_record('UA', f'*.{domain_name}', ipeu)
                )
                create_record_as = r53client.change_resource_record_sets(
                    HostedZoneId=zone_id,
                    ChangeBatch=create_record('AS', f'*.{domain_name}', ipas)
                )
                create_record_oc = r53client.change_resource_record_sets(
                    HostedZoneId=zone_id,
                    ChangeBatch=create_record('OC', f'*.{domain_name}', ipoc)
                )
                create_record_na = r53client.change_resource_record_sets(
                    HostedZoneId=zone_id,
                    ChangeBatch=create_record('NA', f'*.{domain_name}', ipus)
                )
                create_record_sa = r53client.change_resource_record_sets(
                    HostedZoneId=zone_id,
                    ChangeBatch=create_record('SA', f'*.{domain_name}', ipus)
                )
        except r53client.exceptions.InvalidInput as error:
            print(f'\tRecord Set ERROR on line {str(counter)}\n\t{str(error)}')
        except r53client.exceptions.InvalidChangeBatch as error:
            print(f'\tInput ERROR on line {str(counter)}\t{domain_name}\tSome record has not been set!')
    return data_for_regnames


if __name__ == "__main__":
    reg_check = {}
    with open(_DOMAIN_FILE) as f:
        counter = 0
        # Skip all blank lines and write output to line_file
        lines = (line.rstrip() for line in f)
        line_file = list(line for line in lines if line)
        for data in line_file:
            wildcard_flag = False
            domain_data = data.split("|")
            if len(domain_data) == 5:
                if domain_data[0].startswith("*."):
                    wildcard_flag = True
                    domain_name = domain_data[0].replace('*.', '')
                else:
                    domain_name = domain_data[0]
                ip_us = domain_data[1]
                ip_eu = domain_data[2]
                ip_as = domain_data[3]
                ip_oc = domain_data[4]
                if check_availability(domain_name=domain_name):
                    counter += 1
                    print(f'{domain_name} available, continue...')
                    aws_response = aws_create_zone(domain_name=domain_name,
                                                   ipus=ip_us,
                                                   ipeu=ip_eu,
                                                   ipas=ip_as,
                                                   ipoc=ip_oc,
                                                   wildcard_flag=wildcard_flag
                                                   )
                    reg_check.update(aws_response)
                    register_response = register_new_domain(domain_name=domain_name,
                                                            ns1=aws_response[domain_name][0],
                                                            ns2=aws_response[domain_name][1],
                                                            ns3=aws_response[domain_name][2],
                                                            ns4=aws_response[domain_name][3]
                                                            )
                    if register_response:
                        print(f'Registration for {domain_name} started')
                else:
                    print(f'\t{domain_name} busy, try another name!')
            else:
                print(f'\tFile format ERROR on line {str(counter)} action aborted!')
    f.close()

    # Check registration and fix NS
    ns_flag = True
    ns_counter = 0
    while ns_flag:
        # makes a copy of the key that you can iterate over while modifying the dict
        for domain_name in list(reg_check):
            if show_register_status(domain_name):
                upd_response = update_ns(domain=domain_name,
                                         ns1=reg_check.get(domain_name)[0],
                                         ns2=reg_check.get(domain_name)[1],
                                         ns3=reg_check.get(domain_name)[2],
                                         ns4=reg_check.get(domain_name)[3]
                                         )
                ns_counter += 1
                reg_check.pop(domain_name)
                print(f'{str(ns_counter)}. {domain_name}')
            else:
                print(f'{domain_name} registration pending...')
        # Breaks loop, when ready domains count is equal to  input
        if ns_counter == counter:
            print(f'\tNS change done')
            ns_flag = False
