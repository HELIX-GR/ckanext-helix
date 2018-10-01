import re
import datetime
import zope.interface
import zope.schema
import zope.schema.vocabulary
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
import z3c.schema.email

from ckanext.publicamundi.lib import vocabularies
from ckanext.publicamundi.lib.metadata.ibase import IObject

import logging
log1 = logging.getLogger(__name__)

_ = lambda t:t

class IPostalAddress(IObject):

    address = zope.schema.Text(
        title = _(u'Postal address'),
        required = True)

    postalcode = zope.schema.TextLine(
        title = _(u'Postal code'),
        required = True,
        constraint = re.compile("\d{5,5}$").match)

class IPoint(IObject):

    x = zope.schema.Float(required=True)
    y = zope.schema.Float(required=True)

class IPolygon(IObject):

    points = zope.schema.List(
        title = _(u'Points'),
        value_type = zope.schema.Object(IPoint, title=_(u'Point')),
        required = True,
        max_length = 8,
        min_length = 4)

    name = zope.schema.TextLine()

    @zope.interface.invariant
    def check_polygon(obj):
        if not (obj.points[0] == obj.points[-1]):
            raise zope.interface.Invalid(_(u'The polygon line must be closed'))

class IContactInfo(IObject):

    email = z3c.schema.email.RFC822MailAddress(title=_(u'Email'),
        description=_(u'Electronic mail address'), required=False)

    address = zope.schema.Object(IPostalAddress, title=_(u'Postal Address'), required=False)
    
    publish = zope.schema.Bool(title=_(u'Publish'), 
        description=_(u'This information can be safely published'), required=False)

    #@zope.interface.invariant
    #def not_empty(obj):
    #    if obj.email is None and obj.address is None:
    #        raise zope.interface.Invalid(_(u'At least one of email/address should be supplied'))

class IResponsibleParty(IObject):

    organization = zope.schema.TextLine(
        title = _(u'Organization Name'),
        required = True,
        min_length = 2)
    organization.setTaggedValue('translatable', True)   

    email = z3c.schema.email.RFC822MailAddress(
        title = _(u'Email'),
        required = True)

    role = zope.schema.Choice(
        title = _(u'Responsible Party Role'),
        vocabulary = vocabularies.by_name('party-roles').get('vocabulary'), 
        description = _(u'This is the role of the responsible organisation.'),
        default = 'pointOfContact',
        required = True)

class IFreeKeyword(IObject):

    value = zope.schema.TextLine(
        title = _(u'Keyword value'),
        description = _(u'The keyword value is a commonly used word, formalised word or phrase used to describe the subject. While the topic category is too coarse for detailed queries, keywords help narrowing a full text search and they allow for structured keyword search.\nThe value domain of this metadata element is free text.'),
        required = True)

    originating_vocabulary = zope.schema.TextLine(
        title = _(u'Title'),
        description = _(u'If the keyword value originates from a controlled vocabulary (thesaurus, ontology), for example GEMET, the citation of the originating controlled vocabulary shall be provided.\nThis citation shall include at least the title and a reference date (date of publication, date of last revision or of creation) of the originating controlled vocabulary.'),
        required = False)

    reference_date = zope.schema.Date(
        title = _(u'Reference date'),
        required = False)

    date_type = zope.schema.Choice(
        title = _(u'Date Type'),
        vocabulary = vocabularies.by_name('date-types').get('vocabulary'),
        required = False)

    @zope.interface.invariant
    def check_mandatory_parts(obj):
        if obj.originating_vocabulary or obj.reference_date or obj.date_type:
            if not obj.originating_vocabulary or not obj.reference_date or not obj.date_type:
                raise zope.interface.Invalid(_(u'You need to fill in the rest free-keyword fields'))

class IGeographicBoundingBox(IObject):
    
    sblat = zope.schema.Float(
        title = _(u'South Bound Latitude'),
        min = -90.0,
        max = 90.0,
        required = True)

    nblat = zope.schema.Float(
        title = _(u'North Bound Latitude'),
        min = -90.0,
        max = 90.0,
        required = True)
    
    wblng = zope.schema.Float(
        title = _(u'West Bound Longitude'),
        min = -180.0,
        max = 180.0,
        required = True)

    eblng = zope.schema.Float(
        title = _(u'East Bound Longitude'),
        min = -180.0,
        max = 180.0,
        required = True)

    @zope.interface.invariant
    def check_wb_eb(obj):
        if (obj.wblng > obj.eblng):
            raise zope.interface.Invalid(_(
                u'The east bound must be greater than the west bound'))
    
    @zope.interface.invariant
    def check_sb_nb(obj):
        if (obj.sblat > obj.nblat):
            raise zope.interface.Invalid(_(
                u'The north bound must be greater than the south bound'))

class ITemporalExtent(IObject):

    start = zope.schema.Date(
        title = _(u'Start Date'),
        required = True,)

    end = zope.schema.Date(
        title = _(u'End Date'),
        required = True,)

    @zope.interface.invariant
    def check_date_order(obj):
        if obj.start > obj.end:
            msg = _(u'The start-date (%s) is later than end-date (%s)') % (obj.start, obj.end)
            raise zope.interface.Invalid(msg)

