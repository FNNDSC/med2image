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
import os
import glob
import numpy as np
import re

# System dependency imports
import nibabel as nib
import dicom
import pylab
import matplotlib.cm as cm

# Project specific imports
from . import error
from . import message as msg
from . import systemMisc as misc


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
        'dcmInsertionFail': {
            'action'        : 'attempting insert DICOM into volume structure, ',
            'error'         : 'a dimension mismatch occurred. This DICOM file is of different image size to the rest.',
            'exitCode'      : 20},
        'ProtocolNameTag': {
            'action'        : 'attempting to parse DICOM header, ',
            'error'         : 'the DICOM file does not seem to contain a ProtocolName tag.',
            'exitCode'      : 30},
        'PatientNameTag': {
            'action': 'attempting to parse DICOM header, ',
            'error': 'the DICOM file does not seem to contain a PatientName tag.',
            'exitCode': 30},
        'PatientAgeTag': {
            'action': 'attempting to parse DICOM header, ',
            'error': 'the DICOM file does not seem to contain a PatientAge tag.',
            'exitCode': 30},
        'PatientNameSex': {
            'action': 'attempting to parse DICOM header, ',
            'error': 'the DICOM file does not seem to contain a PatientSex tag.',
            'exitCode': 30},
        'PatientIDTag': {
            'action': 'attempting to parse DICOM header, ',
            'error': 'the DICOM file does not seem to contain a PatientID tag.',
            'exitCode': 30},
        'SeriesDescriptionTag': {
            'action': 'attempting to parse DICOM header, ',
            'error': 'the DICOM file does not seem to contain a SeriesDescription tag.',
            'exitCode': 30}
    }
        
    def log(self, *args):
        '''
        get/set the internal pipeline log message object.

        Caller can further manipulate the log object with object-specific
        calls.
        '''
        if len(args):
            self._log = args[0]
        else:
            return self._log

    def name(self, *args):
        '''
        get/set the descriptive name text of this object.
        '''
        if len(args):
            self.__name = args[0]
        else:
            return self.__name

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
        self._log                       = msg.Message()
        self._log._b_syslog             = True
        self.__name                     = "med2image"

        # Directory and filenames
        self._str_workingDir            = ''
        self._str_inputFile             = ''
        self._str_outputFileStem        = ''
        self._str_outputFileType        = ''
        self._str_outputDir             = ''
        self._str_inputDir              = ''

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
        self._dcmList                   = []

        # A logger
        self._log                       = msg.Message()
        self._log.syslog(True)

        # Flags
        self._b_showSlices              = False
        self._b_convertMiddleSlice      = False
        self._b_convertMiddleFrame      = False
        self._b_reslice                 = False
        self.func                       = None #transformation function

        for key, value in kwargs.items():
            if key == "inputFile":          self._str_inputFile         = value
            if key == "outputDir":          self._str_outputDir         = value
            if key == "outputFileStem":     self._str_outputFileStem    = value
            if key == "outputFileType":     self._str_outputFileType    = value
            if key == "sliceToConvert":     self._str_sliceToConvert    = value
            if key == "frameToConvert":     self._str_frameToConvert    = value
            if key == "showSlices":         self._b_showSlices          = value
            if key == 'reslice':            self._b_reslice             = value

        if self._str_frameToConvert.lower() == 'm':
            self._b_convertMiddleFrame = True
        elif len(self._str_frameToConvert):
            self._frameToConvert = int(self._str_frameToConvert)

        if self._str_sliceToConvert.lower() == 'm':
            self._b_convertMiddleSlice = True
        elif len(self._str_sliceToConvert):
            self._sliceToConvert = int(self._str_sliceToConvert)

        self._str_inputDir               = os.path.dirname(self._str_inputFile)
        if not len(self._str_inputDir): self._str_inputDir = '.'
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

    def get_output_file_name(self, **kwargs):
        index   = 0
        frame   = 0
        str_subDir  = ""
        for key,val in kwargs.items():
            if key == 'index':  index       = val 
            if key == 'frame':  frame       = val
            if key == 'subDir': str_subDir  = val
        
        if self._b_4D:
            str_outputFile = '%s/%s/%s-frame%03d-slice%03d.%s' % (
                                                    self._str_outputDir,
                                                    str_subDir,
                                                    self._str_outputFileStem,
                                                    frame, index,
                                                    self._str_outputFileType)
        else:
            str_outputFile = '%s/%s/%s-slice%03d.%s' % (
                                        self._str_outputDir,
                                        str_subDir,
                                        self._str_outputFileStem,
                                        index,
                                        self._str_outputFileType)
        return str_outputFile

    def dim_save(self, **kwargs):
        dims            = self._Vnp_3DVol.shape
        self._log('Image volume logical (i, j, k) size: %s\n' % str(dims))
        str_dim         = 'z'
        b_makeSubDir    = False
        b_rot90         = False
        indexStart      = -1
        indexStop       = -1
        for key, val in kwargs.items():
            if key == 'dimension':  str_dim         = val
            if key == 'makeSubDir': b_makeSubDir    = val
            if key == 'indexStart': indexStart      = val 
            if key == 'indexStop':  indexStop       = val
            if key == 'rot90':      b_rot90         = val
        
        str_subDir  = ''
        if b_makeSubDir: 
            str_subDir = str_dim
            misc.mkdir('%s/%s' % (self._str_outputDir, str_subDir))

        dim_ix = {'x':0, 'y':1, 'z':2}
        if indexStart == 0 and indexStop == -1:
            indexStop = dims[dim_ix[str_dim]]

        for i in range(indexStart, indexStop):
            if str_dim == 'x':
                self._Mnp_2Dslice = self._Vnp_3DVol[i, :, :]
            elif str_dim == 'y':
                self._Mnp_2Dslice = self._Vnp_3DVol[:, i, :]
            else:
                self._Mnp_2Dslice = self._Vnp_3DVol[:, :, i]
            self.process_slice(b_rot90)
            str_outputFile = self.get_output_file_name(index=i, subDir=str_subDir)
            if str_outputFile.endswith('dcm'):
                self._dcm = self._dcmList[i]
            self.slice_save(str_outputFile)

    def process_slice(self, b_rot90=None):
        '''
        Processes a single slice.
        '''
        if b_rot90:
            self._Mnp_2Dslice = np.rot90(self._Mnp_2Dslice)
        if self.func == 'invertIntensities':
            self.invert_slice_intensities()

    def slice_save(self, astr_outputFile):
        '''
        Saves a single slice.

        ARGS

        o astr_output
        The output filename to save the slice to.
        '''
        self._log('Outputfile = %s\n' % astr_outputFile)
        fformat = astr_outputFile.split('.')[-1]
        if fformat == 'dcm':
            if self._dcm:
                self._dcm.pixel_array.flat = self._Mnp_2Dslice.flat
                self._dcm.PixelData = self._dcm.pixel_array.tostring()
                self._dcm.save_as(astr_outputFile)
            else:
                raise ValueError('dcm output format only available for DICOM files')
        else:
            pylab.imsave(astr_outputFile, self._Mnp_2Dslice, format=fformat, cmap = cm.Greys_r)

    def invert_slice_intensities(self):
        '''
        Inverts intensities of a single slice.
        '''
        self._Mnp_2Dslice = self._Mnp_2Dslice*(-1) + self._Mnp_2Dslice.max()


