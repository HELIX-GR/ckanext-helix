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

import logging
log1= logging.getLogger(__name__)


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
    log1.debug('Filtered Elements are %s', filtered_fields)
    
    return filtered_fields

def getDataciteDoi(package):
    """Perform HTTP request"""
    
    randomString = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(4)) + '-' \
        +''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(4))
    doi = "10.0351/" + randomString 
    data_string = '''{
            "data": {
                "type": "dois",
                "attributes": {
                    "doi": "''' + doi + '''",
                    "titles": [
                        {
                            "title": "''' + package['title'] +'''"
                        }
                    ],
                    "state": "draft"
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
    response = requests.post('https://api.test.datacite.org/dois', headers=headers, data=data_string, auth=(client_id, password))

    return doi

