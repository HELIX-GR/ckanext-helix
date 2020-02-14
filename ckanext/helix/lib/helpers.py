import ckan.model as model
import ckan.plugins as p
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic
import os
import itertools
from ckan.lib.navl.dictization_functions import Invalid
import textwrap

import json
import requests
import random
import string

from pylons import config

from ckan.lib import base
import ckan.lib.helpers as h
from ckan.common import c
from ckanext.helix import reference_data

import datetime
import logging
log = logging.getLogger(__name__)

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

def getDataciteDoi(package):
    """Perform HTTP request"""
    package_url = config.get('ckan.site_url') + h.url_for(controller='package', action='read',
                                id=package['name'])
    prefix = config.get('ckanext.helix.datacite.prefix')
    event = config.get('ckanext.helix.datacite.publish')
    #format name for datacite (first name, given name)
    creator_name = package['datacite.creator.creator_name'].replace(" ", ", ", 1)
    publication_year =  datetime.date.today().year
    publisher = package['organization']['name']
    data_string = '''{
            "data": {
                "type": "dois",
                "attributes": {
                    "event":  "''' + event + '''",
                    "prefix": "''' + prefix + '''",
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
                    "publisher": "''' + publisher + '''",
                    "publicationYear": "''' + str(publication_year) + '''" ,
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
        doi = result['data']['id']
    except Exception as ex:
       log.debug('Datacite request failed: %s', ex)
    log.debug('Registered doi is %s', doi)
    return doi