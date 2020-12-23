med2image 2.2.6
==================

Quick Overview
--------------

-  Convert ``DICOM`` or ``NIfTI`` inputs to ``jpg`` or ``png`` outputs.

Overview
--------

``med2image`` is a simple Python3 utility that converts medical image formatted files (such as ``DICOM`` and ``NifTI``) to more web friendly ones, such as ``png`` and ``jpg``.

Currently, ``NIfTI`` and ``DICOM`` input formats are understood, while any graphical output type that is supported by matplotlib can be generated.

At present ``med2image`` does not convert ``DICOM`` to ``NifTI``, but this is planned for a future release.

Dependencies
------------

Make sure that the following dependencies are installed on your host system (or even better, a ``python3`` virtual env):

-  ``pfmisc`` : (a general miscellaneous module for color support, etc)
-  ``nibabel`` : (to read NIfTI files)
-  ``pydicom`` : (to read DICOM files)
-  ``matplotlib`` : (to save data in various image formats)
-  ``pillow`` : (to save data in ``jpg`` format)

Assumptions
-----------

This document assumes UNIX conventions and a ``bash`` shell. The script should work fine under Windows, but we have not actively tested on that platform -- our dev envs are Linux Ubuntu and macOS.

Installation
~~~~~~~~~~~~

Python module
~~~~~~~~~~~~~

One method of installing this script and all of its dependencies is by fetching it from `PyPI <https://pypi.org/project/med2image/>`_.

.. code:: bash

        pip3 install med2image

Should you get an error about ``python3-tk`` not installed, simply do (for example on Ubuntu):

.. code:: bash

        sudo apt-get update
        sudo apt-get install -y python3-tk

Docker container
~~~~~~~~~~~~~~~~

We also offer a docker container of ``med2image`` as a ChRIS-conformant platform plugin here https://github.com/FNNDSC/pl-med2img -- please consult that page for information on running the dockerized container. The containerized version exposes a similar CLI and functionality as this module.

How to Use
----------

``med2image`` needs at a minimum the following required command line arguments:

- ``-i | --inputFile <inputFile>`` : Input file to convert. Typically a ``DICOM`` file or a ``NifTI`` volume.

- ``-d | --outputDir <outputDir> :`` The directory to contain the converted output image files.

**Example:**

.. code:: bash

    # Convert a NifTI file 'vol.nii' to JPEG and store
    # the results in a dirctory called 'out'.
    # The 'out' dir will contain a set of JPEG
    # images of form 'output-sliceXXX.jpg'.

    med2image -i vol.nii -d out

.. code:: bash

    # Convert a DICOM file 'file.dcm' to JPEG and store
    # the results in a dirctory called 'out'.
    # The 'out' dir will contain a set of JPEG
    # images of form 'output-sliceXXX.jpg'.

    # NOTE! If the directory containing 'file.dcm' contains
    # multiple DICOM files, *ALL* of these will be converted
    # to JPEG. See later for only converting a *single*
    # DICOM file.

    med2image -i file.dcm -d out

``NIfTI`` details
-----------------

**NOTE:** ``NifTI`` is typically a *volume* format. One ``NIfTI`` (``.nii``) volume contains multiple *slices*. Converting a ``NifTI`` volume results in multiple ``.jpg`` or ``.png`` results.

- ``NIfTI`` input data can be in 2 forms:

  - 3D : The ``.nii`` volume contains multiple 2D slices

  - 4D : The ``.nii`` file contains multiple 3D volumes that each contain multiple 2D slices

- ``med2image`` understands both types of inputs.

Pull ``NIfTI``
~~~~~~~~~~~~~~

The input should be a ``NIfTI`` volume with extension ``.nii``. We provide a sample volume here https://github.com/FNNDSC/SAG-anon-nii.git

- Clone this repository (``SAG-anon-nii``) to your local computer.

.. code:: bash

    git clone https://github.com/FNNDSC/SAG-anon-nii.git

Convert ``NIfTI``
~~~~~~~~~~~~~~~~~

**NOTE:**

- If ``--outputDir | -d`` is not provided, outputs are created in the *current* directory.
- if ``--sliceToConvert`` is not provided, *all* the slices of the ``.nii`` volume are converted.

Both 3D and 4D ``NIfTI`` input data are understood. In the case of 4D ``NIfTI``, a specific frame (``--frameToConvert``) can be additionally provided in conjunction with a specific slice index. Conversion options include:

- *all* slices (default)
- *middle* slice only, with the CLI ``--sliceToConvert m``
- *someSpecificSlice*, with the CLI ``--sliceToConvert <N>``

