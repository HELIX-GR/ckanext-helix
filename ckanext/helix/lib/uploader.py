import os
import cgi
import datetime
import logging

from pylons import config

import ckan.lib.munge as munge
import ckan.logic as logic

# Note
# We are going to reuse the file storage utility used by CKAN itself
# to store uploaded resources. However, this utility is not included
# in plugins toolkit (therefore, it could break anytime in the future).
from ckan.lib.uploader import get_storage_path, Upload, ResourceUpload, _copy_file

class MetadataUpload(Upload):
    '''Represents an uploaded file containing XML metadata.
    '''

    def __init__(self, old_filename=None):
        super(MetadataUpload, self).__init__('source-metadata', old_filename)

    def update_data_dict(self, data_dict, file_field):
        super(MetadataUpload, self).update_data_dict(data_dict, '', file_field, '')

    def get_path(self, name):
        return os.path.join(self.storage_path, name)

    def upload(self, max_size=2):
        ''' Actually upload the file.
        This should happen just before a commit but after the data has
        been validated and flushed to the db. This is so we do not store
        anything unless the request is actually good.
        max_size is size in MB maximum of the file'''

        if self.filename:
            with open(self.tmp_filepath, 'wb+') as output_file:
                try:
                    _copy_file(self.upload_file, output_file, max_size)
                except logic.ValidationError:
                    os.remove(self.tmp_filepath)
                    raise
            os.rename(self.tmp_filepath, self.filepath)
            self.clear = True

        if (self.clear and self.old_filename
                and not self.old_filename.startswith('http')):
            try:
                os.remove(self.old_filepath)
            except OSError:
                pass    
