"""

@author: anibal

"""
from threading import Timer
import os, psutil, signal

class ProcessTimeout:
    """
    Handler of the timer for setting a timeout to the automatic correction pid
    """


    def __init__(self, pid, timeout):
        self.pid = pid
        self.timeout = timeout
        self.ran = False
        self.timer = Timer(self.timeout, self.kill_proc)

    def killtree(self):
        parent = psutil.Process(self.pid)
        for child in parent.get_children(recursive=True):
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
