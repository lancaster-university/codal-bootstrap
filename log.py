from colorama import Fore, Back, Style

class Log:
    @staticmethod
    def log_info( text ):
        print( Style.BRIGHT + text + Style.RESET_ALL )

    @staticmethod
    def log_warn( text ):
        print( Style.BRIGHT + Fore.YELLOW + text + Style.RESET_ALL )

    @staticmethod
    def log_error( text ):
        print( Style.BRIGHT + Fore.RED + text + Style.RESET_ALL )