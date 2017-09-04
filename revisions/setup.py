import os, shutil, subprocess

from zipfile import ZipFile

from .exceptions import IllegalStateException

class EnviromentSetupService():

    def setup(self, revision, target_directory):
        print("Setting up enviroment...")

        print(" cleaning up working directory...")
        shutil.rmtree(target_directory, ignore_errors=True)
        
        print(" preparing delivery files...")
        os.mkdir(target_directory)
        zipfile = ZipFile(zip_file)
        zipfile.extractall(target_directory)
        
        print(" putting revision script alongside the code...")
        shutil.copy(revision.delivery.assignment.script, target_directory + "/" + os.path.basename(revision.delivery.assignment.script))
        # We must ensure the script is runnable
        process = subprocess.Popen(["chmod", "a+x", target_directory + "/" + os.path.basename(revision.delivery.assignment.script)])
        process.wait()

        print("Enviroment set.")
        

