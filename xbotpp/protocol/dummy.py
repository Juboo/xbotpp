import os
import socket
import xbotpp
from xbotpp import debug
from xbotpp import handler


class dummy:
    '''\
    Dummy protocol class.
    '''

    def __init__(self):
        #: Set to True to end the while loop in :func:`start`.
        self.term = False

        #: Path to the socket object
        self.sock_path = os.path.join(os.path.abspath('.'), 'xbotpp_dummy_socket')

        #: Socket object
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    def handle(self, data):
        '''\
        Handle data recieved from the socket
        '''

        for dline in [s.strip() for s in data.split('\n')]:
            parts = dline.split('\x01')

            if parts[0] in ['privmsg', 'pubmsg', 'notice']:
                event = handler.event.message(parts[1], parts[2], parts[3], parts[0])
                handler.handlers.on_message(event)

            elif parts[0] == "user_join":
                event = handler.event.user_join(parts[1])
                handler.handlers.on_user_join(event)

            elif parts[0] == "user_part":
                event = handler.event.user_part(parts[1])
                handler.handlers.on_user_part(event)

            elif parts[0] == "user_change_nick":
                event = handler.event.user_change_nick(parts[1], parts[2])
                handler.handlers.on_user_change_nick(event)

            elif parts[0] == "bot_die":
                self.term = True
                self.disconnect()

    def disconnect(self, message="See ya~"):
        '''\
        Disconnect from the server, with the quit message `message`.
        '''

        x = 'quit\x01{}\n'.format(message)
        self.sock.send(x.encode('utf-8'))

    def send_message(self, target, message):
        x = 'message\x01{0}\x01{1}'.format(target, message)
        self.sock.send(x.encode('utf-8'))

    def start(self):
        '''\
        Start listening on the socket for data and hand the data off to the
        :func:`handler` function.
        '''

        if os.path.exists(self.sock_path):
            os.remove(self.sock_path)

        self.sock.bind(self.sock_path)

        while self.term == False:
            data = self.sock.recv(4096)
            if data:
                self.handle(str(data, 'utf-8'))

        self.sock.close()
        os.remove(self.sock_path)
