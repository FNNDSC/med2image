#!/usr/bin/env python

'''
This small module handles some error reporting for several
python classes.

The module assumes that the callingClass provides these methods:

    o callingClass.name()       -- returns the string name of the class
    o callingClass.log()        -- returns a Message() object member that
                                   is used a 'log' destination

Also, the callingClass must have a class dictionary, _dictErr, in which each
key has a dictionary of 'action', 'error', 'exitCode':

    callingClass._dictErr = {
        'someKey':      {
            'action':   'some action being performed,',
            'error':    'the error that occured',
            'exitCode': <int>
        }
    }

'''

import  inspect
import  sys

from ._colors import Colors

def report(     callingClass,
                astr_key,
                ab_exitToOs=1,
                astr_header=""
                ):
    '''
    Error handling.

    Based on the <astr_key>, error information is extracted from
    _dictErr and sent to log object.

    If <ab_exitToOs> is False, error is considered non-fatal and
    processing can continue, otherwise processing terminates.

    '''
    log         = callingClass.log()
    b_syslog    = log.syslog()
    log.syslog(False)
    if ab_exitToOs: log( Colors.RED +    "\n:: FATAL ERROR :: " + Colors.NO_COLOUR )
    else:           log( Colors.YELLOW + "\n::   WARNING   :: " + Colors.NO_COLOUR )
    if len(astr_header): log( Colors.BROWN + astr_header + Colors.NO_COLOUR )
    log( "\n" )
    log( "\tSorry, some error seems to have occurred in:\n\t<" )
    log( Colors.LIGHT_GREEN + ("%s" % callingClass.name()) + Colors.NO_COLOUR + "::")
    log( Colors.LIGHT_CYAN + ("%s" % inspect.stack()[2][4][0].strip()) + Colors.NO_COLOUR)
    log( "> called by <")
    try:
        caller = inspect.stack()[3][4][0].strip()
    except:
        caller = '__main__'
    log( Colors.LIGHT_GREEN + ("%s" % callingClass.name()) + Colors.NO_COLOUR + "::")
    log( Colors.LIGHT_CYAN + ("%s" % caller) + Colors.NO_COLOUR)
    log( ">\n")

    log( "\tWhile %s\n" % callingClass._dictErr[astr_key]['action'] )
    log( "\t%s\n" % callingClass._dictErr[astr_key]['error'] )
    log( "\n" )
    if ab_exitToOs:
        log( "Returning to system with error code %d\n" % \
                        callingClass._dictErr[astr_key]['exitCode'] )
        sys.exit( callingClass._dictErr[astr_key]['exitCode'] )
    log.syslog(b_syslog)
    return callingClass._dictErr[astr_key]['exitCode']


def fatal( callingClass, astr_key, astr_extraMsg="" ):
    '''
    Convenience dispatcher to the error_exit() method.

    Will raise "fatal" error, i.e. terminate script.
    '''
    b_exitToOS  = True
    report( callingClass, astr_key, b_exitToOS, astr_extraMsg )


def warn( callingClass, astr_key, astr_extraMsg="" ):
    '''
    Convenience dispatcher to the error_exit() method.

    Will raise "warning" error, i.e. script processing continues.
    '''
    b_exitToOS = False
    report( callingClass, astr_key, b_exitToOS, astr_extraMsg )

    
    