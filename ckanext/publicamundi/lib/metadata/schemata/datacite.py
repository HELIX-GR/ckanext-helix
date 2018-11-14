# -*- coding: UTF-8 -*-

import re
import zope.interface
import zope.schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from ckanext.publicamundi.lib.metadata.ibase import IObject

from ckanext.publicamundi.lib import vocabularies

from . import IMetadata
from ._common import *

from uuid import UUID
_ = lambda t: t # Mock translator

class relatedPubError(zope.schema.ValidationError):
        __doc__ = _("Input is not a valid UUID")


class IDataciteMetadata(IMetadata):
    
    zope.interface.taggedValue('recurse-on-invariants', True)

    url = zope.schema.URI(
        title = u'URL',
        required = False)
   
    abstract = zope.schema.Text(
        title = _(u'Dataset Abstract'),
        description = _(u'This is a brief narrative summary of the contents of this dataset.'),
        required = True)
    abstract.setTaggedValue('translatable', True)
    abstract.setTaggedValue('links-to', 'notes')

    thematic_category = zope.schema.Choice(
        vocabulary = SimpleVocabulary((
            SimpleTerm('environment', 'environment', u'Environment'),
            SimpleTerm('government', 'government', u'Government'),
            SimpleTerm('health', 'health', u'Health'),
            SimpleTerm('economy', 'economy', u'Economy'))),
        title = u'Category',
        required = False,)
        #default = 'economy')

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
        title = u"Τίτλος (Ελληνικά)",
        description = u'Optional title in Greek',)
    optional_title.setTaggedValue('links-to', 'title_optional')


    optional_description = zope.schema.Text(
        required = False,
        title = u"Περιγραφή (Ελληνικά)",
        description = u'Optional notes in greek',)
    optional_description.setTaggedValue('links-to', 'notes_optional')

    dataset_category = zope.schema.Choice(
        vocabulary = SimpleVocabulary((
            SimpleTerm('bio', 'bio', u'Bio'),
            SimpleTerm('geo', 'geo', u'Geo'))),
        required = False,
        title =  u'Dataset type',
        description = u'Dataset type',)

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
    
    created = zope.schema.Date(
        description = _(u'When this dataset was created.'),
        title = u'Date created',
        required = False)
    
    published = zope.schema.Datetime(
        title = u'Published',
        required = False,
        description = u'Add your notes',)

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
        
    
    publisher = zope.schema.Choice(
        vocabulary = SimpleVocabulary((
            SimpleTerm('helix', 'helix', u'Helix'),
            SimpleTerm('aei', 'aei', u'AEI'),
            SimpleTerm('tei', 'tei', u'TEI'),
            SimpleTerm('iek', 'iek', u'IEK'),
            SimpleTerm('clarity', 'clariy', u'Clarity'))),
        description = (u'The name of the organization publishing the dataset.'),
        title = u'Publisher',
        required=False)    
        
    

    def related_publication_empty(value):
        #check for regular expression for dois
        regexDOI = re.compile('(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?![%"#? ])\\S)+)')   
        if not re.match(regexDOI,value):   
            raise relatedPubError
        return True    


    #zope.interface.invariant(related_publication_empty)    
    #     
    related_publication = zope.schema.TextLine(
        title = u'Related Publication',
        description = (u'The DOI of a related publication'),
        required = False,
        constraint=related_publication_empty)
    
    
    funding_reference = zope.schema.TextLine(
        title = u'Funding Reference',
        description = (u'Information about financial support for the creation of this dataset.'),
        required = False)    
    
    contact_email = z3c.schema.email.RFC822MailAddress(
        title = _(u'Contact e-mail'),
        description = (u'Email address of the contact person for this dataset'),
        required = True)
    
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

    #language = zope.schema.Choice(
    #    description = u'The language of the dataset',
    #    vocabulary = SimpleVocabulary((
    #        SimpleTerm('greek', 'greek', u'Greek'),
    #        SimpleTerm('english', 'english', u'English'))),
    #    title = u'Language',
    #    required = False,)
        #default = 'english')
        
    
    languagecode = zope.schema.Choice(
        title = _(u'Language'),
        vocabulary = vocabularies.by_name('languages-iso-639-2').get('vocabulary'),
        description = _(u'This is the language in which the metadata elements are expressed. The value domain of this metadata element is limited to the official languages of the Community expressed in conformity with ISO 639-2.'),
        required = False,
        default = 'eng')
    #languagecode.setTaggedValue('format:markup', {'descend-if-dictized': False})
    
    publication_info = zope.schema.Object(IPublicationInfo,
        description = (u'Information about the publication'),
        title = u'Publication Info',
        required = True)
    
    subject_closed = zope.schema.List(
        title = u'Closed Tags',
        required = True,
        value_type = zope.schema.TextLine(
            title = u'Closed Tag'),
        min_length = 1,
        max_length = 5,)
    subject_closed.setTaggedValue('links-to', 'closed_tag')    


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
 
