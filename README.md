# med2image

## Quick Overview

* Convert DICOM or NIfTI to jpg or png

## Overview

<tt>med2image</tt> is a simple Python utility that converts medical image formatted files to more visual friendly ones, such as <tt>png</tt> and <tt>jpg</tt>.

Currently, NIfTI and DICOM input formats are understood, while any graphical output type that is supported by <tt>matplotlib</tt> can be generated.

## Dependencies
Make sure that the following dependencies are installed on the host system:

* nibabel (to read NIfTI files)
* pydicom (to read DICOM files)
* matplotlib (to save data in various image formats)

### FNNDSC script checkout

An alternate method of installing this script and <b>some</b> of its internal dependencies (<tt>error.py, dgmsocket.py, message.py</tt>) is to checkout the FNNDSC github scripts repository, https://github.com/FNNDSC/scripts.

## Command line arguments

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
        name with a percent character '%', so

            -o %ProtocolName

        will use the DICOM 'ProtocolName' to name the output file. Note
        that special characters (like spaces) in the DICOM value are
        replaced by underscores '_'.

        Multiple tags can be specified, for example

            -o %PatientName%PatientID%ProtocolName

        and the output filename will have each DICOM tag string as
        specified in order, connected with dashes.

        A special %inputFile is available to specify the input file that
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

        [--reslice]
        For 3D data only. Assuming [i,j,k] coordinates, the default is to save
        along the 'k' direction. By passing a --reslice image data in the 'i' and
        'j' directions are also saved. Furthermore, the <outputDir> is subdivided into
        'slice' (k), 'row' (i), and 'col' (j) subdirectories.

        [-x|--man]
        Show full help.

        [-y|--synopsis]
        Show brief help.

## NIfTI conversion 
Both 3D and 4D NIfTI input data are understood. In the case of 4D NIfTI, a specific <b>frame</b> can be specified in conjunction with a specific <b>slice</b> index. In most cases, only a <b>slice</b> is required since most NIfTI data is 3D. Furthermore, all slices can be converted, or just the middle one.

### Examples
### All slices in a volume
To convert <b>all</b> slices in an input NIfTI volume called <tt>vol.nii</tt>, to save the results in a directory called <tt>out</tt> and to use as output the file stem name <tt>image</tt>, do

 ```med2image.py -i vol.nii -d out -o image.jpg -s -1```

or equivalently and more verbosely,

    med2image.py --inputFile vol.nii     --outputDir out      \
                 --outputFileStem image  --outputFileType jpg \
                 --sliceToConvert -1

This will create the following files in <tt>out</tt>

```
image-slice000.jpg
image-slice001.jpg
image-slice002.jpg
image-slice003.jpg
image-slice004.jpg
image-slice005.jpg
image-slice006.jpg
image-slice007.jpg
...
image-slice049.jpg
image-slice050.jpg
image-slice051.jpg
image-slice052.jpg
image-slice053.jpg
```

### Convert only a single slice
Mostly, you'll probably only want to convert the "middle" slice in a volume (for example to generate a representative thumbnail of the volume). To do this, simply specify a <tt>m</tt> to <tt>--sliceToConvert</tt>

 ```med2image.py -i input.nii -o input.jpg -s m```

or, again, slightly more verbosely and with an outputDirectory specifier

 ```med2image.py -i input.nii -d out -o vol --outputFileType jpg --sliceToConvert m```

Alternatively a specific slice index can be converted. Use

 ```med2image.py -i input.nii -d out -o vol --outputFileType jpg --sliceToConvert 20```

to convert only the 20th slice of the volume.

## DICOM conversion

### Convert a single DICOM file
To convert a single DICOM file called <tt>slice.dcm</tt> to <tt>slice.jpg</tt>, do:

```med2image.py -i slice.dcm -o slice.jpg```

which will create a single file, <tt>slice.jpg</tt> in the current directory.

### Convert all DICOMS in a directory/series
To convert all the DICOMS in a directory, simply specifiy a '-1' to the sliceIndex:

```med2image.py -i inputDir/slice.dcm -d outputDir -o slice.jpg -s -1```

Note that this assumes all the DICOM files in the directory <tt>inputDir</tt> belong to the same series.

## Multiple Direction Reslicing
By default, only the slice (or slices) in the acquisition direction are converted. However, by passing a <tt>-r</tt> to the script, all dimensions are converted. Since the script does not know the anatomical orientation of the image, the directions are simply labeled <tt>x</tt>, <tt>y</tt>, and <tt>z</tt>.

The <tt>z</tt> direction is the original acquistion (slice) direction, while <tt>x</tt> and <tt>y</tt> correspond to planes normal to the row and column directions.

Converted images are stored in subdirectories labeled <tt>x</tt>, <tt>y</tt>, and <tt>z</tt>.


