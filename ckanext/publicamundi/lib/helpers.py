import ckan.model as model
import ckan.plugins as p
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic
import os
import itertools

import logging
log1= logging.getLogger(__name__)

def topicsMatch(subject):
    #log1.debug('\n Subjects are %s, type is %s\n', subject, type(subject))

    absolute_path = os.path.dirname(os.path.abspath(__file__))
    #my_map = map(str.strip, open(absolute_path + '/closed-tags.txt')))
    with open(absolute_path + '/closed-tags.txt') as f:
        my_list = f.read().splitlines()
    groups = []
    #check match for each subject
    for tag in subject:
        tag = tag.encode('UTF-8')
        for i, line in enumerate(my_list):
            line = str.strip(line)
            #log1.debug('tag is %s, type is %s line is %s, type is %s', tag, type(tag), line, type(line))
            if tag == line and i < 139:
                groups.append('physical-chemical-and-mathematical-sciences')
                break
            elif tag == line and i < 262:
                groups.append('environmental-sciences')
                break
            elif tag == line and i < 352:
                groups.append('biology-sciences')
                break
            elif tag == line and i < 424:
                groups.append('agricultural-and-veterinary-sciences')
                break
            elif tag == line and i < 652:
                groups.append('engineering-computing-and-technology')
                break
            elif tag == line and i < 809:
                groups.append('medical-and-health-sciences')
                break
            elif tag == line and i < 1012:
                groups.append('business-economics-and-law')
                break
            elif tag == line:
                groups.append('humanities-and-social-studies')
                break    
                
                    
    # remove duplicates                
    groups = list(set(groups))
    log1.debug('\n groups are %s \n', groups)
    
      
    return groups


