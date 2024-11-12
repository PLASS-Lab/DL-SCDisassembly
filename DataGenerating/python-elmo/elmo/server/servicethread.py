import threading
from .protocol import Protocol, ClosureException
import socket


class ServiceThread(threading.Thread):
    def run(self):
        self.execute()

    def execute(self):
        # Method where the service runs
        pass


class OneShotServiceThread(ServiceThread):
    def __init__(self, ip, port, clientsocket):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.clientsocket = clientsocket
        self.protocol = Protocol(clientsocket)

    def run(self):
        try:
            self.execute()
        except ClosureException:
            return
            
    def execute(self):
        # Method where the service runs
        pass


class PermanentServiceThread(ServiceThread):
    def __init__(self):
        threading.Thread.__init__(self)
        self._is_running = True

    def is_running(self):
        return self._is_running

    def stop(self):
        self._is_running = False


class ListeningThread(PermanentServiceThread):
    def __init__(self, host, port, threadclass, debug=False, **kwargs):
        super().__init__()
        self.hostname = host
        self.port = port
        self.threadclass = threadclass
        self.kwargs = kwargs
        self.debug = debug
    
    def execute(self):
        self.tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        # self.tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_ATTACH_REUSEPORT_CBPF, 1)
        self.tcpsock.bind((self.hostname, self.port))
        self.tcpsock.listen(5)
        
        if self.debug:
            print('[port][%s] Listening' % self.port)
        
        while self.is_running():
            try:
                (clientsocket, (ip, port)) = self.tcpsock.accept()
                if self.is_running():
                    if self.debug:
                        print('[port][{}] Accepted: {} <=> {}'.format(
                            self.port,
                            clientsocket.getsockname(),
                            clientsocket.getpeername(),
                        ))
                    newthread = self.threadclass(ip, port, clientsocket, **self.kwargs)
                    newthread.start()
                else:
                    break
            except socket.timeout:
                pass

        print('[port][%s] Stop listening' % self.port)

    def stop(self):
        super().stop()
        clientsocker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientsocker.connect((self.hostname, self.port))
        self.tcpsock.close()
