#!/usr/bin/env python

import os, sys

from timeout import ProcessTimeout

print("I'm going to fork now - the child will write something to a pipe, and the parent will read it back")

r, w = os.pipe() # these are file descriptors, not file objects

pid = os.fork()

if pid:
    # we are the parent
    os.close(w) # use os.close() to close a file descriptor
    r = os.fdopen(r) # turn r into a file object
    print("parent: reading")

    process_timer = ProcessTimeout(pid, 10)
    process_timer.start_timer()
    print("Process timeout timer launched")

    txt = r.read()
    os.waitpid(pid, 0) # make sure the child process gets cleaned up
    
    #if the result has been obtained, the is no point on keeping the timer alive
    if process_timer.ran:
        print("Execution has been terminated for exceding the timeout limit.")
    else:
        process_timer.cancel_timer()
        print("Process finished correctly without exceding timeout limit.")


else:
    # we are the child
    os.close(r)
    w = os.fdopen(w, 'w')
    print("child: writing")
    

    import os, shutil, subprocess

    # move to the jail
    os.chroot('/var/chroot')

    current_dir = os.getcwd()
    script_dir = '/tmp/kwyjibo'
    script = '/opt/kwyjibo/script.sh'
    # os.chdir(script_dir)

    process = subprocess.Popen([script], shell=True, stdout = subprocess.PIPE, stderr=subprocess.PIPE)

    exit_value = process.wait()
    output = process.communicate()
    captured_stdout = output[0]
    print(captured_stdout)
    sys.exit(exit_value)


print("parent: got it; text =", txt)
