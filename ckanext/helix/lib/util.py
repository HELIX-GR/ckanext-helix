import random
import uuid
import string
import json
import collections
import itertools
from functools import wraps
from dictdiffer import (dot_lookup, diff as diff_dicts, patch as patch_dict)

from ckanext.helix.lib.json_encoder import JsonEncoder

import logging
log1 = logging.getLogger(__name__)

class Breakpoint(Exception):
    '''Exception used for Pylons debugging'''
    pass

def to_json(o, indent=None):
    '''Convert to JSON providing our custom encoder'''
    return json.dumps(o.dict, cls=JsonEncoder, indent=indent)

def random_name(l):
    return random.choice(string.lowercase) + \
        ''.join(random.sample(string.lowercase + string.digits, int(l)-1))

def stringify_exception(ex):
    return '%s: %s' %(type(ex).__name__, str(ex).strip())

def raise_for_stub_method():
    raise NotImplementedError('Method should be implemented in a derived class')

def quote(s):
    '''A naive routine to enclose a unicode string in double quotes'''
    return u'"' + s.replace('\\', '\\\\').replace('"', '\\"') + u'"'

def check_uuid(s):
    try:
        s = str(uuid.UUID(s))
    except:
        s = None
    return s

def find_all_duplicates(l):
    counter = collections.Counter(l)
    dups = { k:n for k,n in counter.items() if n > 1 }
    return dups

def once(f):
    f._num_calls = 0
    @wraps(f)
    def f1(*args, **kwargs):
        assert f._num_calls == 0, 'Expected to be called once'
        f._num_calls += 1
        return f(*args, **kwargs)
    return f1

def attr_setter(o, k):
    def f(v):
        setattr(o, k, v)
    return f
 
def item_setter(d, k):
    def f(v):
        d[k] = v
    return f

def const_function(val):
    '''Create a const function'''
    return itertools.repeat(val).next 

class falsy_function(object):
    '''Create a function marked as falsy'''

    def __call__(self, *args, **kwargs):
        assert False, 'This is not supposed to be called'
    
    def __repr__(self):
        return '<not-a-function>'

    def __nonzero__(self): 
        return False

not_a_function = falsy_function()

