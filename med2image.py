#!/usr/bin/env python
#
# NAME
#
#        med2image
#
# DESCRIPTION
#
#        'med2image' converts from medical image data files to
#        display-friendly formats (like png and jpg).
#
# HISTORY
#
# 23 February 2015
# o Initial design and coding.
#

# System imports
import     os
import     sys
import     getpass
import     argparse
import     time
import     numpy     as     np
from       random    import randint

# Project specific imports
from       _common           import     systemMisc     as misc
from       _common._colors   import     Colors
from       _common           import     error
from       _common           import     message        as Message

class med2image(object):
    """
        med2image accepts as input certain medical image formatted data
        and converts each (or specified) slice of this data to a graphical
        display format such as png or jpg.

    """

    _dictErr = {
        'inputFileFail'   : {
            'action'        : 'trying to read input file, ',
            'error'         : 'no handler for this cluster type has been derived.',
            'exitCode'      : 10},
        'emailFail'   : {
            'action'        : 'attempting to send notification email, ',
            'error'         : 'sending failed. Perhaps host is not email configured?',
            'exitCode'      : 20},
    }

    def description(self, *args):
        '''
        Get / set internal object description.
        '''
        if len(args):
            self._str_desc = args[0]
        else:
            return self._str_desc

    def __init__(self, **kwargs):

        #
        # Object desc block
        #
        self._str_desc                  = ''



        # Directory and filenames
        self._str_workingDir            = ''
        self._str_inputFile             = ''
        self._str_outputFileStem        = ''
        self._str_outputFileType        = ''

        self._b_convertAllSlices        = False

        self._str_stdout                = ""
        self._str_stderr                = ""
        self._exitCode                  = 0

        # The actual data volume
        self._V_data                    = None

        for key, value in kwargs.iteritems():
            if key == "remotePort":     self._str_remotePort    = value
            if key == "remoteHost":
                self._b_sshDo           = True
                l_remoteHost    = value.split(':')
                self._str_remoteHost = l_remoteHost[0]
                if len(l_remoteHost) == 2:
                    self._str_remotePort = l_remoteHost[1]
            if key == "remoteUser":     self._str_remoteUser    = value
            if key == "remoteUserIdentity":   self._str_remoteUserIdentity = value

    def run(self):
        '''
        The main 'engine' of the class.
        '''

    def echo(self, *args):
        self._b_echoCmd         = True
        if len(args):
            self._b_echoCmd     = args[0]

    def echoStdOut(self, *args):
        self._b_echoStdOut      = True
        if len(args):
            self._b_echoStdOut  = args[0]

    def stdout(self):
        return self._str_stdout

    def stderr(self):
        return self._str_stderr

    def exitCode(self):
        return self._exitCode

    def echoStdErr(self, *args):
        self._b_echoStdErr      = True
        if len(args):
            self._b_echoStdErr  = args[0]

    def dontRun(self, *args):
        self._b_runCmd          = False
        if len(args):
            self._b_runCmd      = args[0]

    def workingDir(self, *args):
        if len(args):
            self._str_workingDir = args[0]
        else:
            return self._str_workingDir

def synopsis(ab_shortOnly = False):
    scriptName = os.path.basename(sys.argv[0])
    shortSynopsis =  '''
    SYNOPSIS

            %s                                   \\
                    -i|--input <inputFile>                 \\
                    -o|--output <outputFile>               \\
                    [--outputType <outputType>]            \\
                    [--sliceToConvert <sliceToConvert>]    \\
                    [--man|--synopsis]
    ''' % scriptName

    description =  '''
    DESCRIPTION

        `%s' converts input medical image formatted data to a more
        display friendly format.

        Currently understands nifti and dicom.

    ARGS

        -i|--input <inputFile>
        Input file to convert. Typically a DICOM file or a nifti volume.

        -o|--output <outputFile>
        The output file to store conversion.

        [--outputType <outputType>]
        The output file type. If different to <outputFile> extension, will
        append <outputType> to <outputFile>.

        [--sliceToConvert <sliceToConvert>]
        In the case of volume files, the slice (z) index to convert.

        [--man|--synopsis]
        Show either full help or short synopsis.

    EXAMPLES


    ''' % (scriptName)
    if ab_shortOnly:
        return shortSynopsis
    else:
        return shortSynopsis + description

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="med2view converts an input medical image file to a more conventional graphical format.")
    parser.add_argument("-i", "--input",
                        help="input file",
                        dest='input')
    parser.add_argument("-o", "--output",
                        help="output file",
                        dest='output')
    parser.add_argument("-t", "--outputType",
                        help="output image type",
                        dest='outputType',
                        default='none')
    parser.add_argument("-s", "--sliceToConvert",
                        help="slice to convert",
                        dest='sliceToConvert',
                        default='-1')
    parser.add_argument("--printElapsedTime",
                        help="print program run time",
                        dest='printElapsedTime',
                        action='store_true',
                        default=False)
    parser.add_argument("--man",
                        help="man",
                        dest='man',
                        action='store_true',
                        default=False)
    parser.add_argument("--synopsis",
                        help="short synopsis",
                        dest='synopsis',
                        action='store_true',
                        default=False)
    args = parser.parse_args()

    if args.man or args.synopsis:
        if args.man:
            str_help     = synopsis(False)
        else:
            str_help     = synopsis(True)
        print(str_help)
        sys.exit(1)

    C_convert     = med2image(
                                input          = args.input,
                                output         = args.output,
                                outputType     = args.outputType,
                                sliceToConvert = args.sliceToConvert
                             )


    # And now run it!
    misc.tic()
    C_convert.run()
    if args.printElapsedTime: print("Elapsed time = %f seconds" % misc.toc())





