import sys
from ckanapi import RemoteCKAN

EMAIL_DOMAIN = "athena-innovation.gr"
ORGANIZATION_NAME = 'helix'

# script needs an argumenet with the api key
if len(sys.argv)<3:
    print "Url and api key is required"
    exit
url = sys.argv[1]
api_key = sys.argv[2]
ua = 'ckanapi/1.0 (+' + url + ')'

ckan = RemoteCKAN(url, user_agent=ua, apikey=api_key)
# get members of organization
org = ckan.action.organization_show(id=ORGANIZATION_NAME)
org_members = org["users"]
# get all ckan users
all_users = ckan.action.user_list()
for user in all_users:
    # check if a user of athena is not member of organization
    if user['email'] is not None and user['email'].endswith(EMAIL_DOMAIN) \
        and not[element for element in org_members if element['id'] == user['id']] :
            # we need to add user to the organization
            ckan.action.organization_member_create(id=ORGANIZATION_NAME, username=user['id'], role='member')
            print "Added user", user['name']

