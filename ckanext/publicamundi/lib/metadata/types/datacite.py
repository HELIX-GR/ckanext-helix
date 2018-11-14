import zope.interface

from ckanext.publicamundi.lib.metadata.base import (
    Object, object_null_adapter,
    object_format_adapter, ObjectFormatter)
from ckanext.publicamundi.lib.metadata import xml_serializers 
from ckanext.publicamundi.lib.metadata.schemata import IDataciteMetadata

from . import Metadata, deduce, dataset_type
from ._common import *

@dataset_type('datacite')
@object_null_adapter()
@zope.interface.implementer(IDataciteMetadata)
class DataciteMetadata(Metadata):

    ## Factories for fields ## 
    
    title = None
    url = None
    thematic_category = None
    tags = list
    subject_closed = list
    contact_info = ContactInfo
    contacts = dict
    geometry = list
    rating = None
    grade = None
    description = None
    temporal_extent = None
    reviewed = None
    created = None
    published = None
    password = None
    funder = None
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

@xml_serializers.object_xml_serialize_adapter(IDataciteMetadata)
class DataciteXmlSerializer(xml_serializers.ObjectSerializer):
    pass

@object_format_adapter(IDataciteMetadata)
class DataciteFormatter(ObjectFormatter):
    pass
