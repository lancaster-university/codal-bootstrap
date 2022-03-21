from colorama import Fore, Back, Style

class Log:
    @staticmethod
    def info( text ):
        print( Style.BRIGHT + text + Style.RESET_ALL )

    @staticmethod
    def warn( text ):
        print( Style.BRIGHT + Fore.YELLOW + text + Style.RESET_ALL )

    @staticmethod
    def error( text ):
        print( Style.BRIGHT + Fore.RED + text + Style.RESET_ALL )