import re
import zope.interface
import zope.schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from ckanext.publicamundi.lib.metadata.ibase import IObject

from . import IMetadata
from ._common import *

_ = lambda t: t # Mock translator

class IFooMetadata(IMetadata):
    
    zope.interface.taggedValue('recurse-on-invariants', True)

    url = zope.schema.URI(
        title = u'URL',
        required = False)
   

    thematic_category = zope.schema.Choice(
        vocabulary = SimpleVocabulary((
            SimpleTerm('environment', 'environment', u'Environment'),
            SimpleTerm('government', 'government', u'Government'),
            SimpleTerm('health', 'health', u'Health'),
            SimpleTerm('economy', 'economy', u'Economy'))),
        title = u'Category',
        required = False,)
        #default = 'economy')

    baz = zope.schema.TextLine(
        title = u'Baz',
        required = False,
        #default = u'bazinka',
        min_length = 5)

    tags = zope.schema.List(
        title = u'Tags',
        required = False,
        value_type = zope.schema.TextLine(
            title = u'Tag',
            constraint = re.compile('[-a-z0-9]+$').match),
        #min_length = 1,
        max_length = 5,)
    tags.setTaggedValue('allow-partial-update', False)
    tags.setTaggedValue('format', { 'descend-if-dictized': False, 'extra-opts': {}, })

    temporal_extent = zope.schema.Object(ITemporalExtent,
        title = u'Temporal Extent',
        required = False)
    temporal_extent.setTaggedValue('format', { 'descend-if-dictized': False })

    geometry = zope.schema.List(
        title = u'Geometry Feature',
        required = False,
        value_type = zope.schema.List(
            title = u'Polygon Area',
            value_type = zope.schema.Object(IPolygon,
                title = u'Polygon'
            ),
            max_length = 2),
        max_length = 2,)

    reviewed = zope.schema.Bool(
        required = False,
        title = u'Reviewed',
        #default = False,
        description = u'This foo is reviewed by someone',)

    optional_title = zope.schema.TextLine(
        required = False,
        title = u'Title (Greek)',
        description = u'Optional title in Greek',)
    optional_title.setTaggedValue('translatable', True)


    optional_description = zope.schema.Text(
        required = False,
        title = u'Description (Greek)',
        description = u'Optional notes in greek',)
    optional_description.setTaggedValue('translatable', True)

   

    contacts = zope.schema.Dict(
        title = u'Contacts',
        required = False,
        key_type = zope.schema.Choice(
            vocabulary = SimpleVocabulary((
                SimpleTerm('personal', 'personal', u'Personal'), 
                SimpleTerm('personal-alt', 'personal-alt', u'Personal (alt)'), 
                SimpleTerm('office', 'office', u'Office'))),
            title = u'The type of contact'),
        value_type = zope.schema.Object(IContactInfo,
            title = u'Contact',
            required = True))

    contact_info = zope.schema.Object(IContactInfo,
        title = u'Contact Info',
        required = True)
    
    created = zope.schema.Datetime(
        title = u'Created',
        required = False)
    
    published = zope.schema.Datetime(
        title = u'Published',
        required = False,
        description = u'Add your notes',)

    wakeup_time = zope.schema.Time(
        title = u'Wakeup Time',
        required = False)

    rating = zope.schema.Int(
        title = u'Rating',
        required = False,
        min = -10,
        max = 10)
    
    grade = zope.schema.Float(
        title = u'Grade',
        required = False,
        min = -20.0,
        max = 20.0)

    password = zope.schema.Password(
        title = u'Password',
        required = False,
        min_length = 6,
    )
    
    public_doi = zope.schema.TextLine(
        title = u'Public DOI',
        required = False)
    
    creator = zope.schema.Object(ICreator,
        description = (u'The researcher involved in producing the data'),
        title = u'Creator',
        required = False)
    
    subject = zope.schema.Object(ISubject,
        title = u'Subject',
        required = False)
    
    contributor = zope.schema.Object(IContributor,
        description = (u'The institution or person responsible for collecting,distributing, or otherwise contributing to the development of the resource.'),
        title = u'Contributor',
        required = False) 

    '''contributor = zope.schema.List(
        title = _(u'Contributor'),
        description = _(u'The institution or person responsible for collecting,distributing, or otherwise contributing to the development of the resource.'),
        required = False,
        min_length = 1,
        max_length = 4,
        value_type = zope.schema.Object(IContributor,
            title = _(u'Contributor')))
    contributor.setTaggedValue('format:markup', {'descend-if-dictized': True}) '''

    '''alternate_identifier = zope.schema.Object(IAlternateIdentifier,
        title = u'Alternate Identifier',
        required = False)

    related_identifier = zope.schema.Object(IRelatedIdentifier,
        title = u'Related Identifier',
        required = False)

    funding_reference = zope.schema.Object(IFundingReference,
        title = u'Funding Reference',
        required = False)
    '''

    date = zope.schema.List(
        title = _(u'Dates'),
        description = _(u'A relavant date to the dataset.'),
        required = False,
        min_length = 1,
        max_length = 4,
        value_type = zope.schema.Object(IDate,
            title = _(u'Date')))
    date.setTaggedValue('format:markup', {'descend-if-dictized': True})
    
    '''date  = zope.schema.Object(IDate,
        description = (u'A relevant date to the dataset'),
        title=u'Date',
        required=False)'''

    language = zope.schema.Choice(
        description = u'The language of the dataset',
        vocabulary = SimpleVocabulary((
            SimpleTerm('greek', 'greek', u'Greek'),
            SimpleTerm('english', 'english', u'English'))),
        title = u'Language',
        required = False,)
        #default = 'english')
    
    publication_info = zope.schema.Object(IPublicationInfo,
        description = (u'Information about the publication'),
        title = u'Publication Info',
        required = True)
    

    subject_closed = zope.schema.Choice(
        vocabulary = SimpleVocabulary((
            SimpleTerm('biological sciences', 'biological sciences', u'biological ciences'),
            SimpleTerm('english', 'english', u'English'))),
        title = u'Language',
        required = False,)
        #default = 'english')

    @zope.interface.invariant
    def check_tag_duplicates(obj):
        s = set(obj.tags)
        if len(s) < len(obj.tags):
            raise zope.interface.Invalid('Tags contain duplicates')
    
    @zope.interface.invariant
    def check_publication_date(obj):
        if obj.published and (obj.published < obj.created):
            raise zope.interface.Invalid('The publication date is before creation date')

    #@zope.interface.invariant
    #def publication_not_empty(obj):
     #   if obj.publication_year is None and obj.address is None:
      #      raise zope.interface.Invalid(_(u'Publication year is required'))
 
