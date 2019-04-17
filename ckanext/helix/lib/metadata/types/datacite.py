import zope.interface

from ckanext.helix.lib.metadata.base import (
    Object, object_null_adapter,
    object_format_adapter, ObjectFormatter)
from ckanext.helix.lib.metadata import xml_serializers 
from ckanext.helix.lib.metadata.schemata import IDataciteMetadata

from . import Metadata, deduce, dataset_type
from ._common import *

import logging
log1=logging.getLogger(__name__)

@dataset_type('datacite')
@object_null_adapter()
@zope.interface.implementer(IDataciteMetadata)
class DataciteMetadata(Metadata):

    ## Factories for fields ## 
    
    title = None
    url = None
    tags = list
    closed_subject = list
    license_id = None
    description = None
    dataset_category = None
    creator = Creator

    ## Deduce methods ##

    @deduce('url')
    def _deduce_url(self): 
        return self.url

    @deduce('notes')
    def _deduce_notes(self): 
        return self.description
    
    @deduce('id')
    def _deduce_id(self): 
        return self.identifier

    @deduce('license_id')
    def _deduce_license(self):
        log1.debug('license is %s',self.license_id)
        return self.license_id

    @deduce('closed_tag')
    def _deduce_closed_subject(self):
        return self.closed_subject    

    @deduce('tags')
    def _deduce_free_tag(self):
        result = []
        for kw in self.free_tags: 
            tag = {'state':'active'}
            tag['name'] = kw
            result.append(tag)
        return result 

@xml_serializers.object_xml_serialize_adapter(IDataciteMetadata)
class DataciteXmlSerializer(xml_serializers.ObjectSerializer):
    pass

@object_format_adapter(IDataciteMetadata)
class DataciteFormatter(ObjectFormatter):
    pass
