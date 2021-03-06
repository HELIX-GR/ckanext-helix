import logging
import zope.interface
import zope.schema
import zope.schema.interfaces
import itertools
from collections import Counter
from operator import attrgetter, itemgetter

import pylons
import ckan.plugins.toolkit as toolkit
from ckan.lib.navl.dictization_functions import missing, StopOnError, Invalid

from ckanext.helix.lib import logger
from ckanext.helix.lib import dictization
import ckanext.helix.lib.metadata as ext_metadata

_ = toolkit._
aslist = toolkit.aslist
asbool = toolkit.asbool


#
# Validators/Converters for package
#

def is_dataset_type(value, context):
    if not value in ext_metadata.dataset_types:
        raise Invalid('Unknown dataset-type (%s)' %(value))
    return value

def preprocess_dataset_for_read(key, data, errors, context):
    #logger.debug('PREPROCESS DATA READ IS [%s]\n \n', data )
    assert key[0] == '__before', \
        'This validator can only be invoked in the __before stage'
    
    def debug(msg):
        logger.debug('Pre-processing dataset for reading: %s' %(msg))
    
    debug('context=%r' %(context.keys()))
    
    #raise Breakpoint('preprocess read')
    pass

def postprocess_dataset_for_read(key, data, errors, context):
    #logger.debug('POSTPROCESS DATA READ IS [%s]\n\n', data )
    assert key[0] == '__after', (
        'This validator can only be invoked in the __after stage')
    
    def debug(msg):
        logger.debug('Post-processing dataset for reading: %s' %(msg))
    
    debug('context=%r' %(context.keys()))
    
    # Note This is not always supplied (?). I suppose this is due to the
    # fact that package dicts are cached (on their revision-id).
    requested_with_api = context.has_key('api_version')
    
    # Prepare computed fields, reorganize structure etc.
    #data[('baz_view',)] = u'I am a read-only Baz'
    #data[('baz_view',)] = { 'a': 99, 'b': { 'measurements': [ 1, 5, 5, 12 ] } }

    #raise Breakpoint('postprocess read')
    pass

