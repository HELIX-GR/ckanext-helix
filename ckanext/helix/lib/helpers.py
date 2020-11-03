# coding: utf8

import ckan.model as model
import ckan.plugins as p
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic
import os
import itertools
from ckan.lib.navl.dictization_functions import Invalid
import textwrap

import xml.etree.ElementTree as etree
import ckanext.helix.reference_data as ext_reference_data 

import urllib2
import json
import requests
import random
import string

from pylons import config

from ckan.lib import base
from ckan.common import c, config, _
import ckan.lib.helpers as h

from ckan.lib.mailer import mail_recipient
from ckan.lib.mailer import MailerException

import datetime
import logging
log= logging.getLogger(__name__)


from ckanext.helix import reference_data


def topicsMatch(subject):

    #open file with ANDS-FOR vocabulary
    closed_subjects = None
    with open(reference_data.get_path('closed-subject.txt')) as f:
        closed_subjects = f.read().splitlines()
    groups = []
    if(type(subject) != list): #if its a single string make it into a list
        subjects = []
        subjects.append(subject)
    else:
        subjects = subject
    #check match for each subject
    for tag in subjects:
        tag = tag.encode('UTF-8')
        for i, line in enumerate(closed_subjects):
            line = str.strip(line)
            if tag == line and i < 164:
                groups.append('physical-chemical-and-mathematical-sciences')
                break
            elif tag == line and i < 294:
                groups.append('environmental-sciences')
                break
            elif tag == line and i < 384:
                groups.append('biological-sciences')
                break
            elif tag == line and i < 459:
                groups.append('agricultural-and-veterinary-sciences')
                break
            elif tag == line and i < 752:
                groups.append('engineering-computing-and-technology')
                break
            elif tag == line and i < 912:
                groups.append('medical-and-health-sciences')
                break
            elif tag == line and i < 1052:
                groups.append('business-economics-and-law')
                break
            elif tag == line:
                groups.append('humanities-and-social-studies')
                break    
                
                    
    # remove duplicates                
    groups = list(set(groups))

    return groups


def min_title_length(value, context):
            '''Check minimun title length'''
            if len(value) < 6:
                raise Invalid("Value must be longer than 6 characters")
            return value
            pass

class CodeBlock():
    def __init__(self, head, block=None):
        self.head = head
        self.block = block
    def __str__(self, indent=""):
        result = indent + self.head + "\n"
        indent += "    "
        if self.block:
            for block in self.block:
                if isinstance(block, CodeBlock):
                    result += block.__str__(indent)
                else:
                    result += indent + block + "\n"
        return result

    def append(self, lines):
        result = self.__str__()
        for line in lines:
            result = result + line + '\n'
        return result


# map fields from xsd to Helix schema
def mapFields():
    with open(ext_reference_data.get_path('mappings.xml')) as f: 
        m = f.read()
            
    root = etree.fromstring(m) 

    filtered_fields = []
        
    for element in root.iter():
        if element.tag != 'map' and 'mapping' not in element.attrib:
            filtered_fields.append(element.attrib['name'])
    log.debug('Filtered Elements are %s', filtered_fields)
    
    return filtered_fields

