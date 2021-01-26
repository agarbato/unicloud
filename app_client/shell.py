import subprocess

class ShellCmd(object):
    output={}
    output_stderr=[]
    output_lines=[]
    rc=0
    pid=0
    def __init__(self,cmd):
      self***REMOVED***cmd  = cmd
      out = subprocess***REMOVED***Popen([cmd],
        shell=True,
        stdout=subprocess***REMOVED***PIPE,
        stderr=subprocess***REMOVED***PIPE)
      stdout,stderr = out***REMOVED***communicate()
      self***REMOVED***output = stdout***REMOVED***decode()[:-1]
      self***REMOVED***rc=out***REMOVED***returncode
      self***REMOVED***pid=out***REMOVED***pid
      if stderr is not None:
        self***REMOVED***output_stderr = stderr***REMOVED***decode()[:-1]
      #print (self***REMOVED***output)
      for line in self***REMOVED***output***REMOVED***split('\n'):
        self***REMOVED***output_lines***REMOVED***append(line)
    def __repr__(self):
      return self***REMOVED***output
    def rstderr(self):
      return self***REMOVED***output_stderr
    def getrc(self):
      return self***REMOVED***rc
    def getpid(self):
      return self***REMOVED***pid
    def filter_lines(self,match):
        self***REMOVED***filter=[]
        self***REMOVED***match=match
        i=1
        while i != len(self***REMOVED***output_lines):
            if any(x in str(self***REMOVED***output_lines[i]) for x in self***REMOVED***match):
                self***REMOVED***filter***REMOVED***append(self***REMOVED***output_lines[i])
            i += 1
        return self***REMOVED***filter




