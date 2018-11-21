import ckan.model as model
import ckan.plugins as p
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic
import os
import itertools

import logging
log1= logging.getLogger(__name__)

def topicsMatch(subject):

    absolute_path = os.path.dirname(os.path.abspath(__file__))
    #my_map = map(str.strip, open(absolute_path + '/closed-tags.txt')))
    #open file with ANDS-FOR vocabulary
    with open(absolute_path + '/closed-tags.txt') as f:
        my_list = f.read().splitlines()
    groups = []
    if(type(subject) != list): #if its a single string make it into a list
        subjects = []
        subjects.append(subject)
    else:
        subjects = subject
    #check match for each subject
    for tag in subjects:
        tag = tag.encode('UTF-8')
        for i, line in enumerate(my_list):
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
            elif tag == line and i < 1012:
                groups.append('business-economics-and-law')
                break
            elif tag == line:
                groups.append('humanities-and-social-studies')
                break    
                
                    
    # remove duplicates                
    groups = list(set(groups))

    return groups


