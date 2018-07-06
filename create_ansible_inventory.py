import boto3
import argparse
import re
from pprint import pprint


parser = argparse.ArgumentParser()
parser.add_argument('--profile', action="store", required=True, help="AWS profile to use")
parser.add_argument('--region', action="store", required=True, help="Region")
parser.add_argument('--tenant', nargs='?', type=str, default="*", help="Tenant/Role")
args = parser.parse_args()

# use whatever profile region you have setup in your config
boto3.setup_default_session(profile_name=args.profile, region_name=args.region)
ec2_client = boto3.client('ec2')

tagvalue = args.tenant

def get_instances_by_customer(ec2_client, tagvalue):
    response = ec2_client.describe_instances(
        Filters=[
            {
                'Name': 'tag-value', 'Values': [tagvalue]
            },
        ]
    )
    return response

response = get_instances_by_customer(ec2_client, tagvalue)


def customer_inventory_file(response, tagvalue):
    cust_hosts = []
    for instance in response['Reservations']:
        instance_state = instance['Instances'][0]['State']
        if instance_state['Code'] == 16:
            for name_tags in instance['Instances']:
                for get_hostname in name_tags['Tags']:
                    if get_hostname['Key'] == 'Name':
                        hostnames = get_hostname['Value']
                        cust_hosts.append(hostnames)
    return cust_hosts




#customer_inventory_file(response, customer)

all_hosts = customer_inventory_file(response, tagvalue)



def write_inventory_file(all_hosts):
    mtas = []
    logags = []
    nats = []
    cmtas = []
    rests = []
    smtps = []
    etls = []
    apps = []
    pps = []
    pp = re.compile('^[a-z]+\.pp\d+v\..')
    app = re.compile('^[a-z]+\.app\d+v\..')
    etl = re.compile('^[a-z]+\.etl\d+v\..')
    rest = re.compile('^[a-z]+\.mta\d+vrest\..')
    smtp = re.compile('^[a-z]+\.mta\d+vsmtp\..')
    cmta = re.compile('^[a-z]+\.mta\d+\..*')
    mta = re.compile('^[a-z]+\.plat\d+\..*')
    old_mta = re.compile('^plat\d+\.*')
    log = re.compile('^[a-z]+\.plat\d+log\..*')
    old_log = re.compile('^logag\d+\.*')
    nat = re.compile('^[^.]+\.(dmz)?nat\d+\..*')
    #for node in all_hosts:
    for plats in all_hosts:
        if mta.match(plats):
            mtas.append(plats)
        elif old_mta.match(plats):
            mtas.append(plats)
   # print(mtas)
    for ags in all_hosts:
        if log.match(ags):
            logags.append(ags)
        elif old_log.match(ags):
            logags.append(ags)
   # print(logags)
    for gats in all_hosts:
        if nat.match(gats):
            nats.append(gats)
   # print(cmtas)
    for cons in all_hosts:
        if cmta.match(cons):
            cmtas.append(cons)
   # print(rests)
    for restnodes in all_hosts:
        if rest.match(restnodes):
            rests.append(restnodes)
   # print(smtps)
    for smtpnodes in all_hosts:
        if smtp.match(smtpnodes):
            smtps.append(smtpnodes)
   # print(etls)
    for etlnodes in all_hosts:
        if etl.match(etlnodes):
            etls.append(etlnodes)
   # print(apps)
    for appnodes in all_hosts:
        if app.match(appnodes):
            apps.append(appnodes)
   # print(pps)
    for ppnodes in all_hosts:
        if pp.match(ppnodes):
            pps.append(ppnodes)
    f = open('inventory', 'w')
    f.write("[{}]".format("mta") + '\n')
    for a in mtas:
        f.write("{:<20}".format(a) + '\n')
    f.write("[{}]".format("logag") + '\n')
    for a in logags:
        f.write("{:<20}".format(a) + '\n')
    f.write("[{}]".format("nat") + '\n')
    for a in nats:
        f.write("{:<20}".format(a) + '\n')
    f.write("[{}]".format("cmta") + '\n')
    for a in cmtas:
        f.write("{:<20}".format(a) + '\n')
    f.write("[{}]".format("rest") + '\n')
    for a in rests:
        f.write("{:<20}".format(a) + '\n')
    f.write("[{}]".format("smtp") + '\n')
    for a in smtps:
        f.write("{:<20}".format(a) + '\n')
    f.write("[{}]".format("etl") + '\n')
    for a in etls:
        f.write("{:<20}".format(a) + '\n')
    f.write("[{}]".format("app") + '\n')
    for a in apps:
        f.write("{:<20}".format(a) + '\n')
    f.write("[{}]".format("pp") + '\n')
    for a in pps:
        f.write("{:<20}".format(a) + '\n')
    f.close()

write_inventory_file(all_hosts)
