import zope.interface
import zope.schema
import copy
import json
import datetime

from ckanext.helix.lib.metadata.types import *
from ckanext.helix.tests.helpers import assert_faulty_keys
from ckanext.helix.tests import fixtures

#
# INSPIRE (faulty) fixtures
#

# Missing required title, abstract
insp11 = InspireMetadata(
        contact = [
            ResponsibleParty(organization=u"Org", email=u"email@asd.gr", role="pointOfContact")],
        datestamp = datetime.date.today(),
        languagecode = "gre",
        identifier = "12314213123",
        locator = ["http://www.google.com"],
        resource_language = ["gre"],
        topic_category = ["biota"],
        keywords = {
            'keywords-gemet-concepts': ThesaurusTerms(
                terms=["atmosphere"],
                thesaurus=fixtures.thesaurus_gemet_concepts
            ),
            'keywords-gemet-inspire-themes': ThesaurusTerms(
                terms=["land-cover", "land-use"],
                thesaurus=fixtures.thesaurus_gemet_inspire_data_themes,
            ),
            },
        bounding_box = [
            GeographicBoundingBox(nblat=0.0, sblat=0.0, eblng=0.0, wblng=0.0)],
        temporal_extent = [
            TemporalExtent(start=datetime.date(2012,1,1), end=datetime.date(2013,1,1))],
        creation_date = datetime.date(2012,1,1),
        publication_date = datetime.date(2013,1,1),
        revision_date = datetime.date(2014,1,1),
        lineage = u"lineaage",
        spatial_resolution = [SpatialResolution(distance=1, uom=u"meters")],
        conformity = [
            Conformity(title=u"specifications blabla", date=datetime.date.today(), date_type="creation", degree="conformant")],
        access_constraints = [u"lalala1", u"lalala2"],
        limitations = [u"limit1", u"limit2"],
        responsible_party = [
            ResponsibleParty(organization=u"Org", email=u"email@asd.gr", role="pointOfContact"), 
            ResponsibleParty(organization=u"Org2", email=u"email2@asd.gr", role="pointOfContact")])

# Missing required topic_category, responsible_party
insp12 = InspireMetadata(
    contact = [
        ResponsibleParty(organization=u"Org", email=u"email@asd.gr", role="pointOfContact")],
    datestamp = datetime.date.today(),
    languagecode = "gre",
    title = u"Title",
    identifier = "abc123",
    abstract = u"abstracttttttt",
    locator = ["http://www.google.com", "http://helix.eu"],
    resource_language = ["gre"],
    keywords = {
            'keywords-gemet-concepts': ThesaurusTerms(
                terms=["atmosphere"],
                thesaurus=fixtures.thesaurus_gemet_concepts
            ),
            'keywords-gemet-inspire-themes': ThesaurusTerms(
                terms=["land-cover", "land-use"],
                thesaurus=fixtures.thesaurus_gemet_inspire_data_themes,
            ),
        },
    bounding_box = [
        GeographicBoundingBox(nblat=0.0, sblat=0.0, wblng=0.0, eblng=0.0)],
    temporal_extent = [
        TemporalExtent(start = datetime.date(2012,1,1), end = datetime.date(2014,1,1))],
    creation_date = datetime.date(2012,1,1),
    publication_date = datetime.date(2013,1,1),
    revision_date = datetime.date(2014,1,1),
    lineage = u"lineaage",
    spatial_resolution = [SpatialResolution(distance=5, uom = u"meters")],
    conformity = [
        Conformity(title=u"specifications blabla", date=datetime.date.today(), date_type="creation", degree="conformant")],
    access_constraints = [u"lalala1", u"lalala2"],
    limitations = [u"limit1", u"limit2"])

# Creation, publication, revision wrong date ranges & temporal extent start, end (invariant)
insp2 = InspireMetadata(
    contact = [ResponsibleParty(organization=u"Org", email=u"email@asd.gr", role="pointOfContact")],
    datestamp = datetime.date.today(),
    languagecode = "gre",
    title = u"Title",
    identifier = "abc123",
    abstract = u"abstracttttttt",
    locator = ["http://www.google.com"],
    resource_language = ["gre"],
    topic_category = ["biota"],
    keywords = {
            'keywords-gemet-concepts': ThesaurusTerms(
                terms=["atmosphere"],
                thesaurus=fixtures.thesaurus_gemet_concepts
            ),
            'keywords-gemet-inspire-themes': ThesaurusTerms(
                terms=["land-cover", "land-use"],
                thesaurus=fixtures.thesaurus_gemet_inspire_data_themes,
            ),
        },
    bounding_box = [
        GeographicBoundingBox(nblat=0.0, sblat=0.0, eblng=0.0, wblng=0.0)],
    temporal_extent = [
        TemporalExtent(start=datetime.date(2012,1,1), end=datetime.date(2013,1,1))],
    creation_date = datetime.date(2014,1,1),
    publication_date = datetime.date(2013,1,1),
    revision_date = datetime.date(2012,1,1),
    lineage = u"lineaage",
    spatial_resolution = [
        SpatialResolution(distance=5, uom=u"meters")],
    conformity = [
        Conformity(title=u"specifications blabla", date=datetime.date.today(), date_type="creation", degree="conformant")],
    access_constraints = [u"lalala1", u"lalala2"],
    limitations = [u"limit1", u"limit2"],
    responsible_party = [
        ResponsibleParty(organization=u"Org", email=u"email@asd.gr", role="pointOfContact")])

