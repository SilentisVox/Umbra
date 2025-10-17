import sys
import time
import datetime

RED                                     = "\033[38;2;220;0;0m"
YELLOW                                  = "\033[38;2;227;176;0m"
GREEN                                   = "\033[38;2;90;220;100m"
BLUE                                    = "\033[38;2;100;180;230m"
GRAY                                    = "\033[38;2;80;80;80m"
UNDER                                   = "\001\033[4m\002"
END                                     = "\033[0m"

def sys_print(user_input: str) -> None:
        sys.stdout.write(user_input)

def flush() -> None:
        sys.stdout.flush()

def white(user_input: str) -> str:
        return "\033[38;2;255;255;255m{}\033[0m".format(user_input)

def red(user_input: str) -> str:
        return "\033[38;2;219;37;40m{}\033[0m".format(user_input)

def yorange(user_input: str) -> str:
        return "\033[38;2;219;165;22m{}\033[0m".format(user_input)

def green(user_input: str) -> str:
        return "\033[38;2;59;219;46m{}\033[0m".format(user_input)

def teal(user_input: str) -> str:
        return "\033[38;2;0;219;163m{}\033[0m".format(user_input)

def blue(user_input: str) -> str:
        return "\033[38;2;71;156;219m{}\033[0m".format(user_input)

def gray(user_input: str) -> str:
        return "\033[38;2;80;80;80m{}\033[0m".format(user_input)

def custom(user_input: str, color: tuple[int, int, int]) -> str:
        return "\033[38;2;{};{};{}m{}\033[0m".format(color[0], color[1], color[2], user_input)

def timey() -> str:
        return datetime.datetime.now().strftime("%H:%M:%S")

def info(user_input: str) -> None:
        sys_print("\r[{}] [{}] {}\n".format(teal(timey()), blue("INFO"), user_input))
        flush()

def debug(user_input: str) -> None:
        sys_print("\r[{}] [{}] {}\n".format(teal(timey()), yorange("DBUG"), user_input))
        flush()

def success(user_input: str) -> None:
        sys_print("\r[{}] [{}] {}\n".format(teal(timey()), green("DONE"), user_input))
        sys_print(prompt())
        flush()

def error(user_input: str) -> None:
        sys_print(("\r[{}] [{}] {}\n".format(teal(timey()), red("FAIL"), user_input)))
        flush()

def cursor_on():
        sys_print("\033[?25h")
        flush()

def cursor_off():
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

def prompt() -> str:
        return "\r{}Umbra{}> ".format(UNDER, END)

def banner() -> None:
        unfromatted_banner                      = "┬ ┬┌┬┐┬─┐┬─┐┌─┐│ ││││├─┤├┬┘├─┤└─┘┴│┴┴─┘┴└ ┴ ┴"
        colors                                  = [
                (145, 145, 145), (129, 129, 129), (145, 145, 145), (140, 140, 140),
                (132, 132, 132), (125, 125, 125), (125, 125, 125), (126, 126, 126),
                (125, 125, 125), (125, 125, 125), (132, 132, 132), (140, 140, 140),
                (145, 145, 145), (145, 145, 145), (145, 145, 145), (145, 145, 145),
                (129, 129, 129), (123, 123, 123), (97, 97, 97),    (45, 45, 45),
                (53, 53, 53),    (47, 47, 47),    (45, 45, 45),    (47, 47, 47),
                (53, 53, 53),    (45, 45, 45),    (97, 97, 97),    (123, 123, 123),
                (129, 129, 129), (145, 145, 145), (124, 124, 124), (94, 94, 94),
                (43, 43, 43),    (43, 43, 43),    (43, 43, 43),    (43, 43, 43), 
                (43, 43, 43),    (43, 43, 43),    (43, 43, 43),    (43, 43, 43), 
                (43, 43, 43),    (43, 43, 43),    (43, 43, 43),    (94, 94, 94), 
                (124, 124, 124)
        ]
        formatted_banner                = unfromatted_banner.replace("\n", "")
        finished                        = ""
        
        for index, character in enumerate(formatted_banner):
                color                   = colors[index]
                r, g, b                 = color[0], color[1], color[2]

                if not index % 15:
                        finished+= "\n  "

                finished                += f"\033[38;2;{r};{g};{b}m{character}\033[0m"
        finished                        += "\n"

        sys_print(finished)
        flush()
        silentis()

def silentis() -> None:
        cursor_off()

        for _ in range(39):
                s1                      = custom("s", color_calculator(_ + 1))
                i1                      = custom(("i" if _ > 4  else ""), color_calculator(_ - 4))
                l                       = custom(("l" if _ > 8  else ""), color_calculator(_ - 8))
                e                       = custom(("e" if _ > 12 else ""), color_calculator(_ - 12))
                n                       = custom(("n" if _ > 16 else ""), color_calculator(_ - 16))
                t                       = custom(("t" if _ > 20 else ""), color_calculator(_ - 20))
                i2                      = custom(("i" if _ > 24 else ""), color_calculator(_ - 24))
                s2                      = custom(("s" if _ > 28 else ""), color_calculator(_ - 28))

                name                    = "\r         " + s1 + i1 + l + e + n + t + i2 + s2
                sys_print(name)
                flush()
                time.sleep(0.02)

        sys_print("\n\n")
        flush()
        cursor_on()

def color_calculator(calculated_step: int) -> None:
        if calculated_step < 0:
                number                          = (0, 0, 0)

        elif calculated_step < 6:
                number                          = calculated_step * 29

        elif calculated_step < 10:
                number                          = (145 - ((calculated_step - 6) * 29))

        else:
                number                          = 58

        return (number, number, number)

def get_help():
        menu                            = """
        \r Command       Description
        \r ----------------------------------------------------------------------
        \r
        \r shell    [+]  Begins communication with a specified client.
        \r sessions      Displays current sessions avaialable.
        \r generate      Generates a reverse shell payload w/ settings.
        \r jobs          Displays current services running.
        \r start    [+]  Starts the HTTPS service.
        \r stop     [+]  Stops the HTTPS service.
        \r kill     [+]  Kills a connection with a specified client.
        \r eradicate     Kills all current sessions.
        \r help          Displays this menu.
        \r clear         Clears the terminal window.
        \r exit          Exits Silence.

        """

        sys_print(menu)
        flush()

def get_command_help(description):
        menu                            = """
        \r Command               Description
        \r ----------------------------------------------------------------------
        \r {}\n""".format(description)

        sys_print(menu)
        flush()

def jobs(server: object) -> None:
        port                            = str(server.server.bind_agent.getsockname()[1])
        status                          = green("Started") if server.server.running else "Stopped"
        job_list = """
        \r Jobs                   Status
        \r ----------------------------------------------------------------------
        \r https://0.0.0.0:{}{}{}\n\n""".format(port, (" " * (7 - len(port))), status)

        sys_print(job_list)
        flush()

def sessions(clients: dict) -> None:
        all_sessions                    = """     
        \r Client ID       IP Address       OS Type            User        Status
        \r ----------------------------------------------------------------------
        \r"""

        for client_id in clients.keys():
                client                  = clients[client_id]
                client_ip               = (str(client.ip)   + " " * 16)[:15]
                client_os               = (str(client.os)   + " " * 18)[:17]
                client_user             = (str(client.user) + " " * 11)[:10]
                client_status           = green("Active") if client.status == "Active" else red("Lost")
                all_sessions           += " {}  {}  {}  {}  {}\n".format(client_id, client_ip, client_os, client_user, client_status)

        all_sessions                   += "\n"
        sys_print(all_sessions)
        flush()