CASE 1: All slices in a volume
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Now, let's convert all slices in the input ``NIfTI`` volume ``SAG-anon.nii``, and save the results to a nested subdir ``nifti-results/all-slices``. We'll use as output file name stem ``sample`` and convert to ``jpg``.

Assuming you have cloned the ``SAG-anon-nii`` repo and assuming that you have ``med2image`` on your UNIX shell path,

.. code:: bash

    med2image -i SAG-anon-nii/SAG-anon.nii                 \
              -d nifti-results/all-slices                  \
              -o sample.jpg -s -1

or equivalently and more verbosely,

.. code:: bash

    med2image --inputFile SAG-anon-nii/SAG-anon.nii         \
              --outputDir nifti-results/all-slices          \
              --outputFileStem sample  --outputFileType jpg \
              --sliceToConvert -1

resulting in

::

    nifti-results/all-slices/sample-slice000.jpg
    nifti-results/all-slices/sample-slice001.jpg
    nifti-results/all-slices/sample-slice002.jpg
    nifti-results/all-slices/sample-slice003.jpg
    ...
    nifti-results/all-slices/sample-slice188.jpg
    nifti-results/all-slices/sample-slice189.jpg
    nifti-results/all-slices/sample-slice190.jpg
    nifti-results/all-slices/sample-slice191.jpg

Note that even if the nested output directory structure does not exist, ``med2image`` will create it for you.

Case 2: Convert only a single slice
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Often times, you might only want to convert the "middle" slice in a volume (for example to generate a representative thumbnail of the volume). To do this, simply specify an ``m`` to ``--sliceToConvert`` (or ``-s m``):

.. code:: bash

    med2image -i SAG-anon-nii/SAG-anon.nii    \
              -d nifti-results/middle-slice   \
              -o sample --outputFileType jpg  \
              --sliceToConvert m

resulting in

::

    nifti-results/middle-slice/sample-slice096.jpg

Alternatively a specific slice index can be converted. Use

.. code:: bash

    med2image -i SAG-anon-nii/SAG-anon.nii    \
              -d nifti-results/specific-slice \
              -o sample                       \
              --outputFileType jpg            \
              --sliceToConvert 20

to convert only the 20th slice of the volume.

resulting in

::

    nifti-results/specific-slice/sample-slice020.jpg

``DICOM``
---------

**NOTE:** One ``DICOM`` (``.dcm``) file typically corresponds to one ``.png`` or ``.jpg`` file (slice).

Pull DICOM
~~~~~~~~~~

The input should be a ``DICOM`` file usually with extension ``.dcm``

