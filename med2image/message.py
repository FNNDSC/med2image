#!/usr/bin/env python3.5

import  sys
import  os
import  time
import  inspect
from    io          import  IOBase

# pman local dependencies
from    .dgmsocket   import  C_dgmsocket
from    ._colors     import  Colors

class Message:
    '''
    A simple messaging class that is able to send text content to a variety
    of destinations, including file handles, system devices, and datagram
    socket targets.

    Messages can be tagged with optional debug level descriptors, allowing
    easy filtering by setting an object's internal verbosity value.
    
    Messages can also be prepended with syslog style prefixes, as well as
    "group" type string tags for easy post-filtering.

    Furthermore, text messages can be left/right justified in columns of given 
    width by setting in-call flags.
    
    '''

    def verbosity(self, *args):
        '''
        get/set the verbosity level.

        The verbosity level filters messages that are output
        to the console. Only messages tagged with a verbosity
        less-than-or-equal-to the class verbosity are output.

        This does not affect output to non-console devices
        such as files or remote sockets.

        verbosity():    returns the current level
        verbosity(<N>): sets the verbosity to <N>
        
        '''
        if len(args):
            self._verbosity             = args[0]
        else:
            return self._verbosity
    

    def tagstring(self, *args):
        '''
        get/set the tag string itself.

        If called with non-zero length argument, will toggle the
        internal b_tag flag to True.

        The tagstring, if flagged TRUE and non-zero length, will
        prepend each output log line. In this manner, it's possible
        to post-filter log files for specific tags.

        tagstring():            returns the current tagstring
        tagstring(<string>):    sets the tagstring to <string>

        '''
        if len(args):
            self._str_tag = args[0]
            self._b_tag   = True
        else:
            return self._str_tag


    def tag(self, *args):
        '''
        get/set the tag flag.

        The tag flag toggles the most basic prepending to each log
        output. The idea with the tagging text is to provide a 
        simple mechanism by which a log output can be filtered/parsed
        for specific outputs.

        tag():                  returns the current syslog flag
        tag(True|False):        sets the flag to True|False

        '''
        if len(args):
            self._b_tag = args[0]
        else:
            return self._b_tag


    def syslog(self, *args):
        '''
        get/set the syslog flag.

        The syslog flag toggles prepending each message with
            a syslog-style prefix.

        syslog():               returns the current syslog flag
        syslog(True|False):     sets the flag to True|False

        '''
        if len(args):
            self._b_syslog = args[0]
        else:
            return self._b_syslog


    def str_syslog(self, *args):
        '''
        get/set the str_syslog, i.e. the current value of the
        syslog prepend string.

        str_syslog():           returns the current syslog string
        str_syslog(<astr>):     sets the syslog string to <astr>

        '''
        if len(args):
            self._str_syslog = args[0]
        else:
            return self._str_syslog
            

    def tee(self, *args):
        '''
        get/set the tee flag.

        The tee flag toggles any output that is directed to non-console
        destinations to also appear on the console. Tee'd console output
        is still verbosity filtered
        
        tee():                  returns the current syslog flag
        tee(True|False):        sets the flag to True|False

        '''
        if len(args):
            self._b_tee = args[0]
        else:
            return self._b_tee


    def socket_parse(self, astr_destination):
        '''
        Examines <astr_destination> and if of form <str1>:<str2> assumes
        that <str1> is a host to send datagram comms to over port <str2>.

        Returns True or False.
        
        '''
        t_socketInfo = astr_destination.partition(':')
        if len(t_socketInfo[1]):
            self._b_isSocket    = True
            self._socketRemote  = t_socketInfo[0]
            self._socketPort    = t_socketInfo[2]
        else:
            self._b_isSocket    = False
        return self._b_isSocket
        

    def to(self, *args):
        '''
        get/set the 'device' to which messages are sent.

        Valid targets are:

            string filenames:           '/tmp/test.log'
            remote hosts:               'pretoria:1701'
            system devices:             sys.stdout, sys.stderr
            special names:              'stdout'
            file handles:               open('/tmp/test.log')
            
        '''
        if len(args):
            self._logFile = args[0]
            if self._logHandle and self._logHandle != sys.stdout:
                self._logHandle.close()
            
            # if type(self._logFile) is types.FileType:
            if isinstance(self._logFile, IOBase):
                self._logHandle = self._logFile
            elif self._logFile == 'stdout':
                self._logHandle = sys.stdout
            elif self.socket_parse(self._logFile):
                self._logHandle = C_dgmsocket(
                                            self._socketRemote,
                                            int(self._socketPort))
            else:
                self._logHandle = open(self._logFile, "a")
            self._sys_stdout      = self._logHandle
        else:
            return self._logFile
            
            
    def vprintf(self, alevel, format, *args):
        '''
        A verbosity-aware printf.

        '''
        if self._verbosity and self._verbosity >= alevel:
            sys.stdout.write(format % args)

    def canPrintVerbose(self, alevel):
        return int(self._verbosity) and int(alevel) <= int(self._verbosity)
        

    @staticmethod
    def syslog_generate(str_processName, str_pid):
      '''
      Returns a string similar to:

            Tue Oct  9 10:49:53 2012 pretoria message.py[26873]:

      where 'pretoria' is the hostname, 'message.py' is the current process
      name and 26873 is the current process id.
      '''
      localtime = time.asctime( time.localtime(time.time()) )      
      hostname = os.uname()[1]
      syslog = '%s %s %s[%s]' % (localtime, hostname, str_processName, str_pid)
      return syslog
      
        
    def __call__(self, *args, **kwargs):
        '''
        Output the payload.

        The following keyword arguments are supported:

            debug = <level>             tag this message with a debug level
            verbosity = <level>         same as 'debug'

            syslog = True|False         temporarily set the syslog flag for
                                        this function call. Useful when
                                        creating a two-column output
            lw = <colWidth>             left justify message in <colWidth>
            rw = <colWidth>             right justify message in <colWidth>

        Typical calling syntax:

            log = Message()

            # default
            log.to(sys.stdout)

            # prints message to stdout            
            log('hello, world\n')              

            log.verbosity(1)
            # With verbosity set to 1, messages tagged with
            # a debug level greater than 1 will not be
            # printed to stdout.
            log('hello world\n', debug=5)

            # Setting verbosity to 10 will allow the previous
            # message to be printed.
            log.verbosity(10)
            log('hello, world\n', debug=5)

            # Simple two-column justifed output can be created by
            # first printing a message left justifed in a column of
            # width 40 (with no carriage return, i.e. no '\n')
            log('starting process...', lw=40)
            # followed by a right justified message (with a '\n')
            log('[ ok ]\n', rw=20)

        The payload presentation is dependent on several internal flags:

        1. If the class verbosity() is set, i.e. message.verbosity(10), then
           messages are only output to the console if the internal verbosity
           level is less than the tagged level of the message.
        2. If the 'tee' flag is set, and if the output destination is anything
           other than sys.stdout, the message will always be echoed to the 
           console (irrespective of any 'debug' tags)
           

        '''
        b_syslog        = self._b_syslog
        str_prepend     = ''
        str_msg         = ''
        verbosity       = 0
        lw              = 0
        rw              = 0
        str_end         = ' '

        for key, value in kwargs.items():
            if key == 'debug' or key == 'verbose':      verbosity       = value
            if key == 'lw':                             lw              = -value
            if key == 'rw':                             rw              = value
            if key == 'syslog':                         self._b_syslog  = value
            if key == 'end':                            str_end         = value

        if self._b_tag and len(self._str_tag):
            str_prepend = Colors.LIGHT_CYAN + self._str_tag + ' ' + Colors.NO_COLOUR

        if self._b_syslog:
            self._str_syslog = '%s: ' % self.syslog_generate(
                                        self._processName, self._pid)
            str_prepend = Colors.LIGHT_GRAY + self._str_syslog + Colors.NO_COLOUR
        if len(args):
            str_msg = '%s%s' % (str_prepend, args[0])
        else:
            str_msg = '%s%s' % (str_prepend, self._str_payload)
            self._str_payload = ''
        if lw: str_msg  = '%*s' % (lw, str_msg)
        if rw: str_msg  = '%*s' % (rw, str_msg)
        if self._b_flushNewLine and str_end != '':    str_msg += '\n'

        if self._logHandle == sys.stdout:
            if verbosity:
                if self.canPrintVerbose(verbosity):
                    self._sys_stdout.write(str_msg)
            else:
                self._sys_stdout.write(str_msg)
        else:
            self._sys_stdout.write(Colors.strip(str_msg))
        self._sys_stdout.flush()
        if self._b_tee and self._logHandle != sys.stdout:
            if verbosity:
                if self.canPrintVerbose(verbosity):
                    sys.stdout.write(str_msg)
            else: sys.stdout.write(str_msg)
            sys.stdout.flush()
        self.syslog(b_syslog)    

        
    def append(self, str_msg):
        '''
        Append <str_msg> to the internal payload.
        '''
        self._str_payload += str_msg


    def clear(self):
        '''
        Clear the internal payload, i.e. set to empty string.
        '''
        self._str_payload       = ''
            
                
    def __init__(self, **kwargs):
        '''
        Constructor.

        The following keyword arguments are supported:

            syslogPrepend = 0|1         set the syslog prepend flag to 0|1
            logTo = <destination>       set the <destination> that will print
                                        messages.
            tee = 0|1                   set the tee flag to 0|1

        '''

        self._verbosity         = 0

        # On construction, set the "internal" stdout and stderr to the 
        # (current) system stdout and stderr file handles
        self._sys_stdout        = sys.stdout
        self._sys_stderr        = sys.stderr

        self._verbosity         = 1
        self._b_syslog          = False
        self._str_syslog        = ''
        self._b_tag             = False
        self._str_tag           = ''
        self._b_tee             = False
        self._b_flushNewLine    = False

        self._b_isSocket        = False
        self._socketPort        = 0
        self._socketRemote      = ''

        self._str_payload       = ''
        self._logFile           = 'stdout'
        self._logHandle         = None

        self._processName       = os.path.basename(
                                    inspect.stack()[-1][0].f_code.co_filename)
        self._pid               = os.getpid()

        self.to(self._logFile)
        for key, value in kwargs.items():
            if key == "syslogPrepend":  self._b_syslog          = int(value)
            if key == "logTo":          self.to(value)
            if key == 'tee':            self._b_tee             = value
            
        
