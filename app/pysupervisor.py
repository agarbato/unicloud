#https://stackoverflow.com/questions/11729159/use-python-xmlrpclib-with-unix-domain-sockets
#http://supervisord.org/api.html
from http.client import HTTPConnection
import socket
from xmlrpc import client


class UnixStreamHTTPConnection(HTTPConnection):
    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(self.host)


class UnixStreamTransport(client.Transport, object):
    def __init__(self, socket_path):
        self.socket_path = socket_path
        super(UnixStreamTransport, self).__init__()

    def make_connection(self, host):
        return UnixStreamHTTPConnection(self.socket_path)


def pysupervisor_get_process_state(process_name):
    proxy = client.ServerProxy('http://localhost', transport=UnixStreamTransport("/run/supervisord.sock"))
    response = proxy.supervisor.getProcessInfo(process_name)['statename']
    return response


def pysupervisor_sshd_status():
    sshd_status = pysupervisor_get_process_state("sshd")
    if sshd_status != "RUNNING":
        return False
    else:
        return True


