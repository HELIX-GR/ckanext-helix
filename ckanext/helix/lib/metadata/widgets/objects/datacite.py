import zope.interface
from collections import OrderedDict

from ckanext.helix.lib.metadata import schemata
from ckanext.helix.lib.metadata.fields import *
from ckanext.helix.lib.metadata.widgets import (
    object_widget_adapter, field_widget_adapter, field_widget_multiadapter)
from  ckanext.helix.lib.metadata.widgets.base import (
    EditFieldWidget, EditObjectWidget, 
    ReadFieldWidget, ReadObjectWidget,
    ListFieldWidgetTraits, DictFieldWidgetTraits)

import logging
log1 = logging.getLogger(__name__)  

from . import _common

@field_widget_multiadapter([IListField, schemata.IDate],
    qualifiers=['date.datacite'], is_fallback=False)
class DateEditWidget(EditFieldWidget, ListFieldWidgetTraits):
 
    def get_item_qualifier(self):
        return 'item'
    
    def get_template(self):
        return 'package/snippets/fields/edit-list-date-datacite.html'

@field_widget_multiadapter([IListField, schemata.IContributor],
    qualifiers=['contributor.datacite'], is_fallback=False)
class ContributorEditWidget(EditFieldWidget, ListFieldWidgetTraits):
 
    def get_item_qualifier(self):
        return 'item'
    
    def get_template(self):
        return 'package/snippets/fields/edit-list-contributor-datacite.html'




@field_widget_multiadapter([IListField, ITextLineField], qualifiers=['tags.datacite'])
class TagsEditWidget(EditFieldWidget):

    def __init__(self, field, *args):
        assert isinstance(field, zope.schema.List)
        EditFieldWidget.__init__(self, field)

    def get_template(self):
        return 'package/snippets/fields/edit-list-tags-datacite.html'

@field_widget_multiadapter([IListField, ITextLineField], qualifiers=['tags.datacite'])
class TagsReadWidget(ReadFieldWidget):

    def __init__(self, field, *args):
        assert isinstance(field, zope.schema.List)
        ReadFieldWidget.__init__(self, field)

    def get_template(self):
        return 'package/snippets/fields/read-list-tags-datacite.html'

@field_widget_multiadapter([IDictField, schemata.IContactInfo],
    qualifiers=['contacts.datacite'], is_fallback=True)
class DictOfContactsEditWidget(EditFieldWidget, DictFieldWidgetTraits):
 
    def get_template(self):
        return 'package/snippets/fields/edit-dict-contacts-datacite.html'

@object_widget_adapter(schemata.IDataciteMetadata, qualifiers=['datasetform'], is_fallback=True)
class DataciteEditWidget(EditObjectWidget):
    
    def prepare_template_vars(self, name_prefix, data):
        tpl_vars = super(DataciteEditWidget, self).prepare_template_vars(name_prefix, data)
        # Add variables
        return tpl_vars
   
    def get_field_template_vars(self):
        return {
            'url': {
                'title': ('Web Site'),
            },
        }
    
    def get_field_qualifiers(self):

        qualifiers = super(DataciteEditWidget, self).get_field_qualifiers()      
        qualifiers.update({
            'tags': 'tags'
        })
        
        return qualifiers
    
    def get_glue_template(self):
        return 'package/snippets/objects/glue-edit-datacite-datasetform.html'
        
    def get_template(self):
        return None # use glue template

@object_widget_adapter(schemata.IDataciteMetadata)
class DataciteReadWidget(ReadObjectWidget):
    
    def prepare_template_vars(self, name_prefix, data):
        tpl_vars = super(DataciteReadWidget, self).prepare_template_vars(name_prefix, data)
        # Add variables
        return tpl_vars
   
    def get_field_qualifiers(self):
        
        qualifiers = super(DataciteReadWidget, self).get_field_qualifiers()
        qualifiers['tags'] = 'tags.datacite'
        qualifiers['creator'] = 'creator.datacite'
        
        return qualifiers
    
    def get_glue_template(self):
        return 'package/snippets/objects/glue-read-datacite.html'

    def get_template(self):
        return None # use glue template

@object_widget_adapter(schemata.IDataciteMetadata, qualifiers=['table'])
class TableReadWidget(_common.TableReadWidget):

    def get_field_order(self):
        return [
           'title',
           'optional_title',
           'optional_description',
           'contact_email',
           'closed_subject',
           'creator',
           'publication_year',
           'public_doi',
           'related_publication',
           'is_derived_from',
           'is_similar_to',
           'languagecode'
        ]

    

    def get_field_qualifiers(self):
        return OrderedDict([
            ('creator', 'creator.datacite')
        ])

