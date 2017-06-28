#
# ChRIS reloaded - ANSI Colors
#
# (c) 2012 FNNDSC, Boston Children's Hospital
#


class Colors( object ):
    '''
    ANSI colors.
    '''

    # Define some colours for prompt usage
    BLACK="\033[0;30m"
    RED="\033[0;31m"
    GREEN="\033[0;32m"
    BROWN="\033[0;33m"
    BLUE="\033[0;34m"
    PURPLE="\033[0;35m"
    CYAN="\033[0;36m"

    BLINK_BLACK="\033[5;30m"
    BLINK_RED="\033[5;31m"
    BLINK_GREEN="\033[5;32m"
    BLINK_BROWN="\033[5;33m"
    BLINK_BLUE="\033[5;34m"
    BLINK_PURPLE="\033[5;35m"
    BLINK_CYAN="\033[5;36m"

    YELLOW="\033[1;33m"
    LIGHT_GRAY="\033[0;37m"
    DARK_GRAY="\033[1;30m"
    LIGHT_RED="\033[1;31m"
    LIGHT_GREEN="\033[1;32m"
    LIGHT_BLUE="\033[1;34m"
    LIGHT_PURPLE="\033[1;35m"
    LIGHT_CYAN="\033[1;36m"
    WHITE="\033[1;37m"

    WHITE_BCKGRND="\033[47m"
    CYAN_BCKGRND="\033[46m"
    PURPLE_BCKGRND="\033[45m"
    BLUE_BCKGRND="\033[44m"
    BROWN_BCKGRND="\033[43m"
    GREEN_BCKGRND="\033[42m"
    RED_BCKGRND="\033[41m"
    BLACK_BCKGRND="\033[40m"

    NO_COLOUR="\033[0m"

  
    @staticmethod
    def strip( text ):
        '''
        Strips all color codes from a text.
        '''
        members = [attr for attr in Colors.__dict__.keys() if not attr.startswith( "__" ) and not attr == 'strip']

        for c in members:
            text = text.replace( vars( Colors )[c], '' )
        return text