class med2image_dcm(med2image):
    '''
    Sub class that handles DICOM data.
    '''
    def __init__(self, **kwargs):
        med2image.__init__(self, **kwargs)

        self.l_dcmFileNames = sorted(glob.glob('%s/*.dcm' % self._str_inputDir))
        self.slices         = len(self.l_dcmFileNames)

        if self._b_convertMiddleSlice:
            self._sliceToConvert = int(self.slices/2)
            self._dcm            = dicom.read_file(self.l_dcmFileNames[self._sliceToConvert],force=True)
            self._str_inputFile  = self.l_dcmFileNames[self._sliceToConvert]
            if not self._str_outputFileStem.startswith('%'):
                self._str_outputFileStem, ext = os.path.splitext(self.l_dcmFileNames[self._sliceToConvert])
        if not self._b_convertMiddleSlice and self._sliceToConvert != -1:
            self._dcm = dicom.read_file(self.l_dcmFileNames[self._sliceToConvert],force=True)
            self._str_inputFile = self.l_dcmFileNames[self._sliceToConvert]
        else:
            self._dcm = dicom.read_file(self._str_inputFile,force=True)
        if self._sliceToConvert == -1:
            self._b_3D = True
            self._dcm = dicom.read_file(self._str_inputFile,force=True)
            image = self._dcm.pixel_array
            shape2D = image.shape
            #print(shape2D)
            self._Vnp_3DVol = np.empty( (shape2D[0], shape2D[1], self.slices) )
            i = 0
            for img in self.l_dcmFileNames:
                self._dcm = dicom.read_file(img,force=True)
                image = self._dcm.pixel_array
                self._dcmList.append(self._dcm)
                #print('%s: %s\n' % (img, image.shape))
                try:
                    self._Vnp_3DVol[:,:,i] = image
                except Exception as e:
                    error.fatal(self, 'dcmInsertionFail', '\nFor input DICOM file %s\n%s\n' % (img, str(e)))
                i += 1
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

    def sanitize(value):
        # convert to string and remove trailing spaces
        tvalue = str(value).strip()
        # only keep alpha numeric characters and replace the rest by "_"
        svalue = "".join(character if character.isalnum() else '.' for character in tvalue)
        if not svalue:
            svalue = "no value provided"
        return svalue

    def processDicomField(self, dcm, field):
        value = "no value provided"
        if field in dcm:
            value = self.sanitize(dcm.data_element(field).value)
        return value

    def run(self):
        '''
        Runs the DICOM conversion based on internal state.
        '''
        self._log('Converting DICOM image.\n')
        try:
            self._log('PatientName:                                %s\n' % self._dcm.PatientName)
        except AttributeError:
            self._log('PatientName:                                %s\n' % 'PatientName not found in DCM header.')
            error.warn(self, 'PatientNameTag')
        try:
            self._log('PatientAge:                                 %s\n' % self._dcm.PatientAge)
        except AttributeError:
            self._log('PatientAge:                                 %s\n' % 'PatientAge not found in DCM header.')
            error.warn(self, 'PatientAgeTag')
        try:
            self._log('PatientSex:                                 %s\n' % self._dcm.PatientSex)
        except AttributeError:
            self._log('PatientSex:                                 %s\n' % 'PatientSex not found in DCM header.')
            error.warn(self, 'PatientSexTag')
        try:
            self._log('PatientID:                                  %s\n' % self._dcm.PatientID)
        except AttributeError:
            self._log('PatientID:                                  %s\n' % 'PatientID not found in DCM header.')
            error.warn(self, 'PatientIDTag')
        try:
            self._log('SeriesDescription:                          %s\n' % self._dcm.SeriesDescription)
        except AttributeError:
            self._log('SeriesDescription:                          %s\n' % 'SeriesDescription not found in DCM header.')
            error.warn(self, 'SeriesDescriptionTag')
        try:
            self._log('ProtocolName:                               %s\n' % self._dcm.ProtocolName)
        except AttributeError:
            self._log('ProtocolName:                               %s\n' % 'ProtocolName not found in DCM header.')
            error.warn(self, 'ProtocolNameTag')

        if self._b_convertMiddleSlice:
            self._log('Converting middle slice in DICOM series:    %d\n' % self._sliceToConvert)

        l_rot90 = [ True, True, False ]
        misc.mkdir(self._str_outputDir)
        if not self._b_3D:
            str_outputFile = '%s/%s.%s' % (self._str_outputDir,
                                        self._str_outputFileStem,
                                        self._str_outputFileType)
            self.process_slice()
            self.slice_save(str_outputFile)
        if self._b_3D:
            rotCount = 0
            if self._b_reslice:
                for dim in ['x', 'y', 'z']:
                    self.dim_save(dimension = dim, makeSubDir = True, rot90 = l_rot90[rotCount], indexStart = 0, indexStop = -1)
                    rotCount += 1
            else:
                self.dim_save(dimension = 'z', makeSubDir = False, rot90 = False, indexStart = 0, indexStop = -1)

                
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
                sliceEnd    = -1
            else:
                sliceStart  = self._sliceToConvert
                sliceEnd    = self._sliceToConvert + 1

            misc.mkdir(self._str_outputDir)
            if self._b_reslice:
                for dim in ['x', 'y', 'z']:
                    self.dim_save(dimension = dim, makeSubDir = True, indexStart = sliceStart, indexStop = sliceEnd, rot90 = True)
            else:
                self.dim_save(dimension = 'z', makeSubDir = False, indexStart = sliceStart, indexStop = sliceEnd, rot90 = True)



