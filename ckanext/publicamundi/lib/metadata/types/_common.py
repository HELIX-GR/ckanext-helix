import zope.interface

from ckan.plugins import toolkit 

from ckanext.publicamundi.lib.metadata.base import (
    Object, object_null_adapter,
    object_format_adapter, ObjectFormatter)

from ckanext.publicamundi.lib.metadata.schemata import *

_ = toolkit._

@object_null_adapter()
class PostalAddress(Object):
    
    zope.interface.implements(IPostalAddress)

    postalcode = None
    address = None
    

@object_null_adapter()
class ContactInfo(Object):
    
    zope.interface.implements(IContactInfo)

    email = None
    address = None
    publish = None

@object_null_adapter()
class Point(Object):
    
    zope.interface.implements(IPoint)

    x = None
    y = None

    def __eq__(self, other):
        if isinstance(other, Point):
            return self.x == other.x and self.y == other.y
        else:
            return False

@object_null_adapter()
class Polygon(Object):

    zope.interface.implements(IPolygon)

    points = None
    name = None

@object_null_adapter()
class ResponsibleParty(Object):
    
    zope.interface.implements(IResponsibleParty)

    organization = None
    email = None
    role = None

@object_null_adapter()
class FreeKeyword(Object):
    
    zope.interface.implements(IFreeKeyword)

    value = None
    originating_vocabulary = None
    reference_date = None
    date_type = None

    @classmethod
    def normalize_keyword(cls, s):
        from inflection import dasherize, underscore
        return dasherize(underscore(unicode(s)))
    
    def __init__(self, **kwargs):
        value = kwargs.get('value')
        if value:
            kwargs['value'] = self.normalize_keyword(value)
        super(FreeKeyword, self).__init__(**kwargs)
        
@object_null_adapter()
class GeographicBoundingBox(Object):
    
    zope.interface.implements(IGeographicBoundingBox)

    nblat = None
    sblat = None
    eblng = None
    wblng = None

@object_null_adapter()
class TemporalExtent(Object):
    
    zope.interface.implements(ITemporalExtent)

    start = None
    end = None

@object_format_adapter(ITemporalExtent)
class TemporalExtentFormatter(ObjectFormatter):

    def _format(self, obj, opts):
        s = _('From %(start)s To %(end)s') % dict(start=obj.start, end=obj.end)
        return u'<%s>' % s if opts.get('quote') else s

@object_null_adapter()
class SpatialResolution(Object):
    
    zope.interface.implements(ISpatialResolution)

    distance = None
    uom = None

@object_null_adapter()
class ReferenceSystem(Object):
    
    zope.interface.implements(IReferenceSystem)

    code = None
    code_space = None
    version = None

@object_null_adapter()
class Conformity(Object):
    
    zope.interface.implements(IConformity)

    title = None
    date = None
    date_type = None
    degree = None

@object_null_adapter()
class Creator(Object):
    
    zope.interface.implements(ICreator)

    creator_name = None
    creator_name_type = None
    creator_name_identifier = None
    creator_name_identifier_scheme = None
    creator_name_identifier_scheme_uri = None
    creator_affiliation = None
    
@object_null_adapter()
class Subject(Object):
    
    zope.interface.implements(ISubject)

    subject_name = None
    subject_scheme = None
    subject_scheme_uri = None
    subject_value_uri = None

@object_null_adapter()
class Contributor(Object):
    
    zope.interface.implements(IContributor)

    contributor_name = None
    contributor_type = None
    contributor_name_type = None
    contributor_name_identifier = None
    contributor_name_identifier_scheme = None
    contributor_name_identifier_scheme_uri = None
    contributor_affiliation = None

@object_null_adapter()
class RelatedIdentifier(Object):
    
    zope.interface.implements(IRelatedIdentifier)

    related_identifier = None
    related_identifier_type = None
    relation_type = None
    related_metadata_scheme = None
    related_metadata_scheme_uri = None
    related_metadata_scheme_type = None

@object_null_adapter()
class AlternateIdentifier(Object):
    
    zope.interface.implements(IAlternateIdentifier)

    alternate_identifier = None
    alternate_identifier_type = None

@object_null_adapter()
class FundingReference(Object):
    
    zope.interface.implements(IFundingReference)

    funder_name = None
    funder_identifier = None
    funder_identifier_type = None
    award_number = None
    award_uri = None
    award_title = None