We provide a sample directory of ``.dcm`` images here ``FNNDSC/SAG-anon``. (https://github.com/FNNDSC/SAG-anon.git)

- Clone this repository (``SAG-anon``) to your local computer.

.. code:: bash

    git clone https://github.com/FNNDSC/SAG-anon.git

Convert ``DICOM``
~~~~~~~~~~~~~~~~~

**NOTE:**

- If ``--outputDir | -d`` is not provided, any output(s) are created in the current directory.
- if ``--sliceToConvert`` argument is not specified and if mutiple ``dcm`` files are contained in the input directory with the ``DICOM`` input, then all the ``.dcm`` files are converted.
- alternatively, specifying a ``--convertOnlySingleDICOM`` will only convert the DICOM file specified with the ``--inputFile`` flag.


Convert all DICOMS in a directory/series
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To convert all the ``DICOM`` files in a directory, simply specify either ``--sliceToConvert -1`` (or just leave out the argument/value pair completely):

.. code:: bash

    med2image -i SAG-anon/0001-1.3.12.2.1107.5.2.19.45152.2013030808110258929186035.dcm   \
              -d dicom-results/all-slices      \
              -o sample                        \
              --outputFileType jpg             \
              --sliceToConvert -1

    # OR equivalently

    med2image -i SAG-anon/0001-1.3.12.2.1107.5.2.19.45152.2013030808110258929186035.dcm  \
              -d dicom-results/all-slices      \
              -o sample                        \
              --outputFileType jpg


resulting in

::

    dicom-results/all-slices/sample-slice000.jpg
    dicom-results/all-slices/sample-slice001.jpg
    dicom-results/all-slices/sample-slice002.jpg
    dicom-results/all-slices/sample-slice003.jpg
    ...
    dicom-results/all-slices/sample-slice188.jpg
    dicom-results/all-slices/sample-slice189.jpg
    dicom-results/all-slices/sample-slice190.jpg
    dicom-results/all-slices/sample-slice191.jpg

Convert a single ``DICOM`` file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Mostly, you'll probably only want to convert the "middle" slice in a DICOM directory (for example to generate a representative thumbnail of the directory). To do this, simply specify a `m` to --sliceToConvert (or `-s m`)

.. code:: bash

    med2image -i SAG-anon/0001-1.3.12.2.1107.5.2.19.45152.2013030808110258929186035.dcm    \
              -d dicom-results/middle-slice  \
              -o sample --outputFileType jpg \
              --sliceToConvert m

resulting in

::

    dicom-results/middle-slice/sample.jpg

Note that even though the first slice in the ``SAG-anon`` directory was supplied to the script, ``med2image`` nonetheless found and converted the middle slice in the directory.

Alternatively a specific slice index can be converted. Use

.. code:: bash

    med2image -i SAG-anon/0001-1.3.12.2.1107.5.2.19.45152.2013030808110258929186035.dcm     \
              -d dicom-results/specific-slice  \
              -o sample --outputFileType jpg   \
              --sliceToConvert 20

resulting in

::

    dicom-results/specific-slice/sample.jpg

Again, even though the first slice was supplied to the script, ``med2image`` selected and converted the 20th slice in the directory.

Special Cases
^^^^^^^^^^^^^

For ``DICOM`` data, the ``<outputFileStem>`` can optionally be set to the value of an internal ``DICOM`` tag. The tag is specified by preceding the tag name with a percent character ``%``, so

- ``-o %PatientID``

will use the ``DICOM`` ``PatientID`` to name the output file. Note that special characters (like spaces) in the ``DICOM`` value are replaced by underscores '_'.

.. code:: bash

    med2image -i SAG-anon/0001-1.3.12.2.1107.5.2.19.45152.2013030808110258929186035.dcm   \
              -d dicom-results/tags         \
              -o %PatientID.jpg -s m

This will create the following file in the ``tags`` sub-directory within ``dicom-results`` directory.

.. code:: bash

    dicom-results/tags/1449c1d.jpg

Multiple tags can be specified, for example

- ``-o %PatientName%PatientID%ProtocolName``

and the output filename will have each ``DICOM`` tag string as specified in order, connected with dashes.

.. code:: bash

    med2image -i SAG-anon/0001-1.3.12.2.1107.5.2.19.45152.2013030808110258929186035.dcm \
              -d dicom-results/tags                        \
              -o %PatientName%PatientID%ProtocolName.jpg   \
              -s m

This will create the following file in the ``tags`` sub-directory within ``dicom-results`` directory.

.. code:: bash

    dicom-results/tags/anonymized-1449c1d-SAG_MPRAGE_220_FOV.jpg


Multiple Direction Reslicing
----------------------------

By default, only the slice (or slices) in the acquisition direction are converted. However, by passing a `--reslice` to the script, all dimensions are converted. Since the script does not know the anatomical orientation of the image, the directions are simply labeled ``x``, ``y``, and ``z``.

The ``z`` direction is the original acquistion (slice) direction, while ``x`` and ``y`` correspond to planes normal to the row and column directions. Converted images are stored in subdirectories labeled ``x``, ``y``, and ``z``.

No interpolation in the ``x`` and ``y`` directions is performed. This often results in ugly images!

**NOTE:** In case of ``DICOM`` images, the `--reslice` option will work only if all slices in the directory are converted, i.e. converting with ``--sliceToConvert -1``

Special Operations
------------------

``med2image`` also supports some very basic image processing through a ``--func <functionName>`` CLI, which applies some canned transformation on the image. Currently supported is

::

    --func invertIntensities

which simply inverts the contrast intensity of the source image. Additional functions are planned for future releases.

Command Line Arguments
----------------------

::

        -i|--inputFile <inputFile>
        Input file to convert. Typically a DICOM file or a nifti volume.

        [-I|--inputDir <inputDir>]
        If specified, a directory containing the <inputFile>. In this case
        <inputFile> should be specified as relative to <inputDir>.

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

        [--convertOnlySingleDICOM]
        If specified, will only convert the single DICOM specified by the
        '--inputFile' flag. This is useful for the case when an input
        directory has many DICOMS but you specifially only want to convert
        the named file. By default the script assumes that multiple DICOMS
        should be converted en mass otherwise.

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

        [--func <functionName>]
        Apply the specified transformation function before saving. Currently
        support functions:

            * invertIntensities
              Inverts the contrast intensity of the source image.

        [--reslice]
        For 3D data only. Assuming [i,j,k] coordinates, the default is to save
        along the 'k' direction. By passing a --reslice image data in the 'i' and
        'j' directions are also saved. Furthermore, the <outputDir> is subdivided into
        'slice' (k), 'row' (i), and 'col' (j) subdirectories.

        [-x|--man]
        Show full help.

        [-y|--synopsis]
        Show brief help.