# Min_length of contact, locator smaller than one 
insp3 = InspireMetadata(
    contact = [],
    datestamp = datetime.date.today(),
    languagecode = "gre",
    title = u"Title",
    identifier = "abc123",
    abstract = u"abstracttttttt",
    locator = [],
    resource_language = ["gre"],
    topic_category = ["biota"],
    keywords = {
            'keywords-gemet-concepts': ThesaurusTerms(
                terms=["atmosphere"],
                thesaurus=fixtures.thesaurus_gemet_concepts
            ),
            'keywords-gemet-inspire-themes': ThesaurusTerms(
                terms=["land-cover", "land-use"],
                thesaurus=fixtures.thesaurus_gemet_inspire_data_themes,
            ),
        },
    bounding_box = [
        GeographicBoundingBox(nblat=0.0, sblat=0.0, wblng=0.0, eblng=0.0)],
    temporal_extent = [
        TemporalExtent(start=datetime.date(2012,1,1), end=datetime.date(2014,1,1))],
    creation_date = datetime.date(2012,1,1),
    publication_date = datetime.date(2013,1,1),
    revision_date = datetime.date(2014,1,1),
    lineage = u"lineaage",
    spatial_resolution = [
        SpatialResolution(distance=5, uom=u"meters")],
    conformity = [
        Conformity(title=u"specifications blabla", date=datetime.date.today(), date_type="creation", degree="conformant")],
    access_constraints = [u"lalala1", u"lalala2"],
    limitations = [u"limit1", u"limit2"],
    responsible_party = [
        ResponsibleParty(organization=u"Org", email=u"email@asd.gr", role="pointOfContact"), 
        ResponsibleParty(organization=u"Org2", email=u"email2@asd.gr", role="pointOfContact")])

# Temporal-Extent start field (required field in ITemporalExtent) missing
insp4 = InspireMetadata(
    contact = [
        ResponsibleParty(organization=u"Org", email=u"email@asd.gr", role="pointOfContact")],
    datestamp = datetime.date.today(),
    languagecode = "gre",
    title = u"Title",
    identifier = "abc123",
    abstract = u"abstracttttttt",
    locator = ["http://www.google.com", "http://helix.eu"],
    resource_language = ["gre"],
    topic_category = ["biota"],
    keywords = {
            'keywords-gemet-concepts': ThesaurusTerms(
                terms=["atmosphere"],
                thesaurus=fixtures.thesaurus_gemet_concepts
            ),
            'keywords-gemet-inspire-themes': ThesaurusTerms(
                terms=["land-cover", "land-use"],
                thesaurus=fixtures.thesaurus_gemet_inspire_data_themes,
            ),
        },
    bounding_box = [
        GeographicBoundingBox(nblat=0.0, sblat=0.0, wblng=0.0, eblng=0.0)],
    temporal_extent = [
        TemporalExtent(end=datetime.date(2014,1,1))],
    creation_date = datetime.date(2012,1,1),
    publication_date = datetime.date(2013,1,1),
    revision_date = datetime.date(2014,1,1),
    lineage = u"lineaage",
    spatial_resolution = [
        SpatialResolution(distance=5, uom=u"meters")],
    conformity = [
        Conformity(title=u"specifications blabla", date=datetime.date.today(), date_type="creation", degree="conformant")],
    access_constraints = [u"lalala1" ,u"lalala2"],
    limitations = [u"limit1", u"limit2"],
    responsible_party = [
        ResponsibleParty(organization=u"Org", email=u"email@asd.gr", role="pointOfContact"), 
        ResponsibleParty(organization=u"Org2", email=u"email2@asd.gr", role="pointOfContact")])

# Temporal-Extent (not required field) missing 
insp5 = copy.deepcopy(insp4)
insp5.temporal_extent = None

# Temporal-Extent wrong date range
insp6 = copy.deepcopy(insp4)
insp6.temporal_extent = [
    TemporalExtent(start=datetime.date(2013,1,1), end=datetime.date(2012,1,1))],

