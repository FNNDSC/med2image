# med2image
<tt>med2image</tt> is a simple Python utility that converts medical image formatted files to more visual friendly ones, such as <tt>png</tt> and <tt>jpg</tt>.

Currently, NIfTI and DICOM input formats are understood, while any graphical output type that is supported by <tt>matplotlib</tt> can be generated.

## Dependencies
Make sure that the following dependencies are installed on the host system:

* nibabel (to read NIfTI files)
* pydicom (to read DICOM files)
* matplotlib (to save data in various image formats)

## Command line arguments

        -i|--inputFile <inputFile>
        Input file to convert. Typically a DICOM file or a nifti volume.

        [-d|--outputDir <outputDir>]
        The directory to contain the converted output image files.

        -o|--outputFileStem <outputFileStem>
        The output file stem to store conversion. If this is specified
        with an extension, this extension will be used to specify the
        output file type.

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

        [--man|--synopsis]
        Show either full help or short synopsis.

## NIfTI conversion 
Both 3D and 4D NIfTI input data are understood. In the case of 4D NIfTI, a specific <b>frame</b> can be specified in conjunction with a specific <b>slice</b> index. In most cases, only a <b>slice</b> is required since most NIfTI data is 3D. Furthermore, all slices can be converted, or just the middle one.

### Examples
### All slices in a volume
To convert <b>all</b> slices in an input NIfTI volume called <tt>input.nii</tt>, to save the results in a directory called <tt>out</tt> and to use as output the file stem name <tt>vol</tt>, do

 ```med2image.py -i input.nii -d out -o vol --outputFileType jpg --sliceToConvert -1```

This will create the following files in <tt>out</tt>

```
vol-slice000.jpg
vol-slice001.jpg
vol-slice002.jpg
vol-slice003.jpg
vol-slice004.jpg
vol-slice005.jpg
vol-slice006.jpg
vol-slice007.jpg
...
vol-slice049.jpg
vol-slice050.jpg
vol-slice051.jpg
vol-slice052.jpg
vol-slice053.jpg
```

### Convert only a single slice
Mostly, you'll probably only want the "middle" slice in a volume will converted (for example to generate a representative thumbnail of the volume). To do this, simply specify a <tt>m</tt> to <tt>--sliceToConvert</tt>

 ```med2image.py -i input.nii -d out -o vol --outputFileType jpg --sliceToConvert m```

Alternatively a specific slice index can be converted. Use

 ```med2image.py -i input.nii -d out -o vol --outputFileType jpg --sliceToConvert 20```

to convert only the 20th slice of the volume.

## DICOM conversion
DICOM conversion is currently file-by-file since DICOM data is typically single-file-per-slice. 

### Convert a single DICOM file
To convert a single DICOM file called <tt>slice.dcm</tt>, do:

```med2image.py -i slice.dcm -d out -o slice --outputFileType jpg```

which will create a single file, <tt>slice.jpg</tt> in the directory <tt>out</tt>.

### Convert all DICOMS in a directory/series
To convert all the DICOMS in a directory, simply run the script appropriately over each file in the directory. Assuming that you are in a directory with DICOM files all ending in <tt>dcm</tt>, simply run

```for F in *dcm ; do med2image.py -i $F -d out -o $F --outputFileType jpg ; done```

to create an output directory called <tt>out</tt> which will contain every DICOM file in the original directory, keeping the name of each file identical to the input DICOM, but with a <tt>jpg</tt> extension attached.