def getDataciteDoi(package):
    """Perform HTTP request"""

    package_url = config.get('ckan.site_url') + h.url_for(controller='package', action='read',
                                id=package['name'])
    random_str = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(4)) + '-' \
        +''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(4))
    doi = config.get('ckanext.helix.datacite.prefix') + random_str
    event = config.get('ckanext.helix.datacite.publish')
    #format name for datacite (first name, given name)
    creator_name = package['datacite.creator.creator_name'].replace(" ", ", ", 1)
    if 'datacite.publication_year' in package:
        publication_year =  package['datacite.publication_year'] 
    else:
        publication_year =  datetime.date.today().year
    publisher = package['organization']['name']
    data_string = '''{
            "data": {
                "type": "dois",
                "attributes": {
                    "event":  "''' + event + '''",
                    "doi": "''' + doi + '''",
                    "url": "''' + package_url + '''",
                    "titles": [
                        {
                            "title": "''' + package['title'] +'''"
                        }
                    ],
                    "creators": [
                    {
                        "name": "''' + creator_name + '''",
                        "nameType": "Personal",
                        "affiliation": [],
                        "nameIdentifiers": []
                    }],
                    "publisher": "''' + publisher +'''",
                    "publicationYear":"''' + str(publication_year) + '''",
                    "types": {
                        "resourceTypeGeneral": "Dataset"
                    }
                }
            }
        }'''
    headers = {
        'Accept': 'application/vnd.api+json',
        'Content-Type': 'application/vnd.api+json',
    }
    
    datacite_url = config.get('ckanext.helix.datacite.api_url')
    client_id = config.get('ckanext.helix.datacite.client_id')
    password = config.get('ckanext.helix.datacite.password')
    try:
        response = requests.post(datacite_url, headers=headers, data=data_string, auth=(client_id, password))
        #return auto-generated doi
        result = json.loads(response.text)
        #doi = result['data']['id']
    except Exception as ex:
       log.debug('Datacite request failed: %s', ex)
    log.debug('Registered doi is %s', doi)
    return doi

def get_org_licenses(org_name):

    default_licenses =  base.model.Package.get_license_options()
    file_name = reference_data.get_path('licenses_' + org_name + '.json')
    if os.path.isfile(file_name):
        with open(file_name) as f:
            data = json.load(f)
            licenses = []
            for license in data:
                license_tuple = (license['title'], license['id'])
                licenses.append(license_tuple)        
    else: 
        return default_licenses

    return licenses

def get_user_list():
    
    context = {'model': model, 'session': model.Session, 'ignore_auth': True}
    users = logic.get_action('user_list')(context, {})    
    return users

def notify_admins(pkg):
    admins = []
    context_copy = {'model': model, 'session': model.Session,
                    'user': c.user or c.author, 'auth_user_obj': c.userobj, 'ignore_auth': True}

    organization = logic.get_action('organization_show')(
        context_copy, {'id': pkg['organization']['id'], 'include_users': True})
    for user in organization['users']:
        if user['capacity'] == 'admin':
            admins.append(user['name'])
    extra_vars = {'dataset_url': config.get('ckan.site_url') + '/dataset/' + pkg['id'],
                  'site_title': config.get('ckan.site_title'),
                  'site_url': config.get('ckan.site_url'),
                  'organization_name': organization.get('name'),
                  'organization_edit_url': config.get('ckan.site_url') + '/organization/bulk_process/' + organization.get('id'),
                  'dataset_title': pkg['title']}
    body = base.render_jinja2(
        'emails/new_dataset_text.txt', extra_vars)
    subject = _('Νέο σύνολο δεδομένων {0}').format(pkg['title'])
    for admin in admins:
        try:
            mail_recipient("user", admin,
                           subject, body)
        except MailerException:
            success = False
            # return 'Error sending e-mail'


def notify_users(datasets):
    context_copy = {'model': model, 'session': model.Session,
                    'user': c.user or c.author, 'auth_user_obj': c.userobj, 'ignore_auth': True}
    for id in datasets:
        dataset = logic.get_action('package_show')(context_copy, {'id': id})
        user = logic.get_action('user_show')(
            context_copy, {'id': dataset['creator_user_id']})
        extra_vars = {'dataset_url': config.get('ckan.site_url') + '/dataset/' + id,
                      'site_title': config.get('ckan.site_title'),
                      'site_url': config.get('ckan.site_url'),
                      'dataset_title': dataset.get('title')}
        body = base.render_jinja2(
            'emails/dataset_accepted_text.txt', extra_vars)
        subject =_('Αποδοχή συνόλου δεδομένων {0}').format(dataset.get('title'))
        try:
            mail_recipient("user", user['name'],
                           subject, body)
        except MailerException:
            success = False
            # return 'Error sending e-mail'
    return
