import os
import json


class ClosureException(Exception):
   pass


# https://stackoverflow.com/questions/20007319/how-to-do-a-large-text-file-transfer-in-python

class SocketTool:
    @classmethod
    def convert_to_bytes(cl, no):
        result = bytearray()
        result.append(no & 255)
        for i in range(3):
            no = no >> 8
            result.append(no & 255)
        return result

    @classmethod
    def bytes_to_number(cl, b):
        import sys
        b = b if (sys.version_info > (3, 0)) else map(ord, b)
        
        res = 0
        for i in range(4):
            res += b[i] << (i*8)
        return res        
        
    @classmethod
    def send_file(cl, s, filename, mode='rb'):
        length = os.path.getsize(filename)
        s.send(cl.convert_to_bytes(length)) # has to be 4 bytes
        with open(filename, mode) as infile:
            d = infile.read(1024*64) # We send by pack of 64 ko
            while d:
                s.send(d)
                d = infile.read(1024*64)

    @classmethod
    def get_file(cl, s):
        size = s.recv(4) # assuming that the size won't be bigger then 1GB
        size = cl.bytes_to_number(size)
        current_size = 0
        buffer = b''
        while current_size < size:
            data = s.recv(1024*64)
            if not data:
                break
            if len(data) + current_size > size:
                data = data[:size-current_size] # trim additional data
            buffer += data
            # you can stream here to disk
            current_size += len(data)
        # you have entire file in memory
        return buffer
        
    @classmethod
    def send_data(cl, s, data):
        data = json.dumps(data)
        data = data.encode('utf-8')
        s.send(cl.convert_to_bytes(len(data))) # has to be 4 bytes
        for i in range(0, len(data), 1024*64):
            s.send(data[i:i+1024*64])
        
    @classmethod
    def get_data(cl, s):
        import sys
        exception_class = json.decoder.JSONDecodeError if (sys.version_info > (3, 0)) else ValueError

        try:
            data = cl.get_file(s)
            data = data.decode('utf-8')
            data = json.loads(data)
            return data
        except exception_class:
            return None

    @classmethod
    def send_ack(cl, s, positive=True):
        data = 'OK' if positive else 'NO'
        s.send(data.encode('ascii'))

    @classmethod
    def get_ack(cl, s):
        data = s.recv(2).decode('ascii')
        return (data == 'OK')


class Protocol:
    def __init__(self, clientsocket):
        self.clientsocket = clientsocket
    
    def send_file(self, filename, mode='rb'):
        SocketTool.send_file(self.clientsocket, filename, mode)
    
    def get_file(self):
        return SocketTool.get_file(self.clientsocket)
        
    def send_data(self, data):
        SocketTool.send_data(self.clientsocket, data)
    
    def get_data(self):
        return SocketTool.get_data(self.clientsocket)
        
    def send_ack(self, positive=True):
        SocketTool.send_ack(self.clientsocket, positive)

    def send_nack(self, positive=True):
        SocketTool.send_ack(self.clientsocket, not positive)

    def get_ack(self):
        return SocketTool.get_ack(self.clientsocket)
        
    def please_assert(self, condition):
        if not condition:
            self.send_nack()
            self.clientsocket.close()
            raise ClosureException
    
    def get_object_or_nack(self, model, **kwargs):
        try:
            return model.objects.get(**kwargs)
        except model.DoesNotExist:
            self.send_nack()
            self.clientsocket.close()
            raise ClosureException
    
    def close(self):
        self.clientsocket.close()