# Keywords include unexpected terms
insp7 = copy.deepcopy(insp4)
insp7.temporal_extent = None
insp7.keywords = {
            'keywords-gemet-concepts': ThesaurusTerms(
                terms=["analysis", "foo"], # Term "foo" does not exist
                thesaurus=fixtures.thesaurus_gemet_concepts
            ),
            'keywords-gemet-inspire-themes': ThesaurusTerms(
                terms=["buildings", "addresses"],
                thesaurus=fixtures.thesaurus_gemet_inspire_data_themes,
            ),
        },


# Wrong Thesaurus Name Provided
insp8 = copy.deepcopy(fixtures.inspire1)
insp8.keywords = {
            'keywords-gemet-inspire-themes': ThesaurusTerms(
                terms=["buildings", "addresses"],
                thesaurus= Thesaurus(
                    title = u'GEMET INSPIRE Themes',
                    name = 'keywords-gemet-wrong-inspire-themes',
                    reference_date = datetime.date(2014, 1, 1),
                    version = 1.0,
                    date_type = 'creation'
                    )
                ),
            }

# Missing keyword terms from INSPIRE Data themes 
insp9 = copy.deepcopy(fixtures.inspire1)
insp9.keywords = {
        'keywords-gemet-themes': ThesaurusTerms(
            terms=["air", "agriculture", "climate"],
            thesaurus=fixtures.thesaurus_gemet_themes
        ),
        }

# Keywords completely empty
insp91 = copy.deepcopy(fixtures.inspire1)
insp91.keywords = {}

# Free keywords originating vocabulary dates not set
insp92 = copy.deepcopy(fixtures.inspire1)
insp92.free_keywords = [
    FreeKeyword(value="hello-world", originating_vocabulary=u"Vocabulary"),
    FreeKeyword(value="goodbye")]

# Some free keywords are present
insp93 = copy.deepcopy(fixtures.inspire1)
insp93.free_keywords = [
        FreeKeyword(value="lala", originating_vocabulary=u"HelloWorld", reference_date=datetime.date.today(), date_type="creation"),
        FreeKeyword(value="goodbye")]

#
# Tests
#

def test_insp11():
    ''' Missing required title, abstract'''
    assert_faulty_keys(insp11, 
        expected_keys=set(['title', 'abstract']))

def test_insp12():
    '''Missing required topic_category, responsible_party'''
    assert_faulty_keys(insp12,
        expected_keys=set(['topic_category', 'responsible_party']))

def test_insp2():
    ''' Creation, publication, revision date ranges not valid'''
    assert_faulty_keys(insp2,
        expected_keys = set(['__after']), 
        expected_invariants = ["later than publication date", "later than last revision date"]
    )

def test_insp3():
    ''' Min_length of contact, locator smaller than min_length'''
    assert_faulty_keys(insp3,
        expected_keys=set(['contact', 'locator']))

def test_insp4():
    '''Temporal-Extent start field (required field in ITemporalExtent) missing'''
    assert_faulty_keys(insp4,
        expected_keys=set(['temporal_extent']))

def test_insp5():
    '''Temporal-Extent (not required field) missing'''
    assert_faulty_keys(insp5)

def test_insp6():
    '''Temporal-Extent wrong date range'''
    assert_faulty_keys(insp6,
        expected_keys=set(['temporal_extent']), expected_invariants=["later than end date"])

def test_insp7():
    '''Unexpected keywords (not found in vocabularies)'''
    assert_faulty_keys(insp7,
        expected_keys=set(['keywords']))

def test_insp8():
    '''Wrong Thesaurus name provided'''
    assert_faulty_keys(insp8,
        expected_keys=set(['keywords']))

def test_insp9():
    '''Missing Keywords from INSPIRE Data themes'''
    assert_faulty_keys(insp9,
        expected_keys=set(['__after']))

def test_insp91():
    '''Completely empty keywords'''
    assert_faulty_keys(insp91,
        expected_keys=set(['keywords']))

def test_insp92():
    ''' Free keywords originating vocabulary dates not set'''
    assert_faulty_keys(insp92,
        expected_keys=set(['free_keywords']))

def test_insp93():
    ''' Some free keywords are present'''
    assert_faulty_keys(insp93)

def test_fixtures_inspire1():
    '''Everything should be ok'''
    assert_faulty_keys(fixtures.inspire1)


if __name__ == '__main__':
    #test_insp11()
    #test_insp12()
    #test_insp2()
    #test_insp3()
    #test_insp4()
    #test_insp5()
    #test_insp6()
    test_insp7()
    test_insp8()
    #test_fixtures_inspire1()
    pass

