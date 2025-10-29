from src.Utilities import *

import socket
import time
import threading

# Because multiple times these same methods are being called, the simpler approach
# is to include them in a more public-accessible area.

# The #1 issue with linux or another operating system alike, is the ability to send
# or prioritize sending packets fragmented. If we grab a chunk of data and the OS
# intended on sending more, we close off immediatetly, rather we should wait for the
# whole chunk of data to be sent over.

class Receiver:
        def __init__(self, time: int = 2000) -> None:
                self.time               = time

        @Public.Method
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

        @Public.Method
        def start_timer(self) -> threading.Thread:
                timer                   = threading.Thread(
                        target          = self.timeout,
                        daemon          = True
                )
                timer.start()

                return timer

        @Public.Method
        def timeout(self) -> None:
                seconds                 = self.time / 1000
                time.sleep(seconds)