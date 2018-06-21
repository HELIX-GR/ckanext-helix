import zope.interface
import zope.schema
import re

from ckanext.publicamundi.lib.metadata.ibase import IObject

from . import IMetadata

class ICkanMetadata(IMetadata):
    
    zope.interface.taggedValue('recurse-on-invariants', True)
    
    #publisher = zope.schema.TextLine(title=u'Publisher', required=False, min_length=3)
    #publisher.setTaggedValue('links-to', 'publisher')
    
    publication_year = zope.schema.TextLine(title=u'Publication year', required=False, min_length=3)
    publication_year.setTaggedValue('links-to', 'publication_year')
	
    license_uri = zope.schema.TextLine(title=u'License URI', required=False, min_length=3)
    license_uri.setTaggedValue('links-to', 'license_uri')
    
    notes = zope.schema.TextLine(title=u'Notes', required=False, min_length=3)
    notes.setTaggedValue('links-to', 'notes')

    date = zope.schema.TextLine(title=u'Date', required=False, min_length=3)
    date.setTaggedValue('links-to', 'date')

    date_information = zope.schema.TextLine(title=u'Date information', required=False, min_length=3)
    date_information.setTaggedValue('links-to', 'date_information')
    
    #resource_type_general = zope.schema.TextLine(title=u'Resource type', required=False, min_length=3)
    #resource_type_general.setTaggedValue('links-to', 'resource_type_general')

    alternate_identifier = zope.schema.TextLine(title=u'Alternate identifier', required=False, min_length=3)
    alternate_identifier.setTaggedValue('links-to', 'alternate_identifier')
    
    alternate_identifier_type = zope.schema.TextLine(title=u'Alternate identifier type', required=False, min_length=3)
    alternate_identifier_type.setTaggedValue('links-to', 'alternate_identifier_type')
    
    subject = zope.schema.TextLine(title=u'Subject', required=False)
    subject.setTaggedValue('links-to', 'subject')

    subject_scheme = zope.schema.TextLine(title=u'  Subject scheme', required=False)
    subject_scheme.setTaggedValue('links-to', 'subject_scheme')

    subject_scheme_uri = zope.schema.TextLine(title=u'  Subject scheme URI', required=False)
    subject_scheme_uri.setTaggedValue('links-to', 'subject_scheme_uri')

    subject_value_uri = zope.schema.TextLine(title=u' Subject value URI', required=False)
    subject_value_uri.setTaggedValue('links-to', 'subject_value_uri')

    # Creator #   
    

    # Contributor #

    contributor = zope.schema.TextLine(title=u'Contributor', required=False, min_length=3)
    contributor.setTaggedValue('links-to', 'contributor')

    contributor_type = zope.schema.TextLine(title=u'Contributor type', required=False)
    contributor_type.setTaggedValue('links-to', 'contributor_type')

    contributor_name_type = zope.schema.TextLine(title=u'Contributor name type', required=False)
    contributor_name_type.setTaggedValue('links-to', 'contributor_name_type')

    contributor_name_identifier = zope.schema.TextLine(title=u'Contributor name identifier', required=False)
    contributor_name_identifier.setTaggedValue('links-to', 'contributor_name_identifier')    

    contributor_name_identifier_scheme = zope.schema.TextLine(title=u'  Name identifier scheme', required=False)
    contributor_name_identifier_scheme.setTaggedValue('links-to', 'contributor_name_identifier_scheme')

    contributor_name_identifier_scheme_uri = zope.schema.TextLine(title=u'  Identifier scheme URI', required=False)
    contributor_name_identifier_scheme_uri.setTaggedValue('links-to', 'contributor_name_identifier_scheme_uri')

    contributor_affiliation = zope.schema.TextLine(title=u'Contributor affiliation', required=False)
    contributor_affiliation.setTaggedValue('links-to', 'contributor_affiliation')

    # Related identifier #

    related_identifier = zope.schema.TextLine(title=u'Related identifier', required=False, min_length=3)
    related_identifier.setTaggedValue('links-to', 'related_identifier')

    related_identifier_type = zope.schema.TextLine(title=u'Related identifier type', required=False)
    related_identifier_type.setTaggedValue('links-to', 'related_identifier_type')

    relation_type = zope.schema.TextLine(title=u'Contributor name type', required=False)
    relation_type.setTaggedValue('links-to', 'relation_type')

    related_metadata_scheme = zope.schema.TextLine(title=u'Related metadata scheme', required=False)
    related_metadata_scheme.setTaggedValue('links-to', 'related_metadata_scheme')    

    related_metadata_scheme_uri = zope.schema.TextLine(title=u'Related metadata_scheme URI', required=False)
    related_metadata_scheme_uri.setTaggedValue('links-to', 'related_metadata_scheme_uri')

    related_metadata_scheme_type = zope.schema.TextLine(title=u'  Related metadata scheme type', required=False)
    related_metadata_scheme_type.setTaggedValue('links-to', 'related_metadata_scheme_type')

    # Funder reference #

    funder_name = zope.schema.TextLine(title=u'Funder name', required=False, min_length=3)
    funder_name.setTaggedValue('links-to', 'funder_name')
    
    funder_identifier = zope.schema.TextLine(title=u'Funder identifier', required=False)
    funder_identifier.setTaggedValue('links-to', 'funder_identifier')
    
    funder_identifier_type = zope.schema.TextLine(title=u'Funder identifier type', required=False)
    funder_identifier_type.setTaggedValue('links-to', 'funder_identifier_type')

    award_number = zope.schema.TextLine(title=u'Award number', required=False)
    award_number.setTaggedValue('links-to', 'award_number')

    award_uri = zope.schema.TextLine(title=u'Award URI', required=False)
    award_uri.setTaggedValue('links-to', 'award_uri')    

    award_title = zope.schema.TextLine(title=u'Award title', required=False)
    award_title.setTaggedValue('links-to', 'award_title')