def postprocess_dataset_for_edit(key, data, errors, context):

    #logger.debug('\nPOSTPROCESS EDIT START IS %s\n', data )  
    assert key[0] == '__after', (
        'This validator can only be invoked in the __after stage')
     
    def debug(msg):
        logger.debug('Post-processing dataset for editing: %s' %(msg))
    
    # The state we are moving to
    state = data.get(('state',), '') 
    
    # The previous state (if exists)
    pkg = context.get('package')
    prev_state = pkg.state if pkg else ''

    requested_with_api = 'api_version' in context
    is_new = not pkg

    #if is_new and not requested_with_api:
    #    return # only core metadata are expected

    key_prefix = dtype = data[('dataset_type',)]
    if not dtype in ext_metadata.dataset_types:
        raise Invalid('Unknown dataset-type: %s' %(dtype))
    
    #logger.debug('DATA IS [%s]' % ', '.join(map(str, data)) ) 
    # 1. Build metadata object

    cls = ext_metadata.class_for_metadata(dtype)
    md = cls.from_converted_data(data, for_edit=True)


    if not md:
        return # failed to create (in resources form ?)

    data[(key_prefix,)] = md
    
    #logger.debug('MD IS %s', md )
    # 2. Validate as an object

    if not 'skip_validation' in context:
        validation_errors = md.validate(dictize_errors=True)
        #logger.debug("\n\n VALIDATION ERRORS IS: %s ,errors is %s, type of errors is %s \n\n", validation_errors, errors, type(validation_errors) )
        #errors[('datacite.related_publication',)] = 'Missing Value'
        #logger.debug("\n\n validation 4 is:: %s type is %s \n\n", validation_errors['creator'],  type(validation_errors['creator']), )
        # Map validation_errors to errors
        for key, value in validation_errors.items():
            #logger.debug("\n\n validation is %s, type is %s, value is %s, type is %s\n", key, type(key), value, type(value) )
            #key = "('datacite.{}',)".format(key)
            if not isinstance(value, list) :
                # fix key-value for classes like Creator (contains multiple fields)
                k = key + '.' + next(iter(value))
                # make key compatible with errors dict (tuple)
                k = tuple([str.encode("('datacite.%s',)" % k)])
                v =  value[next(iter(value))]
                #logger.debug("\n\n key[0] is %s, value[0] is %s \n", k, v)
                if v[0][0] == 'R':       #RequiredMissing
                    errors[k] = u'Missing value'
            else:
                # make key compatible with errors dict (tuple)
                #key = tuple([str.encode("('datacite.%s',)" % key)])
                # fix error message displayed
                #logger.debug("\n\n value in validation is value[0] %s, type is %s, key is %s\n", value[0], type(value[0]), key )
                if value[0][:8] == 'Required':
                    key = tuple([str.encode("('datacite.%s',)" % key)])
                    errors[key] = u'Missing value'
                elif value[0][:7] == 'related':
                    #remove duplicate error (for wrong value)
                    key_to_remove = tuple([str.encode('datacite.%s' % key)])
                    key = tuple([str.encode("('datacite.%s',)" % key)])
                    errors[key] = u'Invalid DOI value'  
                    errors[key_to_remove] =  []

        #for k, v in errors.items():
        #    logger.debug("K: %s,type: %s v: %s,type %s ", k,type(k), v, type(v))      
        # Fixme Map validation_errors to errors  ! ! ! ! 
        #assert not validation_errors
   
    # 3. Convert fields to extras
    
    #logger.debug("\n MD IS: %s \n", md )

    # add datacite fields after ckan extras
    index = 7
    for k, v in md.to_extras():
            #logger.debug("\n Key is: %s, value is %s \n", k, v )
            data[('extras', index, 'key')] = k
            data[('extras', index, 'value')] = v
            index = index + 1 
    
    # 4. Compute next state
    
    if 'skip_validation' in context:
        state = data[('state',)] = 'invalid' 
        #data[('private',)] = True
    
    #add extra value manually
    #data['extras', 6, 'key'] = 'datacite.funder'
    #data['extras', 6, 'value'] = 'NIK'

    if not state:
        if prev_state == 'invalid':
            state = data[('state',)] = 'active'
   
    #logger.debug('\nPOSTPROCESS EDIT END Data IS %s', data )
    return

def preprocess_dataset_for_edit(key, data, errors, context):
    #logger.debug('\nPREPROCESS DATA EDIT START IS [%s]', data)
    assert key[0] == '__before', \
        'This validator can only be invoked in the __before stage'
    
    def debug(msg):
        logger.debug('Pre-processing dataset for editing: %s' %(msg))
    
    received_data = { k:v for k,v in data.iteritems() if not (v is missing) }
    unexpected_data = received_data.get(('__extras',), {})
    
    #debug('Received data: %r' %(received_data))
    #debug('Received (but unexpected) data: %r' %(unexpected_data))
    
    # Figure out if a nested dict is supplied (instead of a flat one).
    
    # Note This "nested" input format is intended to be used by the action api,
    # as it is far more natural to the JSON format. Still, this format option is
    # not restricted to api requests (it is possible to be used even by form-based
    # requests).
   
    key_prefix = dtype = received_data.get(('dataset_type',))
    r = unexpected_data.get(dtype) if dtype else None
   
    if isinstance(r, dict) and (dtype in ext_metadata.dataset_types):
        # Looks like a nested dict keyed at key_prefix
        debug('Trying to flatten input at %s' %(key_prefix))
        if any([ k[0].startswith(key_prefix) for k in received_data ]):
            raise Invalid('Not supported: Found both nested/flat dicts')
        # Convert to expected flat fields
        key_converter = lambda k: '.'.join([key_prefix] + map(str, k))
        r = dictization.flatten(r, key_converter)
        data.update({ (k,): v for k, v in r.iteritems() })

    #raise Breakpoint('preprocess_dataset_for_edit')

    #logger.debug('PREPROCESS DATA END IS [%s]', data)  
    pass  

