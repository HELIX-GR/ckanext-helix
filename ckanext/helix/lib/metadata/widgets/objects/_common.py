import itertools
import zope.interface
from collections import OrderedDict
from operator import itemgetter, attrgetter

from ckanext.helix.lib import toolkit
from ckanext.helix.lib.metadata.fields import *
from ckanext.helix.lib.metadata import schemata
from ckanext.helix.lib.metadata.widgets import (
    object_widget_adapter, field_widget_adapter, field_widget_multiadapter)
from ckanext.helix.lib.metadata.widgets.base import (
    ReadObjectWidget, EditObjectWidget, ReadFieldWidget, EditFieldWidget,
    ListFieldWidgetTraits, DictFieldWidgetTraits)

_ = toolkit._ 

import logging
log1 = logging.getLogger(__name__) 

#
# IObject - table/dl views
#

@object_widget_adapter(schemata.IObject, qualifiers=['table'])
class TableReadWidget(ReadObjectWidget):

    max_depth = 2
    
    markup_qualifier = 'td'

    def get_template(self):
        return 'package/snippets/objects/read-object-table.html'
    
    def get_field_order(self):
        '''Explicitly define the order at which fields are listed in rows
        ''' 
        cls = TableReadWidget
        return super(cls, self).get_field_qualifiers().keys()

    def prepare_template_vars(self, name_prefix, data):
        
        cls = TableReadWidget
        Td, Th, Tr = cls._Td, cls._Th, cls._Tr
        
        tpl_vars = super(cls, self).prepare_template_vars(name_prefix, data)
        # Dictize self.obj, format leafs as markup

        dictz_opts = {
            'max-depth': data.get('max_depth', 0) or self.max_depth, 
            'format-values': 'markup:q=%s' % (self.markup_qualifier)
        }
        obj_dict = self.obj.to_dict(flat=False, opts=dictz_opts)
        
        # Re-order according to this widget's field ordering
        
        od = OrderedDict((
            (k, obj_dict[k]) for k in self.get_field_order()
        ))
        

        # Preprocess ordered obj_dict to be displayed as table rows
                
        num_rows, num_cols, rows = cls._tabulate(od)
       
        # Scan TH elements and 
        #  * provide human-friendly titles
        #  * assign qnames (qualified names) for fields
        
        for row in rows:
            for th in filter(lambda t: t.tag == 'th', row):
                kp = th.key_path()
                field = self.obj.get_field(kp)
                th.title = _(field.context.title) or _(field.title)
                th.qname = '.'.join(map(str, (name_prefix,) + kp))
        
        # Prepend extra rows if needed
        
        extras = filter(itemgetter('value'), data.get('extras', []))
        for r in reversed(extras):
            th = Th(r['key'], title=r.get('title'))
            td = Td(r['value'], colspan=(num_cols - 1), attrs=r.get('attrs'))
            row = Tr([th, td])
            row.display = True
            rows.insert(0, row)
        
        # Provide vars to template

        tpl_vars.update({
            'rows': rows,
            'num_rows': num_rows,
            'num_cols': num_cols,
        })
        
        return tpl_vars

    # Helpers

    class _Tr(list):

        __slots__ = ('attrs', 'display')
    
    class _Td(object):

        __slots__ = ('parent', 'data', 'rowspan', 'colspan', 'attrs')

        tag = 'td'
        
        def  __init__(self, data, rowspan=1, colspan=1, attrs=None):
            self.data = data
            self.rowspan = rowspan
            self.colspan = colspan
            self.attrs = attrs 
            self.parent = None

        def __repr__(self):
            return '%s(data=%r, rowspan=%s, colspan=%s)' % (
                self.tag.upper(), 
                self.data, self.rowspan, self.colspan)
        
    class _Th(_Td):
        
        __slots__ = ('title', 'qname')

        tag = 'th'
        
        def  __init__(self, data, title=None, rowspan=1, colspan=1, attrs=None):
            super(type(self), self).__init__(data, rowspan, colspan, attrs)
            self.title = title or self.data
            self.qname = self.data

        def key(self):
            return self.data
        
        def key_path(self):
            p = self
            path = [p.data]
            while p.parent:
                path.insert(0, p.parent.data)
                p = p.parent
            return tuple(path)
       
    @classmethod
    def _tabulate(cls, d):
        
        rows = cls._tabulate_rows(d)
        num_rows = len(rows)
        num_cols = max(map(len, rows)) if rows else 2

        for row in rows:
            row[-1].colspan += num_cols - len(row)
        
        return num_rows, num_cols, rows
    
    @classmethod 
    def _tabulate_rows(cls, x):
        
        Td, Th, Tr = cls._Td, cls._Th, cls._Tr
        
        itr = None
        if isinstance(x, dict):
            itr = x.iteritems()
        elif isinstance(x, list):
            itr = enumerate(x)
        
        res = list()
        if itr:
            for key, val in itr:
                rows = cls._tabulate_rows(val)
                nr = len(rows)
                if rows:
                    parent = Th(data=key, rowspan=nr, colspan=1)
                    # Prepend row grouper to 1st row
                    rows[0].insert(0, parent)
                    rows[0][1].parent = parent
                    # Update all successive (#>1) rows
                    for i in range(1, nr):
                        row = rows[i]
                        if not row[0].parent: 
                            row[0].parent = parent
                        row[-1].colspan -= 1
                    res.extend(rows)
        else:
            if x:
                row = Tr([Td(data=unicode(x), colspan=1)])
                row.display = False
                res.append(row)
        
        return res

