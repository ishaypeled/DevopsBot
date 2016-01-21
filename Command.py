import subprocess, threading

class Command:
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None
        self.res = None

    def run(self, timeout):
        def target():
            print 'Thread started'
            self.process = subprocess.Popen(self.cmd)
            if (self.process.communicate()[0]):
                self.res=self.process.communicate()[0].strip()
            else:
                print "XXXXXXXXX"
            print 'Thread finished'

        thread = threading.Thread(target=target)
        thread.start()
        thread.join(timeout)
        if thread.is_alive():
            print 'Terminating process'
            self.process.terminate()
            thread.join()
