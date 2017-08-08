'''
Created on 30/01/2013

@author: martin
'''
import os
from django.conf import settings

# Deprecated
class Managepath(object):
    
    _INSTANCE = None
    
    def __init__(self):
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        self.base_proyect_path = base_path + "/"
        self.daemon_path = base_path + "/daemon/"
        self.web_path = base_path + "/web/"
        self.model_path = base_path + "/web/seal/"
        
        self.workspace_file_path = settings.WORKSPACE_PATH
        self.delivery_file_path = settings.DELIVERY_FILE_PATH
        self.practice_file_path = settings.PRACTICE_FILE_PATH
        self.script_file_path = settings.SCRIPT_FILE_PATH
        
        self.temporary_files_path = "/tmp/"

    
    def get_daemon_path(self):
        return self.daemon_path
    
    def get_web_path(self):
        return self.web_path
    
    def get_model_path(self):
        return self.model_path
    
    def get_temporary_files_path(self):
        return self.temporary_files_path
    
def get_instance():
    if not Managepath._INSTANCE:
        Managepath._INSTANCE = Managepath()
    return Managepath._INSTANCE

