from src.Utilities import *

# TLS has a specific structured handshake it like to walk through before beginning
# communication with a given client. Its easier to break the records out step by
# step to derive our information.

class Request:
        @Private.Class
        class RecordLayer:
                def __init__(self,
                        handshake               : int = 0,
                        version                 : int = 0,
                        length                  : int = 0
                ) -> None:
                        self.handshake          = handshake
                        self.version            = version
                        self.length             = length

        @Private.Class
        class HandshakeLayer:
                def __init__(self,
                        handshake_type          : int = 0,
                        length                  : int = 0
                ) -> None:
                        self.handshake_type     = handshake_type
                        self.length             = length

        @Private.Class
        class ClientHello:
                def __init__(self,
                        client_version          : int = 0,
                        random                  : int = 0,
                        session_id_length       : int = 0,
                        session_id              : int = 0,
                        cipher_suite_length     : int = 0,
                        cipher_suite            : int = 0
                ) -> None:
                        self.client_version     = client_version
                        self.random             = random
                        self.session_id_length  = session_id_length
                        self.session_id         = session_id
                        self.cipher_suite_length = cipher_suite_length
                        self.cipher_suite       = cipher_suite

        def __init__(self, client_hello: int) -> None:
                self.record_layer       = Request.RecordLayer()
                self.handshake_layer    = Request.HandshakeLayer()
                self.client_hello       = Request.ClientHello()
                self.validity           = self.extract(client_hello)

        @Private.Method
        def extract(self, data: bytes) -> bool:
                data                    = self.reverse(data)

                # Record Layer
                data, record_layer      = self.harvest(data, 5)

                record_layer, self.record_layer.handshake = self.harvest(record_layer, 1, True)
                record_layer, self.record_layer.version   = self.harvest(record_layer, 2, True)
                record_layer, self.record_layer.length    = self.harvest(record_layer, 2, True)

                if self.record_layer.handshake != 0x16:
                        return False

                if self.record_layer.version != 0x0303:
                        return False

                # Handshake Layer
                data, handshake_layer             = self.harvest(data, 4)

                handshake_layer, self.handshake_layer.handshake_type = self.harvest(handshake_layer, 1, True)
                handshake_layer, self.handshake_layer.length         = self.harvest(handshake_layer, 3, True)

                if self.handshake_layer.handshake_type != 0x01:
                        return False

                # ClientHello
                data, client_hello                = self.harvest(data, self.handshake_layer.length)

                client_hello, self.client_hello.client_version      = self.harvest(client_hello, 2, True)
                client_hello, self.client_hello.random              = self.harvest(client_hello, 32, True)
                client_hello, self.client_hello.session_id_length   = self.harvest(client_hello, 1, True)
                client_hello, self.client_hello.session_id          = self.harvest(client_hello, self.client_hello.session_id_length, True)
                client_hello, self.client_hello.cipher_suite_length = self.harvest(client_hello, 2, True)
                client_hello, self.client_hello.cipher_suite        = self.harvest(client_hello, self.client_hello.cipher_suite_length, True)

                return True

        @Private.Method
        def reverse(self, data: int) -> int:
                target                  = 0x00

                while data:
                        byte            = data & 0xFF
                        target          = (target << 8) | byte
                        data          >>= 8

                return target

        @Private.Method
        def harvest(self, data: int, length: int, reverse: bool = False) -> tuple[int, int]:
                target                  = 0x00

                for _ in range(length):
                        byte            = data & 0xFF
                        target          = (target << 8) | byte
                        data          >>= 8

                if not reverse:
                        target          = self.reverse(target)

                return data, target

class Response:
        def ClientHello(random: bytes) -> bytes:
                response                = (
                        # Record Layer
                        b"\x16"             # Hanshake
                        b"\x03\x03" +       # Version
                        b"\x00\x2D" +       # Length

                        # Handshake Layer
                        b"\x01" +           # Type
                        b"\x00\x00\x29" +   # Length

                        # ClientHello
                        b"\x03\x03" +       # Version
                        random +
                        b"\x00" +           # Session ID Length
                        b"\x00\x02" +       # Cipher Suites Length
                        b"\x00\x2F" +       # Cipher Suites
                        b"\x01" +           # Compression Methods Length
                        b"\x00"             # Compression Methods
                )

                return response

        def ServerHello(random: bytes) -> bytes:
                response                = (
                        # Record Layer
                        b"\x16"             # Hanshake
                        b"\x03\x03" +       # Version
                        b"\x00\x2C" +       # Length

                        # Handshake Layer
                        b"\x02" +           # ServerHello
                        b"\x00\x00\x28" +   # Length

                        # ServerHello
                        b"\x03\x03" +       # Version
                        random +
                        b"\x00" +           # Session ID Length
                        b"\x00\x2F" +       # Cipher Suites
                        b"\x00" +           # Compression Methods Length
                        b"\x00\x00"         # Extensions Length
                )
                return response

        def ServerHelloDone() -> bytes:
                response                = (
                        b"\x16"             # Handshake
                        b"\x03\x03"         # Version
                        b"\x00\x04"         # Length
                        b"\x0E"             # ServerHelloDone
                        b"\x00\x00\x00"     # Length
                )
                return response

        def ChangeCipherSpec() -> bytes:
                response                = (
                        b"\x14"             # Handshake
                        b"\x03\x03"         # Version
                        b"\x00\x01"         # Length
                        b"\x01"             # ChangeCipherSpec
                )
                return response

        def ApplicationData(application_data: bytes) -> bytes:
                response                = (
                        b"\x17" +
                        b"\x03\x03" +
                        int.to_bytes(len(application_data), 2) +
                        application_data
                )
                return response