@object_widget_adapter(schemata.IObject, qualifiers=['dl'])
class DlObjectReadWidget(ReadObjectWidget):
    
    def get_field_qualifiers(self):
        qualifiers = super(DlObjectReadWidget, self).get_field_qualifiers()
        for key in qualifiers:
            qualifiers[key] = 'dd'
        return qualifiers

    def get_glue_template(self):
        return 'package/snippets/objects/glue-read-object-dl.html'

@object_widget_adapter(schemata.IObject, qualifiers=['td'])
class TdObjectReadWidget(ReadObjectWidget):
    
    def get_field_qualifiers(self):
        qualifiers = super(TdObjectReadWidget, self).get_field_qualifiers()
        for key in qualifiers:
            qualifiers[key] = 'dd'
        return qualifiers

    def get_glue_template(self):
        return 'package/snippets/objects/glue-read-object-td.html'

@field_widget_adapter(IStringField, qualifiers=['dd', 'td'])
@field_widget_adapter(IStringLineField, qualifiers=['dd', 'td'])
@field_widget_adapter(ITextField, qualifiers=['dd', 'td'])
@field_widget_adapter(ITextLineField, qualifiers=['dd', 'td'])
class DataTextReadWidget(ReadFieldWidget):
    
    def get_template(self):
        return 'package/snippets/fields/read-text-dd.html'

