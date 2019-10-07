# -*- coding: UTF-8 -*-

import re
import zope.interface
import zope.schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from ckanext.helix.lib.metadata.ibase import IObject

from ckanext.helix.lib import vocabularies

from . import IMetadata
from ._common import *

from uuid import UUID
_ = lambda t: t # Mock translator

class InvalidDoi(zope.schema.ValidationError):
        __doc__ = _("Input is not a valid DOI")


class IDataciteMetadata(IMetadata):
   
    zope.interface.taggedValue('recurse-on-invariants', True)

    url = zope.schema.URI(
        title = u'URL',
        required = False)
   
    abstract = zope.schema.Text(
        title = _(u'Dataset Abstract'),
        description = _(u'This is a brief narrative summary of the contents of this dataset.'),
        required = False)
    abstract.setTaggedValue('translatable', True)
    abstract.setTaggedValue('links-to', 'notes')

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

    '''contact_info = zope.schema.Object(IContactInfo,
        title = u'Contact Info',
        required = True)'''
    
    public_doi = zope.schema.TextLine(
        title = u'Public DOI',
        required = False)
    

    def valid_doi_check(value):
        #check for regular expression for dois
        regexDOI = re.compile('(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?![%"#? ])\\S)+)')   
        if not re.match(regexDOI,value):   
            raise InvalidDoi
        return True    


    #zope.interface.invariant(valid_doi_check)    
    #     
    related_publication = zope.schema.TextLine(
        title = u'Related Publication',
        description = (u'The DOI of a related publication'),
        required = False,
        constraint=valid_doi_check)
    
    closed_subject = zope.schema.List(
        title = u'Subjects',
        required = False,
        value_type = zope.schema.TextLine(
            title = u'Subject'),
        min_length = 1,
        max_length = 4)
    closed_subject.setTaggedValue('links-to', 'closed_tag')    
 
    license_id = zope.schema.TextLine(
        title = u'License',
        description = (u'The license of the dataset'),
        required = False)
    license_id.setTaggedValue('links-to', 'license_id')    
 
    free_tags = zope.schema.List(
        title= _(u'Tags'),
        description = _(u'Free keywords'),
        required = False,
        value_type = zope.schema.TextLine(
            title = u'Tag'),
        min_length = 1,
        max_length = 6)
    free_tags.setTaggedValue('links-to', 'tags')  
    
    contact_email = z3c.schema.email.RFC822MailAddress(
        title = _(u'Contact e-mail'),
        description = (u'Email address of the contact person for this dataset'),
        required = True)
    
    creator = zope.schema.Object(ICreator,
        description = (u'The researcher involved in producing the data'),
        title = u'Creator',
        required = False)
    
    '''subject = zope.schema.Object(ISubject,
        title = u'Subject',
        required = False) '''
    

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
    

    date = zope.schema.List(
        title = _(u'Dates'),
        description = _(u'A relavant date to the dataset.'),
        required = False,
        min_length = 1,
        max_length = 4,
        value_type = zope.schema.Object(IDate,
            title = _(u'Date')))
    date.setTaggedValue('format:markup', {'descend-if-dictized': True})  '''
    
    
    languagecode = zope.schema.Choice(
        title = _(u'Language'),
        vocabulary = vocabularies.by_name('languages-iso-639-2').get('vocabulary'),
        description = _(u'This is the language in which the metadata elements are expressed. The value domain of this metadata element is limited to the official languages of the Community expressed in conformity with ISO 639-2.'),
        required = False,
        default = 'eng')
    #languagecode.setTaggedValue('format:markup', {'descend-if-dictized': False})


    @zope.interface.invariant
    def check_tag_duplicates(obj):
        s = set(obj.tags)
        if len(s) < len(obj.tags):
            raise zope.interface.Invalid('Tags contain duplicates')
    
    