class ISpatialResolution(IObject):
    
    zope.interface.taggedValue('allow-partial-update', False)

    denominator = zope.schema.Int(
        title = _(u'Equivalent Scale'),
        min = 1, # positive integer
        required = False)

    distance = zope.schema.Int(
        title = _(u'Resolution Distance'),
        min = 1, # positive integer
        required = False)

    uom = zope.schema.TextLine(
        title = _(u'Unit of Measure'),
        required = False,
        min_length = 1)

    @zope.interface.invariant
    def check(obj):
        # A valid spatial-resolution must have at least one of the following:
        # (i) a denominator, or (ii) a distance with a specified unit
        if not obj.denominator:
            if not (obj.distance and obj.uom):
                raise zope.interface.Invalid(_(
                    u'At least of one of (i) a denominator, or (ii) a distance must be given.'))

class IReferenceSystem(IObject):

    code = zope.schema.Choice(
            title= _(u'System'),
            description = _(u'Coordinate Reference System'),
            vocabulary = vocabularies.by_name('reference-systems').get('vocabulary'),
            default = 'http://www.opengis.net/def/crs/EPSG/0/2100',
            required = True)

    code_space = zope.schema.NativeStringLine(
            title = _(u'Code-Space'),
            description = _(u'Reference System Code-Space'),
            #default = 'urn:ogc:def:crs:EPSG',
            required = False)

    version = zope.schema.NativeStringLine(
            title = _(u'Version'),
            description = _(u'Reference System version'),
            #default = '6.11.2',
            required = False)


class IConformity(IObject):

    title = zope.schema.Text(
        title = _(u'Specification'),
        required = True)
    title.setTaggedValue('translatable', True)

    date = zope.schema.Date(
        title = _(u'Date'),
        required = True)

    date_type = zope.schema.Choice(
        title = _(u'Date Type'),
        vocabulary = vocabularies.by_name('date-types').get('vocabulary'),
        required = True)

    degree = zope.schema.Choice(
        title = _(u'Degree'),
        vocabulary = vocabularies.by_name('degrees').get('vocabulary'),
        description = _(u'This is the degree of conformity of the resource to the implementing rules adopted under Article 7(1) of Directive 2007/2/EC or other specification.'),
        default = "not-evaluated",
        required = True)

class ICreator(IObject):

    creator_name = zope.schema.TextLine(
        title = _(u'Creator name'),
        description=_(u'Person or organization that has produced the dataset'), 
        required=True)
    '''
    creator_name_type = zope.schema.Choice(
        title = _(u'Creator name type'),
        vocabulary = vocabularies.by_name('name-type').get('vocabulary'), 
        description = _(u'This is the type of creator name.'),
        default = 'personal',
        required = False)    

    creator_name_identifier = zope.schema.TextLine(
        title = _(u'Creator name identifier'),
        description=_(u'Name identifier'), required=False)

    creator_name_identifier_scheme = zope.schema.TextLine(
        title = _(u'Creator name identifier scheme'),
        description=_(u'Name identifier scheme'), required=False)
    
    creator_name_identifier_scheme_uri = zope.schema.TextLine(
        title = _(u'Creator name identifier scheme uri'),
        description=_(u'Name identifier scheme uri'), required=False)   
    '''
    creator_affiliation = zope.schema.TextLine(
        title = _(u'Organization'),
        #vocabulary = vocabularies.by_name('affiliation-type').get('vocabulary'), 
        description=_(u'The affiliation of the creator'),
        #default = _(u'Institutional'),
        required = False)

class ISubject(IObject):

    subject_name = zope.schema.TextLine(
        title = _(u'Subject'),
        description=_(u'Subject, keyword, classification code'), required=False)
    
    subject_scheme = zope.schema.TextLine(
        title = _(u'Subject scheme'),
        description = _(u'This is the scheme of the subject'),
        required = False)    

    subject_scheme_uri = zope.schema.TextLine(
        title = _(u'Subject scheme uri'),
        description = _(u'This is the scheme uri of the subject'),
        required = False)    

    subject_value_uri = zope.schema.TextLine(
        title = _(u'Subject value uri'),
        description = _(u'This is the value uri of the subject'),
        required = False)    

