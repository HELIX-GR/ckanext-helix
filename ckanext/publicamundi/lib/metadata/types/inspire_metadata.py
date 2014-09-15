from lxml import etree
from owslib.iso import MD_Metadata
import zope.interface
import zope.schema
import os
import StringIO

from zope.schema.vocabulary import SimpleVocabulary
from ckanext.publicamundi.lib.metadata.base import Object
from ckanext.publicamundi.lib.metadata.schemata.inspire_metadata import \
    IThesaurusTerms, IThesaurus
from ckanext.publicamundi.lib.metadata.schemata.inspire_metadata import \
    IInspireMetadata
from ckanext.publicamundi.lib.metadata.types import object_null_adapter
from ckanext.publicamundi.lib.metadata.types.common import *
from ckanext.publicamundi.lib.metadata.vocabularies import inspire_vocabularies
from ckanext.publicamundi.lib.metadata import xml_serializers
from ckanext.publicamundi.lib.metadata.xml_serializers import object_xml_serialize_adapter

class Thesaurus(Object):
    zope.interface.implements(IThesaurus)

    # Interface IThesaurus

    title = None
    reference_date = None
    date_type = None
    name = None
    version = None

    @property
    def vocabulary(self):
        spec = inspire_vocabularies.get_by_name(self.name)
        return spec.get('vocabulary') if spec else None

    # Factory for Thesaurus

    @classmethod
    def make(cls, name):
        '''Create a new Thesaurus instance from it's machine-name name.
        '''
        spec = inspire_vocabularies.get_by_name(name)
        if spec:
            kwargs = {
               'title': spec.get('title'),
               'name': spec.get('name'),
               'reference_date': spec.get('reference_date'),
               'version' : spec.get('version'),
               'date_type': spec.get('date_type'),
            }
            return cls(**kwargs)
        else:
            raise ValueError(
                'Cannot find an INSPIRE thesaurus named "%s"' %(name))

@object_null_adapter(IThesaurusTerms)
class ThesaurusTerms(Object):
    zope.interface.implements(IThesaurusTerms)

    thesaurus = Thesaurus
    terms = list

@object_null_adapter(IInspireMetadata)
class InspireMetadata(Object):
    zope.interface.implements(IInspireMetadata)

    contact = list
    datestamp = None
    languagecode = None
    title = None
    identifier = list
    abstract = None
    locator = list
    resource_language = list
    topic_category = list
    keywords = list
    bounding_box = list
    temporal_extent = list
    creation_date = None
    publication_date = None
    revision_date = None
    lineage = None
    denominator = list
    spatial_resolution = list
    conformity = list
    access_constraints = list
    limitations = list
    responsible_party = list

# XML serialization