if __name__ == "__main__":
    '''
    __main__
    '''

    
    log1 = Message()
    log2 = Message()
    
    log1.syslog(True)
    log1(Colors.RED + Colors.WHITE_BCKGRND + 'hello world!\n' + Colors.NO_COLOUR)

    # Send message via datagram to 'pretoria' on port '1701'.
    log1.to('pangea:1701')
    log1('hello, pangea!\n');
    log1('this has been sent over a datagram socket...\n')

    # Now for some column width specs and 'debug' type messages
    # These will all display on the console since debug=5 and the
    # log1.verbosity(10) means that all debug tagged messages with
    # level less-than-or-equal-to 10 will be passed.
    log1.to('stdout')
    log1.verbosity(10)
    log1('starting process 1...', lw=90, debug=5)
    log1('[ ok ]\n', rw=20, syslog=False, debug=5)
    log1('parsing process 1 outputs...', lw=90, debug=5)
    log1('[ ok ]\n', rw=20, syslog=False, debug=5)
    log1('preparing final report...', lw=90, debug=5)
    log1('[ ok ]\n', rw=20, syslog=False, debug=5)

    log2.to('/tmp/log2.log')
    log2.tee(True)
    # A verbosity level of log2.verbosity(1) and a
    # log2.to(sys.stdout) will not output any of the 
    # following since the debug level for each message 
    # is set to '5'. The verbosity should be at least
    # log2.verbosity(5) for output to appear on the
    # console.
    # 
    # If log2.tee(True) and log2.to('/tmp/log2.log')
    # then all messages will be displayed regardless
    # of the internal verbosity level.
    log2.verbosity(1)   
    log2('starting process 1...', lw=90, debug=5)
    log2('[ ok ]\n', rw=20, syslog=False, debug=5)
    log2('parsing process 1 outputs...', lw=90, debug=5)
    log2('[ ok ]\n', rw=20, syslog=False, debug=5)
    log2('preparing final report...', lw=90, debug=5)
    log2('[ ok ]\n', rw=20, syslog=False, debug=5)

    
    log1.to('/tmp/test.log')
    log1('and now to /tmp/test.log\n')

    log2.to(open('/tmp/test2.log', 'a'))
    log2('another message to /tmp/test2.log\n')
    log2.tagstring('MARK-->')
    log2('this text is tagged\n')
    log2('and so is this text\n')
    
    log1.clear()
    log1.append('this is message ')
    log1.append('that is constructed over several ')
    log1.append('function calls...\n')
    log1.to('stdout')
    log1()

    log2.tag(False)
    log2('goodbye!\n')
    
