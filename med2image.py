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
import     glob
import     numpy             as         np
from       random            import     randint
import     re

# System dependency imports
import     nibabel           as         nib
import     dicom
import     pylab
import     matplotlib.cm     as         cm

# Project specific imports
import     error
import     message           as msg
from       _common           import     systemMisc     as misc
from       _common._colors   import     Colors

class med2image(object):
    """
        med2image accepts as input certain medical image formatted data
        and converts each (or specified) slice of this data to a graphical
        display format such as png or jpg.

    """

    _dictErr = {
        'inputFileFail'   : {
            'action'        : 'trying to read input file, ',
            'error'         : 'could not access/read file -- does it exist? Do you have permission?',
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

    def log(self): return self._log

    @staticmethod
    def urlify(astr, astr_join = '_'):
        # Remove all non-word characters (everything except numbers and letters)
        astr = re.sub(r"[^\w\s]", '', astr)
        
        # Replace all runs of whitespace with an underscore
        astr = re.sub(r"\s+", astr_join, astr)
        
        return astr

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
        self._str_outputDir             = ''

        self._b_convertAllSlices        = False
        self._str_sliceToConvert        = ''
        self._str_frameToConvert        = ''
        self._sliceToConvert            = -1
        self._frameToConvert            = -1

        self._str_stdout                = ""
        self._str_stderr                = ""
        self._exitCode                  = 0

        # The actual data volume and slice
        # are numpy ndarrays
        self._b_4D                      = False
        self._b_3D                      = False
        self._b_DICOM                   = False
        self._Vnp_4DVol                 = None
        self._Vnp_3DVol                 = None
        self._Mnp_2Dslice               = None
        self._dcm                       = None

        # A logger
        self._log                       = msg.Message()
        self._log.syslog(True)

        # Flags
        self._b_showSlices              = False
        self._b_convertMiddleSlice      = False
        self._b_convertMiddleFrame      = False

        for key, value in kwargs.iteritems():
            if key == "inputFile":          self._str_inputFile         = value
            if key == "outputDir":          self._str_outputDir         = value
            if key == "outputFileStem":     self._str_outputFileStem    = value
            if key == "outputFileType":     self._str_outputFileType    = value
            if key == "sliceToConvert":     self._str_sliceToConvert    = value
            if key == "frameToConvert":     self._str_frameToConvert    = value
            if key == "showSlices":         self._b_showSlices          = value

        if self._str_frameToConvert.lower() == 'm':
            self._b_convertMiddleFrame = True
        elif len(self._str_frameToConvert):
            self._frameToConvert = int(self._str_frameToConvert)

        if self._str_sliceToConvert.lower() == 'm':
            self._b_convertMiddleSlice = True
        elif len(self._str_sliceToConvert):
            self._sliceToConvert = int(self._str_sliceToConvert)

        str_fileName, str_fileExtension  = os.path.splitext(self._str_outputFileStem)
        if len(self._str_outputFileType):
            str_fileExtension            = '.%s' % self._str_outputFileType

        if len(str_fileExtension) and not len(self._str_outputFileType):
            self._str_outputFileType     = str_fileExtension

        if not len(self._str_outputFileType) and not len(str_fileExtension):
            self._str_outputFileType     = '.png'

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

    def slice_save(self, astr_outputFile):
        '''
        Processes/saves a single slice.

        ARGS

        o astr_output
        The output filename to save the slice to.

        '''
        self._log('Outputfile = %s\n' % astr_outputFile)
        pylab.imsave(astr_outputFile, self._Mnp_2Dslice, cmap = cm.Greys_r)


class med2image_dcm(med2image):
    '''
    Sub class that handles DICOM data.
    '''
    def __init__(self, **kwargs):
        med2image.__init__(self, **kwargs)

        l_dcmFileNames = glob.glob('*.dcm')
        slices         = len(l_dcmFileNames)

        if self._b_convertMiddleSlice:
            self._sliceToConvert = int(slices/2)
            self._dcm            = dicom.read_file(l_dcmFileNames[self._sliceToConvert])
            self._str_inputFile  = l_dcmFileNames[self._sliceToConvert]
            str_outputFile       = l_dcmFileNames[self._sliceToConvert]
            if not self._str_outputFileStem.startswith('%'):
                self._str_outputFileStem, ext = os.path.splitext(l_dcmFileNames[self._sliceToConvert])
        else:
            self._dcm = dicom.read_file(self._str_inputFile)
        if self._str_outputFileStem.startswith('%'):
            str_spec = self._str_outputFileStem
            self._str_outputFileStem = ''
            for key in str_spec.split('%')[1:]:
                str_fileComponent = ''
                if key == 'inputFile':
                    str_fileName, str_ext = os.path.splitext(self._str_inputFile) 
                    str_fileComponent = str_fileName
                else:
                    str_fileComponent = eval('self._dcm.%s' % key)
                    str_fileComponent = med2image.urlify(str_fileComponent)
                if not len(self._str_outputFileStem):
                    self._str_outputFileStem = str_fileComponent
                else:
                    self._str_outputFileStem = self._str_outputFileStem + '-' + str_fileComponent
        image = self._dcm.pixel_array
        self._Mnp_2Dslice = image

    def run(self):
        '''
        Runs the DICOM conversion based on internal state.
        '''
        self._log('Converting DICOM image.\n')
        self._log('PatientName:                                %s\n' % self._dcm.PatientName)
        self._log('PatientAge:                                 %s\n' % self._dcm.PatientAge)
        self._log('PatientSex:                                 %s\n' % self._dcm.PatientSex)
        self._log('PatientID:                                  %s\n' % self._dcm.PatientID)
        self._log('SeriesDescription:                          %s\n' % self._dcm.SeriesDescription)
        self._log('ProtocolName:                               %s\n' % self._dcm.ProtocolName)
        if self._b_convertMiddleSlice:
            self._log('Converting middle slice in DICOM series:    %d\n' % self._sliceToConvert)


        misc.mkdir(self._str_outputDir)
        str_outputFile = '%s/%s.%s' % (self._str_outputDir,
                                       self._str_outputFileStem,
                                       self._str_outputFileType)
        self.slice_save(str_outputFile)

class med2image_nii(med2image):
    '''
    Sub class that handles NIfTI data.
    '''

    def __init__(self, **kwargs):
        med2image.__init__(self, **kwargs)
        nimg = nib.load(self._str_inputFile)
        data = nimg.get_data()
        if data.ndim == 4:
            self._Vnp_4DVol     = data
            self._b_4D          = True
        if data.ndim == 3:
            self._Vnp_3DVol     = data
            self._b_3D          = True

    def run(self):
        '''
        Runs the NIfTI conversion based on internal state.
        '''

        self._log('About to perform NifTI to %s conversion...\n' %
                  self._str_outputFileType)

        frames     = 1
        frameStart = 0
        frameEnd   = 0

        sliceStart = 0
        sliceEnd   = 0

        if self._b_4D:
            self._log('4D volume detected.\n')
            frames = self._Vnp_4DVol.shape[3]
        if self._b_3D:
            self._log('3D volume detected.\n')

        if self._b_convertMiddleFrame:
            self._frameToConvert = int(frames/2)

        if self._frameToConvert == -1:
            frameEnd    = frames
        else:
            frameStart  = self._frameToConvert
            frameEnd    = self._frameToConvert + 1

        for f in range(frameStart, frameEnd):
            if self._b_4D:
                self._Vnp_3DVol = self._Vnp_4DVol[:,:,:,f]
            slices     = self._Vnp_3DVol.shape[2]
            if self._b_convertMiddleSlice:
                self._sliceToConvert = int(slices/2)

            if self._sliceToConvert == -1:
                sliceEnd    = self._Vnp_3DVol.shape[2]
            else:
                sliceStart  = self._sliceToConvert
                sliceEnd    = self._sliceToConvert + 1

            misc.mkdir(self._str_outputDir)
            for i in range(sliceStart, sliceEnd):
                imslice                 = self._Vnp_3DVol[:,:,i]
                # rotate the slice by 90 for conventional display
                self._Mnp_2Dslice       = np.rot90(imslice)

                if self._b_4D:
                    str_outputFile = '%s/%s-frame%03d-slice%03d.%s' % (
                                                            self._str_outputDir,
                                                            self._str_outputFileStem,
                                                            f, i,
                                                            self._str_outputFileType)
                else:
                    str_outputFile = '%s/%s-slice%03d.%s' % (self._str_outputDir,
                                                            self._str_outputFileStem,
                                                            i,
                                                            self._str_outputFileType)
                self.slice_save(str_outputFile)

def synopsis(ab_shortOnly = False):
    scriptName = os.path.basename(sys.argv[0])
    shortSynopsis =  '''
    NAME

	    med2image.py - convert medical images to jpg/png/etc.

    SYNOPSIS

            %s                                   \\
                     -i|--input <inputFile>                \\
                    [-d|--outputDir <outputDir>]           \\
                     -o|--output <outputFileStem>          \\
                    [-t|--outputFileType <outputFileType>] \\
                    [-s|--sliceToConvert <sliceToConvert>] \\
                    [-f|--frameToConvert <frameToConvert>] \\
                    [--showSlices]                         \\
                    [-x|--man]				   \\
		    [-y|--synopsis]

    BRIEF EXAMPLE

	    med2image.py -i slice.dcm -o slice.jpg

    ''' % scriptName

    description =  '''
    DESCRIPTION

        `%s' converts input medical image formatted data to a more
        display friendly format, such as jpg or png.

        Currently understands NIfTI and DICOM input formats.

    ARGS

        -i|--inputFile <inputFile>
        Input file to convert. Typically a DICOM file or a nifti volume.

        [-d|--outputDir <outputDir>]
        The directory to contain the converted output image files.

        -o|--outputFileStem <outputFileStem>
        The output file stem to store conversion. If this is specified
        with an extension, this extension will be used to specify the
        output file type.
        
        SPECIAL CASES:
        For DICOM data, the <outputFileStem> can be set to the value of
        an internal DICOM tag. The tag is specified by preceding the tag
        name with a percent character '%%', so 
        
            -o %%ProtocolName
            
        will use the DICOM 'ProtocolName' to name the output file. Note
        that special characters (like spaces) in the DICOM value are 
        replaced by underscores '_'.
        
        Multiple tags can be specified, for example
        
            -o %%PatientName%%PatientID%%ProtocolName
            
        and the output filename will have each DICOM tag string as 
        specified in order, connected with dashes.
        
        A special %%inputFile is available to specify the input file that
        was read (without extension).

        [-t|--outputFileType <outputFileType>]
        The output file type. If different to <outputFileStem> extension,
        will override extension in favour of <outputFileType>.

        [-s|--sliceToConvert <sliceToConvert>]
        In the case of volume files, the slice (z) index to convert. Ignored
        for 2D input data. If a '-1' is sent, then convert *all* the slices.
        If an 'm' is specified, only convert the middle slice in an input
        volume.

        [-f|--frameToConvert <sliceToConvert>]
        In the case of 4D volume files, the volume (V) containing the
        slice (z) index to convert. Ignored for 3D input data. If a '-1' is
        sent, then convert *all* the frames. If an 'm' is specified, only
        convert the middle frame in the 4D input stack.

        [--showSlices]
        If specified, render/show image slices as they are created.

        [-x|--man]
        Show full help.

        [-y|--synopsis]
        Show brief help.

    EXAMPLES

    NIfTI

    o Convert each slice in a NIfTI volume 'vol.nii' to a jpg called
      'image-sliceXXX.jpg' and store results in a directory called 'out':

    		med2image.py -i vol.nii -d out -o image.jpg -s -1

    o Convert only the middle slice in an input volume and store in current
      directory:

    		med2image.py -i vol.nii -o image.jpg -s m

    o Convert a specific slice, i.e. slice 20

    		med2image.py -i vol.nii -o image.jpg -s 20

    DICOM

    o Simply convert a DICOM file called 'slice.dcm' to a jpg called 'slice.jpg':

    		med2image.py -i slice.dcm -o slice.jpg

    o Convert all DICOM in a directory/series

    		for F in *dcm ; do med2image.py -i $F -o ${F}.jpg ; done

    GITHUB

        o See https://github.com/FNNDSC/med2image for more help and source.


    ''' % (scriptName)
    if ab_shortOnly:
        return shortSynopsis
    else:
        return shortSynopsis + description

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="med2view converts an input medical image file to a more conventional graphical format.")
    parser.add_argument("-i", "--inputFile",
                        help="input file",
                        dest='inputFile')
    parser.add_argument("-o", "--outputFileStem",
                        help="output file",
                        default="output.jpg",
                        dest='outputFileStem')
    parser.add_argument("-d", "--outputDir",
                        help="output image directory",
                        dest='outputDir',
                        default='.')
    parser.add_argument("-t", "--outputFileType",
                        help="output image type",
                        dest='outputFileType',
                        default='')
    parser.add_argument("-s", "--sliceToConvert",
                        help="slice to convert (for 3D data)",
                        dest='sliceToConvert',
                        default='-1')
    parser.add_argument("-f", "--frameToConvert",
                        help="frame to convert (for 4D data)",
                        dest='frameToConvert',
                        default='-1')
    parser.add_argument("--printElapsedTime",
                        help="print program run time",
                        dest='printElapsedTime',
                        action='store_true',
                        default=False)
    parser.add_argument('--showSlices',
                        help="show slices that are converted",
                        dest='showSlices',
                        action='store_true',
                        default='False')
    parser.add_argument("-x", "--man",
                        help="man",
                        dest='man',
                        action='store_true',
                        default=False)
    parser.add_argument("-y", "--synopsis",
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

    str_outputFileStem, str_outputFileExtension     = os.path.splitext(args.outputFileStem)
    if len(str_outputFileExtension):
        str_outputFileExtension = str_outputFileExtension.split('.')[1]
    try:
        str_inputFileStem,  str_inputFileExtension      = os.path.splitext(args.inputFile)
    except:
        print(synopsis(False))
        sys.exit(1)
    
    if not len(args.outputFileType) and len(str_outputFileExtension):
        args.outputFileType = str_outputFileExtension

    if len(str_outputFileExtension):
        args.outputFileStem = str_outputFileStem

    b_niftiExt           = (str_inputFileExtension   == '.nii'    or \
                            str_inputFileExtension   == '.gz')
    b_dicomExt           =  str_inputFileExtension   == '.dcm'
    if b_niftiExt:
        C_convert     = med2image_nii(
                                inputFile         = args.inputFile,
                                outputDir         = args.outputDir,
                                outputFileStem    = args.outputFileStem,
                                outputFileType    = args.outputFileType,
                                sliceToConvert    = args.sliceToConvert,
                                frameToConvert    = args.frameToConvert,
                                showSlices        = args.showSlices
                            )

    if b_dicomExt:
        C_convert   = med2image_dcm(
                                inputFile         = args.inputFile,
                                outputDir         = args.outputDir,
                                outputFileStem    = args.outputFileStem,
                                outputFileType    = args.outputFileType,
                                sliceToConvert    = args.sliceToConvert,
                             )


    # And now run it!
    misc.tic()
    C_convert.run()
    if args.printElapsedTime: print("Elapsed time = %f seconds" % misc.toc())
    sys.exit(0)




