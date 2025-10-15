from src.CommandHandler import *
from src.UmbraServer    import *
from src.TextAssets     import *

import argparse

def main() -> None:
        banner()

        parser                          = argparse.ArgumentParser()
        parser.add_argument("-c", type=str, help="Callback address")
        parser.add_argument("-p", type=int, help="HTTPS Handler port (Default 443)", default=443)
        parser.add_argument("-d", type=int, help="Client dwell time in milliseconds.", default=2000)
        args                            = parser.parse_args()

        if not args.c:
                debug("Callback address not specified (-c callback)")
                return

        umbra_server                    = UmbraServer()
        umbra_server.callback_ip        = args.c
        umbra_server.callback_port      = args.p
        umbra_server.time               = args.d

        if not umbra_server.startup(("0.0.0.0", args.p)):
                return

        command_handler                 = CommandHandler()
        command_handler.umbra_server    = umbra_server
        command_handler.command("generate encoded")

        try:
                while True:
                        user_input      = input(prompt())
                        command_handler.command(user_input)

        except KeyboardInterrupt:
                info("Exiting ...")
                command_handler.eradicate()

        except Exception as exception:
                error("Exception: {}".format(exception))
                command_handler.eradicate()

if __name__ == "__main__":
        main()