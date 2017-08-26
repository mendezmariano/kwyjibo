"""

@author: anibal

"""
from threading import Timer
import os, psutil, signal

class ProcessTimeout:
    """
    Handler of the timer for setting a timeout to the automatic correction process
    """


    def __init__(self, process, timeout):
        self.process = process
        self.timeout = timeout
        self.ran = False
        self.timer = Timer(self.timeout, self.kill_proc)

    def killtree(self):
        parent = psutil.Process(self.process.pid)
        for child in parent.get_children(recursive=True):
            print("killing process %d", child.pid)
            # child.kill()
            os.kill(child.pid, signal.SIGKILL)
        print("killing process %d", parent.pid)
        parent.kill()

    def kill_proc(self):
        print("timer expired, killing process...")
        self.killtree()
        print("process terminate invoked.")
        self.ran = True

    def start_timer(self):
        print("timer started")
        self.timer.start()

    def cancel_timer(self):
        print("timer cancelled")
        self.timer.cancel()
