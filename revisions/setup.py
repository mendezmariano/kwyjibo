import os, shutil, subprocess

from zipfile import ZipFile

from .exceptions import IllegalStateException

class EnviromentSetupService():

    def setup(self, revision, target_directory):
        print("Setting up enviroment...")
        
        print(" target_directory: {target_directory}".format(target_directory = target_directory))

        print(" cleaning up working directory...")
        shutil.rmtree(target_directory, ignore_errors=True)
        
        print(" preparing delivery files...")
        zipfile = ZipFile(revision.delivery.file)
        zipfile.extractall(target_directory)
        
        print(" putting revision script alongside the code...")
        script_file = revision.delivery.assignment.script.file
        shutil.copy(script_file.path, target_directory + "/" + os.path.basename(script_file.path))
        # We must ensure the script is runnable
        process = subprocess.Popen(["chmod", "a+x", target_directory + "/" + os.path.basename(script_file.path)])
        process.wait()

        print(" checking final status...")
        print(os.listdir(target_directory))

        print("Enviroment set.")