@object_xml_serialize_adapter(IInspireMetadata)
class InspireMetadataXmlSerializer(xml_serializers.BaseObjectSerializer):

    def to_xsd(self, wrap_into_schema=False, type_prefix='', annotate=False):
        '''Return the XSD document as an etree Element.
        '''

        # Note We do not support providing parts of it 
        assert wrap_into_schema
        
        here = os.path.dirname(__file__)
        xsd_file = os.path.join(here, 'xsd/isotc211.org-2005/gmd/metadataEntity.xsd')
        
        xsd = None
        with open(xsd_file, 'r') as fp:
            xsd = etree.fromstring(fp.read())
        return xsd

    def dumps(self, o=None):
        '''Dump object (instance of InspireMetadata) o as an INSPIRE-complant XML 
        document.
        '''

        import ckan.plugins as p

        if o is None:
            o = self.obj

        return p.toolkit.render('package/inspire_iso.xml', extra_vars={ 'data': o })

    def to_xml(self, o=None, nsmap=None):
        '''Build and return an etree Element to serialize an object (instance of
        InspireMetadata) o.

        Here, in contrast to what base XML serializer does, we build the etree by
        parsing the XML string (generated by a Jinja2 template).
        '''

        s = self.dumps(o)
        e = etree.fromstring(s)
        return e

    def from_xml(self, e):
        '''Build and return an InspireMetadata object serialized as an etree
        Element e.
        '''

        def to_date(string):
            if isinstance(string, str):
                return datetime.datetime.strptime(string,'%Y-%m-%d').date()
            else:
                return None

        def to_resp_party(alist):
            result = []
            for it in alist:
                result.append(ResponsibleParty(
                    organization = unicode(it.organization),
                    email = [unicode(it.email)],
                    role = it.role))
            return result

        md = MD_Metadata(e)

        datestamp = to_date(md.datestamp)
        id_list = []
        for it in md.identification.uricode:
            id_list.append(unicode(it))

        url_list = []
        for it in md.distribution.online:
            url_list.append(it.url)

        keywords_list = []
        for it in md.identification.keywords:
            thes_title = it['thesaurus']['title']
            if thes_title is not None:
                thes_split = thes_title.split(',')
                # TODO thes_split[1] (=version) can be used in a get_by_title_and_version() 
                # to enforce a specific thesaurus version.
                thes_title = thes_split[0]
                if inspire_vocabularies.get_by_title(thes_title):
                    thes = Thesaurus.make(inspire_vocabularies.munge('Keywords-' + thes_title)),
                    kw = ThesaurusTerms(thesaurus=thes, terms=it['keywords'])
                    keywords_list.append(kw)

        if md.identification.temporalextent_start or md.identification.temporalextent_end:
            temporal_extent = [TemporalExtent(
                start = to_date(md.identification.temporalextent_start),
                end = to_date(md.identification.temporalextent_end))]
        creation_date = None
        publication_date = None
        revision_date = None

        for it in md.identification.date:
            if it.type == 'creation':
                creation_date = to_date(it.date)
            elif it.type == 'publication':
                publication_date = to_date(it.date)
            elif it.type == 'revision':
                revision_date = to_date(it.date)

        #if not creation_date:
        #    raise Exception('creation date not present','')
        #elif not publication_date:
        #    raise Exception('publication date not present','')
        #elif not revision_date:
        #    raise Exception('revision date not present','')

        denom_list = []
        for it in md.identification.denominators:
            try:
                parsed_int = int(it)
                denom_list.append(parsed_int)
            except:
                print 'Cannot parse denominator'

        #denom_list = md.identification.denominators

        spatial_list = []

        if len(md.identification.distance) != len(md.identification.uom):
            raise Exception('unequal list lengths distance,uom','%s %s' % (md.identification.distance,md.identification.uom))
        else:
            for i in range(0,len(md.identification.distance)):
                spatial_list.append(SpatialResolution(
                    distance = md.identification.distance[i],
                    uom = md.identification.uom[i]))

        conf_list = []

        if len(md.dataquality.conformancedate) != len(md.dataquality.conformancedatetype):
            raise Exception('unequal list lengths conformance date,conformancedatetype','!')
        else:
            if md.dataquality.conformancedegree:
                for i in range(0,len(md.dataquality.conformancedate)):
                    if md.dataquality.conformancetitle[i]:
                        conf_list.append(Conformity(
                        title = unicode(md.dataquality.conformancetitle[i]),
                        date = to_date(md.dataquality.conformancedate[i]),
                        date_type = md.dataquality.conformancedatetype[i],
                        degree = md.dataquality.conformancedegree[i]))
                    else:
                        conf_list.append(Conformance(
                            date = to_datemd.dataquality.conformancedate[i]),
                            date_type = md.dataquality.conformancedatetype[i],
                            degree = md.dataquality.conformancedegree[i])
        limit_list = []
        for it in md.identification.uselimitation:
                limit_list.append(unicode(it))
        constr_list = []
        for it in md.identification.otherconstraints:
                constr_list.append(unicode(it))

        obj = InspireMetadata()

        obj.contact = to_resp_party(md.contact)
        obj.datestamp = datestamp
        obj.languagecode = md.languagecode
        obj.title = unicode(md.identification.title)
        obj.abstract = unicode(md.identification.abstract)
        obj.identifier = id_list
        obj.locator = url_list
        obj.resource_language = md.identification.resourcelanguage
        obj.topic_category = md.identification.topiccategory
        obj.keywords = keywords_list
        obj.bounding_box = [GeographicBoundingBox(
            nblat = float(md.identification.extent.boundingBox.maxy),
            sblat = float(md.identification.extent.boundingBox.miny),
            eblng = float(md.identification.extent.boundingBox.maxx),
            wblng = float(md.identification.extent.boundingBox.minx))]
        
        if md.identification.temporalextent_start:
            obj.temporal_extent = temporal_extent
        obj.creation_date = creation_date
        obj.publication_date = publication_date
        obj.revision_date = revision_date
        obj.lineage = unicode(md.dataquality.lineage)
        obj.denominator = denom_list
        obj.spatial_resolution = spatial_list
        obj.conformity = conf_list
        obj.access_constraints = limit_list
        obj.limitations = constr_list
        obj.responsible_party = to_resp_party(md.identification.contact)

        return obj