class IContributor(IObject):

    contributor_name = zope.schema.TextLine(
        title = _(u'Contributor'),
        description=_(u'Institutional/personal name'), required=False)
    
    '''contributor_type = zope.schema.TextLine(
        title = _(u'Contributor type'),
        description=_(u'Distributor, project leader etc.'), required=False)    

    contributor_name_type = zope.schema.Choice(
        title = _(u'Contributor name type'),
        vocabulary = vocabularies.by_name('name-type').get('vocabulary'), 
        description = _(u'This is the type of contributor name.'),
        #default = 'personal',
        required = False)    

    contributor_name_identifier = zope.schema.TextLine(
        title = _(u'Contributor name identifier'),
        description=_(u'Name identifier'), required=False)

    contributor_name_identifier_scheme = zope.schema.TextLine(
        title = _(u'Contributor name identifier scheme'),
        description=_(u'Name identifier scheme'), required=False)
    
    contributor_name_identifier_scheme_uri = zope.schema.TextLine(
        title = _(u'Contributor name identifier scheme uri'),
        description=_(u'Name identifier scheme uri'), required=False)

    contributor_affiliation = zope.schema.Choice(
        title = _(u'Contributor affiliation'),
        vocabulary = vocabularies.by_name('affiliation-type').get('vocabulary'), 
        description=_(u'This is the affiliation of the contributor'), required=False,
        #default = 'institutional'
        )
    '''    

class IAlternateIdentifier(IObject):

    alternate_identifier = zope.schema.TextLine(
        title = _(u'Alternate identifier'),
        description=_(u'e.g. E-GEOD-34814'), required=False)
    
    alternate_identifier_type = zope.schema.TextLine(
        title = _(u'Alternate identifier type'),
        description=_(u'Alternate Identifier type'), required=False)

class IRelatedIdentifier(IObject):

    related_identifier = zope.schema.TextLine(
        title = _(u'Related identifier'),
        description=_(u'related identifier'), required=False)
    
    related_identifier_type = zope.schema.Choice(
        title = _(u'Related identifier type'),
        vocabulary = vocabularies.by_name('related-identifier-type').get('vocabulary'), 
        #default = 'issn', 
        description=_(u'related identifier type'), required=False)
    
    relation_type = zope.schema.Choice(
        title = _(u'Relation type'),
        vocabulary = vocabularies.by_name('relation-type').get('vocabulary'), 
        #default = 'IsSupplementTo', 
        description=_(u'relation type'), required=False)
    
    related_metadata_scheme = zope.schema.TextLine(
        title = _(u'Related metadata scheme'),
        description=_(u'related metadat scheme'), required=False)    

    related_metadata_scheme_uri = zope.schema.TextLine(
        title = _(u'Related metadata scheme uri'),
        description=_(u'related metadat scheme uri'), required=False) 

    related_metadata_scheme_type = zope.schema.TextLine(
        title = _(u'Related metadata scheme type'),
        description=_(u'related metadat scheme type'), required=False) 

class IFundingReference(IObject):

    funder_name = zope.schema.TextLine(
        title = _(u'Funder name'),
        description=_(u'funder'), required=False)
    
    funder_identifier = zope.schema.TextLine(
        title = _(u'Funder identifier'),
        description=_(u'e.g. https://doi.org/10.13039/100000936'), required=False)
    
    funder_identifier_type = zope.schema.Choice(
        title = _(u'Funder identifier type'),
        vocabulary = vocabularies.by_name('funder-identifier-type').get('vocabulary'),
        #default = 'crossrefFunder', 
        description=_(u'funder identifier type'), required=False)
    
    award_number = zope.schema.TextLine(
        title = _(u'Award number'),
        description=_(u'e.g. GBMF3859.01'), required=False)    

    award_uri = zope.schema.TextLine(
        title = _(u'Award uri'),
        description=_(u'e.g. https://www.moore.org/grants/list/GBMF3859.01'), required=False) 

    award_title = zope.schema.TextLine(
        title = _(u'Award title'),
        description=_(u'award title'), required=False)

class IDate(IObject):
    
    date = zope.schema.Date(
        title = _(u'Date'),
        description=_(u'date'), required=False)

    date_type = zope.schema.Choice(
        vocabulary = SimpleVocabulary((
            SimpleTerm('accepted', 'accepted', u'Accepted'),
            SimpleTerm('available', 'available', u'Available'),
            SimpleTerm('copyrighted', 'copyrighted', u'Copyrighted'),
            SimpleTerm('collected', 'collected', u'Collected'),
            SimpleTerm('created', 'created', u'Created'),
            SimpleTerm('issued', 'issued', u'Issued'),
            SimpleTerm('submitted', 'submitted', u'Submitted'),
            SimpleTerm('updated', 'updated', u'Updated'),
            SimpleTerm('valid', 'valid', u'Valid'),)),
        title = u'Date type',
        required=False)

    date_info = zope.schema.TextLine(
        title = _(u'Date Info'),
        description=_(u'date info'), required=False)

class IPublicationInfo(IObject):

    publisher = zope.schema.Choice(
        vocabulary = SimpleVocabulary((
            SimpleTerm('helix', 'helix', u'Helix'),
            SimpleTerm('aei', 'aei', u'AEI'),
            SimpleTerm('tei', 'tei', u'TEI'),
            SimpleTerm('iek', 'iek', u'IEK'),
            SimpleTerm('clarity', 'clariy', u'Clarity'))),
        title = u'Publisher',
        required = False,
    ) 

    publication_year = zope.schema.Int(
        title = u'Publication year',
        required = False)
        #default = 2005,)

    
