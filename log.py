colour = True
try:
    from colorama import Fore, Back, Style
except ImportError as e:
    colour = False
    pass

class Log:
    @staticmethod
    def info( text ):
        if( colour ):
            print( Style.BRIGHT + text + Style.RESET_ALL )
        else:
            print( text )

    @staticmethod
    def warn( text ):
        if( colour ):
            print( Style.BRIGHT + Fore.YELLOW + text + Style.RESET_ALL )
        else:
            print( text )

    @staticmethod
    def error( text ):
        if( colour ):
            print( Style.BRIGHT + Fore.RED + text + Style.RESET_ALL )
        else:
            print( text )