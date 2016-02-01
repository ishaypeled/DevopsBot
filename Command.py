import subprocess, threading

class Command:
    def __init__(self, cmd):
        self.cmd = cmd
        self.res = None

    def run(self, timeout):
        def target():
            print 'Thread started'
            self.res = subprocess.check_output(self.cmd)
            print 'Thread finished'

        thread = threading.Thread(target=target)
        thread.start()
        thread.join(timeout)
        if thread.is_alive():
            print 'Terminating process'
            self.res.terminate()
            thread.join()
