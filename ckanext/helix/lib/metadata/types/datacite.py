import zope.interface

from ckanext.helix.lib.metadata.base import (
    Object, object_null_adapter,
    object_format_adapter, ObjectFormatter)
from ckanext.helix.lib.metadata import xml_serializers 
from ckanext.helix.lib.metadata.schemata import IDataciteMetadata

from . import Metadata, deduce, dataset_type
from ._common import *

@dataset_type('datacite')
@object_null_adapter()
@zope.interface.implementer(IDataciteMetadata)
class DataciteMetadata(Metadata):

    ## Factories for fields ## 
    
    title = None
    url = None
    tags = list
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

@xml_serializers.object_xml_serialize_adapter(IDataciteMetadata)
class DataciteXmlSerializer(xml_serializers.ObjectSerializer):
    pass

@object_format_adapter(IDataciteMetadata)
class DataciteFormatter(ObjectFormatter):
    pass