@field_widget_adapter(ITextLineField, qualifiers=['dd.email', 'td.email'])
@field_widget_adapter(IEmailAddressField, qualifiers=['dd', 'td'])
class DataEmailReadWidget(ReadFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/read-email-dd.html'

@field_widget_adapter(IURIField, qualifiers=['dd', 'td'])
class DataUriReadWidget(ReadFieldWidget):
    
    def get_template(self):
        return 'package/snippets/fields/read-uri-dd.html'

@field_widget_adapter(IDateField, qualifiers=['dd', 'td'])
@field_widget_adapter(IDatetimeField, qualifiers=['dd', 'td'])
@field_widget_adapter(ITimeField, qualifiers=['dd', 'td'])
@field_widget_adapter(ITimedeltaField, qualifiers=['dd', 'td'])
class DataDatetimeReadWidget(ReadFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/read-datetime-dd.html'

@field_widget_adapter(IIntField, qualifiers=['dd', 'td'])
class DataIntReadWidget(ReadFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/read-int-dd.html'

@field_widget_adapter(IFloatField, qualifiers=['dd', 'td'])
class DataFloatReadWidget(ReadFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/read-float-dd.html'

@field_widget_adapter(IBoolField, qualifiers=['dd', 'td'])
class DataBoolReadWidget(ReadFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/read-bool-dd.html'

@field_widget_adapter(IChoiceField, qualifiers=['dd', 'td'])
class DataChoiceReadWidget(ReadFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/read-choice-dd.html'

@field_widget_multiadapter([IListField, IChoiceField], qualifiers=['td'])
class TdChoicesReadWidget(ReadFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/read-list-choice-td.html'

#
# IPoint
#

@object_widget_adapter(schemata.IPoint)
class PointEditWidget(EditObjectWidget):

    def get_template(self):
        return 'package/snippets/objects/edit-point.html'

@object_widget_adapter(schemata.IPoint)
class PointReadWidget(ReadObjectWidget):

    def get_template(self):
        return 'package/snippets/objects/read-point.html'

#
# ITemporalExtent
#

@object_widget_adapter(schemata.ITemporalExtent)
class TemporalExtentEditWidget(EditObjectWidget):

    def get_template(self):
        return 'package/snippets/objects/edit-temporal_extent.html'

@object_widget_adapter(schemata.ITemporalExtent, qualifiers=['item'])
class TemporalExtentAsItemEditWidget(EditObjectWidget):

    def get_template(self):
        return 'package/snippets/objects/edit-temporal_extent-item.html'

@object_widget_adapter(schemata.ITemporalExtent)
class TemporalExtentReadWidget(ReadObjectWidget):

    def get_template(self):
        return 'package/snippets/objects/read-temporal_extent.html'

@object_widget_adapter(schemata.ITemporalExtent, qualifiers=['td'])
class TdTemporalExtentReadWidget(ReadObjectWidget):

    def get_template(self):
        return 'package/snippets/objects/read-temporal_extent-td.html'

#
# IPostalAddress
#

@object_widget_adapter(schemata.IPostalAddress)
class PostalAddressEditWidget(EditObjectWidget):

    def get_template(self):
        return 'package/snippets/objects/edit-postal_address.html'

@object_widget_adapter(schemata.IPostalAddress, qualifiers=['compact'])
class PostalAddressCompactEditWidget(EditObjectWidget):

    def get_template(self):
        return 'package/snippets/objects/edit-postal_address-compact.html'

@object_widget_adapter(schemata.IPostalAddress, qualifiers=['comfortable'])
class PostalAddressComfortableEditWidget(EditObjectWidget):

    def get_template(self):
        return 'package/snippets/objects/edit-postal_address-comfortable.html'

@object_widget_adapter(schemata.IPostalAddress)
class PostalAddressReadWidget(ReadObjectWidget):

    def get_template(self):
        return 'package/snippets/objects/read-postal_address.html'

#
# IContactInfo
#

@object_widget_adapter(schemata.IContactInfo)
class ContactInfoEditWidget(EditObjectWidget):

    def get_field_qualifiers(self):
        return OrderedDict([
            ('email', 'email'),
            ('address', 'compact'),
            ('publish', None),
        ])
        
    def get_template(self):
        return None # use default glue template
        #return 'package/snippets/objects/edit-contact_info.html'

@object_widget_adapter(schemata.IContactInfo)
class ContactInfoReadWidget(ReadObjectWidget):
    
    def get_field_qualifiers(self):
        return OrderedDict([
            ('publish', None),
            ('email', 'email'),
            ('address', None),
        ])

    def get_template(self):
        return None # use glue template
        #return 'package/snippets/objects/read-contact_info.html'

#
# IResponsibleParty
#

@object_widget_adapter(schemata.IResponsibleParty)
class ResponsiblePartyEditWidget(EditObjectWidget):

    def get_field_template_vars(self):
        return {
            'role': {
                'title': _('Party Role'),
                'input_classes': ['span3'],
            },
            'organization': {
                'title': _('Organization Name'),
                'placeholder': u'Acme Widgits',
                'input_classes': ['span4'],
            },
            'email': {
                'placeholder': 'info@example.com',
                'input_classes': ['span3'],
            },
        }
    
    def get_field_qualifiers(self):
        return OrderedDict([
            ('organization', None),
            ('email', None),
            ('role', 'select2'),
        ])
        
    def get_template(self):
        return None 

@object_widget_adapter(schemata.IResponsibleParty)
class ResponsiblePartyReadWidget(ReadObjectWidget):

    def get_template(self):
        return None 

#
# IThesaurusTerms
#

@object_widget_adapter(schemata.IThesaurusTerms, 
    qualifiers=['select'], is_fallback=True)
class ThesaurusTermsEditWidget(EditObjectWidget):
        
    def get_template(self):
        return 'package/snippets/objects/edit-thesaurus_terms-select.html' 

@object_widget_adapter(schemata.IThesaurusTerms, 
    qualifiers=['select2'], is_fallback=False)
class ThesaurusTermsS2EditWidget(EditObjectWidget):
        
    def get_template(self):
        return 'package/snippets/objects/edit-thesaurus_terms-select2.html' 

@object_widget_adapter(schemata.IThesaurusTerms)
class ThesaurusTermsReadWidget(ReadObjectWidget):
    
    def get_template(self):
        return 'package/snippets/objects/read-thesaurus_terms.html' 

@object_widget_adapter(schemata.IThesaurusTerms, qualifiers=['td'])
class TdThesaurusTermsReadWidget(ReadObjectWidget):
    
    def get_template(self):
        return 'package/snippets/objects/read-thesaurus_terms-td.html' 

@field_widget_multiadapter([IDictField, schemata.IThesaurusTerms],
    qualifiers=['td', 'dl'], is_fallback=True)
class DictOfThesaurusTermsReadWidget(ReadFieldWidget):
 
     def get_template(self):
         return 'package/snippets/fields/read-dict-thesaurus_terms.html'

@field_widget_multiadapter([IDictField, schemata.IThesaurusTerms],
    qualifiers=['select'], is_fallback=True)
class DictOfThesaurusTermsEditWidget(EditFieldWidget, DictFieldWidgetTraits):
 
    def get_item_qualifier(self):
        return 'select' 
    
    def get_template(self):
        return 'package/snippets/fields/edit-dict-thesaurus_terms.html'

@field_widget_multiadapter([IDictField, schemata.IThesaurusTerms],
    qualifiers=['select2'], is_fallback=False)
class DictOfThesaurusTermsS2EditWidget(EditFieldWidget, DictFieldWidgetTraits):
 
    def get_item_template_vars(self, key=None, term=None):
        tpl_vars = DictFieldWidgetTraits.get_item_template_vars(self, key, term)
        tpl_vars.update({
            # 'classes': ['ababoua-1', 'ababoua-2']
        })
        return tpl_vars
    
    def get_item_qualifier(self):
        return 'select2' 
    
    def get_template(self):
        return 'package/snippets/fields/edit-dict-thesaurus_terms.html'

#
# ISpatialResolution
#

@object_widget_adapter(schemata.ISpatialResolution)
class SpatialResolutionEditWidget(EditObjectWidget):
        
    def get_template(self):
        return 'package/snippets/objects/edit-spatial_resolution.html' 

@object_widget_adapter(schemata.ISpatialResolution, 
    qualifiers=['item'], is_fallback=False)
class SpatialResolutionAsItemEditWidget(EditObjectWidget):
        
    def get_template(self):
        return 'package/snippets/objects/edit-spatial_resolution-item.html' 

@object_widget_adapter(schemata.ISpatialResolution)
class SpatialResolutionReadWidget(ReadObjectWidget):
        
    def get_template(self):
        return None 

#
# IGeographicBoundingBox
#

@object_widget_adapter(schemata.IGeographicBoundingBox)
class GeographicBoundingBoxEditWidget(EditObjectWidget):
        
    def get_template(self):
        return 'package/snippets/objects/edit-geographic_bbox.html' 

@object_widget_adapter(schemata.IGeographicBoundingBox,
    qualifiers=['item'], is_fallback=False)
class GeographicBoundingBoxAsItemEditWidget(EditObjectWidget):
        
    def get_template(self):
        return 'package/snippets/objects/edit-geographic_bbox-item.html' 

@object_widget_adapter(schemata.IGeographicBoundingBox)
class GeographicBoundingBoxReadWidget(ReadObjectWidget):
        
    def get_template(self):
        return None 

@field_widget_multiadapter([IListField, schemata.IGeographicBoundingBox],
    qualifiers=['td'], is_fallback=False)
class ListOfGeographicBoundingBoxReadWidget(ReadFieldWidget, ListFieldWidgetTraits):

    def prepare_template_vars(self, name_prefix, data):
        parent = super(ListOfGeographicBoundingBoxReadWidget, self)
        tpl_vars = parent.prepare_template_vars(name_prefix, data)
        tpl_vars.update({
            'title': None,
            'description': None,
        })
        return tpl_vars

    def get_item_qualifier(self):
        return 'dl' 
    
    def get_template(self):
        return 'package/snippets/fields/read-list.html' 

#
# IConformity
#

@object_widget_adapter(schemata.IConformity)
class ConformityEditWidget(EditObjectWidget):
        
    def get_field_template_vars(self):
        return {
            'title': {
                'title': _('Specification'),
                'input_classes': ['span5'],
            },
            'date': {
                'title': _('Date'),
            },
            'date_type': {
                'title': _('Date Type'),
            },
            'degree': {
                'title': _('Degree'),
            },
        }
    
    def get_field_qualifiers(self):
        return OrderedDict([
            ('title', None),
            ('date', None),
            ('date_type', 'select2'),
            ('degree', 'select2')
        ])
   
    def get_template(self):
        return None 

@object_widget_adapter(schemata.IConformity)
class ConformityReadWidget(ReadObjectWidget):
        
    def get_template(self):
        return None 

#
# IReferenceSystem
#

@object_widget_adapter(schemata.IReferenceSystem)
class ReferenceSystemEditWidget(EditObjectWidget):
    
    def get_field_qualifiers(self):
        return OrderedDict([
            ('code', 'select2'),
        ])

    def get_field_template_vars(self):
        return {
            'code': {
                'title': _('CRS Code'),
            },
        }

    def get_template(self):
        return None 

@object_widget_adapter(schemata.IReferenceSystem)
class ReferenceSystemReadWidget(ReadObjectWidget):

    def get_template(self):
        return None 

@object_widget_adapter(schemata.IReferenceSystem, 
    qualifiers=['td'], is_fallback=False)
class TdReferenceSystemReadWidget(ReadObjectWidget):
    
    def get_template(self):
        return 'package/snippets/objects/read-reference_system-td.html' 

#
# IFreeKeyword
#

@field_widget_multiadapter([IListField, schemata.IFreeKeyword])
class FreeKeywordsReadWidget(ReadFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/read-list-free_keyword.html'

@field_widget_multiadapter([IListField, schemata.IFreeKeyword], qualifiers=['td'])
class TdFreeKeywordsReadWidget(ReadFieldWidget):

    def get_template(self):
        return 'package/snippets/fields/read-list-free_keyword-td.html'

#
# IDate
#

@object_widget_adapter(schemata.IDate)
class DateEditWidget(EditObjectWidget):
        
    def get_field_template_vars(self):
        return {
            'date': {
                'title': _('Date'),
            },
            'date_type': {
                'title': _('Date Type'),
            },
            'date_info': {
                'title': _('Date Info'),
            },
        }
    
    def get_field_qualifiers(self):
        return OrderedDict([
            ('date', None),
            ('date_type', None),
            ('date_info', None)
        ])
   
    def get_template(self):
        return None 

@object_widget_adapter(schemata.IDate)
class DateReadWidget(ReadObjectWidget):
        
    def get_template(self):
        return None 


#
# ICreator

@object_widget_adapter(schemata.ICreator)
class CreatorEditWidget(EditObjectWidget):

    def get_field_qualifiers(self):
        return OrderedDict([
            ('creator_name', None),
            #('creator_name_type', None),
            #('creator_name_identifier', None),
            #('creator_name_identifier_scheme', None),
            #('creator_name_identifier_scheme_uri', None),
            ('creator_affiliation', None),
        ])
    
    def get_field_template_vars(self):
        return {
            'creator_name': {
                'title': _('Creator'),
                
            },
            'creator_name_type': {
                'title': _('Creator name type'),
            },
            'creator_name_identifier': {
                'title': _('Creator name identifier'),
            },
            'creator_name_identifier_scheme': {
                'title': _('Creator name identifier scheme'),
            },
            'creator_name_identifier_scheme_uri': {
                'title': _('Creator name identifier scheme uri'),
            },
            'creator_affiliation': {
                'title': _('Organization'),
            },
            
        }

    def get_template(self):
        
        return None # use default glue template
        #return 'package/snippets/fields/read-text-dd.html'

@object_widget_adapter(schemata.ICreator, qualifiers=['dd','td'])
class CreatorReadWidget(ReadObjectWidget):
    
    def get_field_qualifiers(self):
        return OrderedDict([
            ('creator_name', None),
            ('creator_affiliaton', None),
        ])
    
    def get_field_order(self):
        return[
            'creator_name',
            'creator_affiliation',
        ]
            

    def get_field_template_vars(self):
        return {
            'creator_name': {
                'title': _('Creator'),
            },
            'creator_affiliation': {
                'title': _('Creator affiliation'),
            },
        }

    def get_template(self):
        return None # use glue template
        #return 'package/snippets/fields/read-text-dd.html'

@object_widget_adapter(schemata.ISubject)
class SubjectEditWidget(EditObjectWidget):

    def get_field_qualifiers(self):
        return OrderedDict([
            ('subject_name', None),
            ('subject_scheme', None),
            ('subject_scheme_uri', None),
            ('subject_value_uri', None),
        ])

    def get_template(self):
        return None # use default glue template
        #return 'package/snippets/fields/read-text-dd.html'

#IContributor

@object_widget_adapter(schemata.IContributor)
class ContributorEditWidget(EditObjectWidget):

    def get_field_template_vars(self):
        return {
            'contributor_name': {
                'title': _('Contributor'),
            },
            
        }

    def get_field_qualifiers(self):
        return OrderedDict([
            ('contributor_name', None),
            #('contributor_type', None),
            #('contributor_name_type', None),
            #('contributor_name_identifier', None),
            #('contributor_name_identifier_scheme', None),
            #('contributor_name_identifier_scheme_uri', None),
            #('contributor_affiliation', None),
        ])

    def get_template(self):
        return None # use default glue template
        #return 'package/snippets/fields/read-text-dd.html'

@object_widget_adapter(schemata.IRelatedIdentifier)
class RelatedIdentifierEditWidget(EditObjectWidget):

    def get_field_qualifiers(self):
        return OrderedDict([
            ('related_identifier', None),
            ('related_identifier_type', None),
            ('relation_type', None),
            ('related_metadata_scheme', None),
            ('related_metadata_scheme_uri', None),
            ('related_metadata_scheme_type', None),
        ])

    def get_template(self):
        return None # use default glue template
        #return 'package/snippets/fields/read-text-dd.html'

@object_widget_adapter(schemata.IAlternateIdentifier)
class AlternateIdentifierEditWidget(EditObjectWidget):

    def get_field_qualifiers(self):
        return OrderedDict([
            ('alternate_identifier', None),
            ('alternate_identifier_type', None),            
        ])

    def get_template(self):
        return None # use default glue template
        #return 'package/snippets/fields/read-text-dd.html'

@object_widget_adapter(schemata.IFundingReference)
class FundingReferenceEditWidget(EditObjectWidget):

    def get_field_qualifiers(self):
        return OrderedDict([
            ('funder_name', None),
            ('funder_identifier', None),
            ('funder_identifier_type', None),
            ('award_number', None),
            ('award_uri', None),
            ('award_title', None),
        ])

    def get_template(self):
        return None # use default glue template
        #return 'package/snippets/fields/read-text-dd.html'

@object_widget_adapter(schemata.IPublicationInfo)
class PublicationInfoEditWidget(EditObjectWidget):

    def get_field_qualifiers(self):
        return OrderedDict([
            ('publisher', None),
            ('publication_year', None),
        ])

    def get_field_template_vars(self):
        return {
            'publisher': {
                'title': _('Publisher'),
            },
            'publication_year': {
                'title': _('Publication Year'),
                'placeholder': (u'e.g. 2003'),
            },                        
        }

    def get_template(self):
        return None # use default glue template
        #return 'package/snippets/fields/read-text-dd.html'



