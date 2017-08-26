import os, shutil, subprocess

os.chroot('/var/chroot')

current_dir = os.getcwd()
script_dir = '/tmp/kwyjibo'
script = '/opt/kwyjibo/script.sh'

print("current dir: %s", current_dir)
print("script dir : %s", script_dir)

os.chdir(script_dir)
print("directory changed successfully to: " + os.getcwd())

process = subprocess.Popen([script], shell=True, stdout = subprocess.PIPE, stderr=subprocess.PIPE)


process_timer = ProcessTimeout(process, RunScriptCommand.TIME_OUT)
process_timer.start_timer()
print("Process timeout timer launched")

# finally, we must capture all results so the can be published
print("waiting for process to finish...")
exit_value = process.wait()
print("process finished with exit value %d", exit_value)

#if the result has been obtained, the is no point on keeping the timer alive
if process_timer.ran:
    print("Execution has been terminated for exceding the timeout limit.")
else:
    process_timer.cancel_timer()
    print("Process finished correctly without exceding timeout limit.")

output = process.communicate()
captured_stdout = output[0]
print("stdout captured.")
print(output)

print("excecution completed.")