def get_field_edit_processor(field):
    '''Get a field-level edit converter wrapped as a CKAN converter function.
    
    This wrapper is intended to be used for a create/update schema converter,
    and has to carry out the following basic tasks:
        - convert input from a web request
        - validate at field level
        - convert to a string form and store at data[key] 
    '''

    def convert(key, data, errors, context):
        value = data.get(key)
        #logger.debug('Processing field %s for editing (%r)', key[0], value)
         
        ser = ext_metadata.serializer_for_field(field)

        # Not supposed to handle missing inputs here
        
        assert not value is missing
        
        # Convert from input/db or initialize to defaults
        
        if not value:
            # Determine default value and initialize   
            if field.default is not None:
                value = field.default
            elif field.defaultFactory is not None:
                value = field.defaultFactory()
        else:
            # Convert from input or db  
            if ser and isinstance(value, basestring):
                try:
                    value = ser.loads(value)
                except Exception as ex:
                    raise Invalid(u'Invalid input (%s)' % (ex.message))
        
        # Ignore empty values (act exactly as the `ignore_empty` validator).
        # Note If a field is marked as required, the check is postponed until
        # the dataset is validated at dataset level.

        if not value:
            data.pop(key)
            raise StopOnError

        # Validate
                
        if not 'skip_validation' in context:
            try: 
                # Invoke the zope.schema validator
                field.validate(value)
            except zope.schema.ValidationError as ex:
                # Map this exception to the one expected by CKAN
                raise Invalid(u'Invalid (%s)' % (type(ex).__name__))

        # Convert to a properly formatted string (for db storage)

        if ser:
            value = ser.dumps(value)
        
        data[key] = value

        return

    return convert

def get_field_read_processor(field):
    '''Get a field-level converter wrapped as a CKAN converter function.
    '''

    def convert(key, data, errors, context):
        value = data.get(key)
        #logger.debug('Processing field %s for reading (%r)', key[0], value)
        
        assert not value is missing
        assert isinstance(value, basestring)
        
        if not value:
            logger.warn('Read empty value for field %s' % (key[0]))

        # noop

        return

    return convert

def guess_language(key, data, errors, context):
    assert key[0] == '__after', (
        'This converter can only be invoked in the __after stage')
    
    lang = None
    extras_list = data[('extras',)]
   
    # Check if language present in extras
    
    lang_item = None
    try:
        i = map(itemgetter('key'), extras_list).index('language')
    except:
        pass
    else:
        lang_item = extras_list[i]
    
    # Try to deduce from metadata
    # Note At 1st stage of create form, md will be not available
    key_prefix = dtype = data[('dataset_type',)]
    md = data.get((key_prefix,))
    if md:
        lang = md.deduce_fields('language').get('language')
        
    # If not deduced and not present, guess is active language
    if not lang and not lang_item:
        req_lang = pylons.i18n.get_lang()
        lang = req_lang[0] if req_lang else 'en'
    
    # Create/Update extras item with our guessed value
    if lang:
        if not lang_item:
            extras_list.append({'key': 'language', 'value': lang})
        else:
            lang_item['value'] = lang
    else:
        assert lang_item
    return

#
# Validators/Converters for resources
#

def guess_resource_type_if_empty(key, data, errors, context):
    '''Guess the resource-type from the the rest of the resource dict.
    
    Try to guess the resource-type from the format (which should be always
    present and non-empty). We shall not assume that the format is converted
    to its canonical form since we dont know the order at which these field
    validators will run.
    '''
    
    value = data[key]
    if value:
        return 
    
    key0, pos, key2 = key
    assert key0 == 'resources' and key2 == 'resource_type'
    
    resource_format = data[('resources', pos, 'format')]
    resource_format = resource_format.encode('ascii').lower()
    
    api_formats = aslist(
        pylons.config.get('ckanext.helix.api_resource_formats'))
    if resource_format in api_formats:
        value = 'api'
    else:
        value = 'file'

    data[key] = value
    return

#
# Helpers
#

def _must_validate(context, data):
    '''Indicate whether an object (or a particular field of it) should be validated
    under the given context.
    '''
    return not (
        ('skip_validation' in context) or 
        (data.get(('state',), '') == 'invalid'))

