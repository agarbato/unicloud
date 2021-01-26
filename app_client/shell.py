import subprocess

class ShellCmd(object):
    output={}
    output_stderr=[]
    output_lines=[]
    rc=0
    pid=0
    def __init__(self,cmd):
      self.cmd  = cmd
      out = subprocess.Popen([cmd],
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
      stdout,stderr = out.communicate()
      self.output = stdout.decode()[:-1]
      self.rc=out.returncode
      self.pid=out.pid
      if stderr is not None:
        self.output_stderr = stderr.decode()[:-1]
      #print (self.output)
      for line in self.output.split('\n'):
        self.output_lines.append(line)
    def __repr__(self):
      return self.output
    def rstderr(self):
      return self.output_stderr
    def getrc(self):
      return self.rc
    def getpid(self):
      return self.pid
    def filter_lines(self,match):
        self.filter=[]
        self.match=match
        i=1
        while i != len(self.output_lines):
            if any(x in str(self.output_lines[i]) for x in self.match):
                self.filter.append(self.output_lines[i])
            i += 1
        return self.filter




