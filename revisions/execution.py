import os, psutil, signal, subprocess, sys

from threading import Timer

from .local_settings import *
from .models import ScriptResult

class ProcessTimeout:
    """
    Handler of the timer for setting a timeout to the automatic correction pid
    """


    def __init__(self, pid, timeout = REVISION_TIMEOUT):
        self.pid = pid
        self.timeout = timeout
        self.ran = False
        self.timer = Timer(self.timeout, self.kill_proc)

    def killtree(self):
        parent = psutil.Process(self.pid)
        for child in parent.children(recursive=True):
            print("killing pid %d", child.pid)
            # child.kill()
            os.kill(child.pid, signal.SIGKILL)
        print("killing pid %d", parent.pid)
        parent.kill()

    def kill_proc(self):
        print("timer expired, killing pid...")
        self.killtree()
        print("pid terminate invoked.")
        self.ran = True

    def start_timer(self):
        print("timer started")
        self.timer.start()

    def cancel_timer(self):
        print("timer cancelled")
        self.timer.cancel()


class SafeCodeRunner(object):
    """
    Service to run delivered code safely within a jail
    """
    def __init__(self):
        super(SafeCodeRunner, self).__init__()
        # self.arg = arg
        
    def execute(self, script_name):
        r, w = os.pipe() # these are file descriptors, not file objects
        pid = os.fork()
        if pid:
            return self.parent(pid, r, w)
        else:
            self.child(r, w, script_name)



    def parent(pid, r, w):
        os.close(w) # use os.close() to close a file descriptor
        r = os.fdopen(r) # turn r into a file object
        print("Fork made, setting timeout...")

        process_timer = ProcessTimeout(pid, REVISION_TIMEOUT)
        process_timer.start_timer()
        print(" ...timeout timer launched")

        txt = r.read()
        exit_value = os.waitpid(pid, 0) # make sure the child process gets cleaned up

        #if the result has been obtained, the is no point on keeping the timer alive
        if process_timer.ran:
            print("Execution has been terminated for exceding the timeout limit.")
        else:
            process_timer.cancel_timer()
            print("Process finished correctly without exceding timeout limit.")

        result = ScriptResult()
        result.exit_value = exit_value
        result.captured_stdout = txt

        return result


    def child(r, w, script_name):
        os.close(r)
        w = os.fdopen(w, 'w')

        # move to the jail
        os.chroot(JAIL_ROOT)

        current_dir = os.getcwd()
        script_dir = EXECUTION_ROOT
        script = os.join(EXECUTION_ROOT, script_name)

        process = subprocess.Popen([script], shell=True, stdout = subprocess.PIPE, stderr=subprocess.PIPE)

        exit_value = process.wait()
        output = process.communicate()
        captured_stdout = output[0]
        print(captured_stdout) # Imprime al pipe que lo comunica con el padre
        sys.exit(exit_value)
