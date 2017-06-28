#!/usr/bin/env python
#
# NAME
#
#        systemMisc
#
# DESCRIPTION
#
#        The 'systemMisc' module contains some helper functions to
#        facilitate system-type interaction.
#
# HISTORY
#
# 05 April 2006
# o Initial design and coding.
#
# 14 December 2006
# o Added data handling convenience routines
#
# January 2008
# o Miscellaneous text / string handling
#

# System imports
import          os
import          fnmatch
import          sys
import          string
import          re
import          types
from            subprocess      import *
from            io       import StringIO
from            numpy           import *
import          time
import          itertools
# import          popen2, fcntl, select

# For internal timing:
Gtic_start = 0.0

def arr_normalize(arr, *args, **kwargs):
    """
    ARGS
        arr                      array to normalize

    **kargs
        scale = <f_scale>        scale the normalized output by <f_scale>


    DESC
        Given an input array, <arr>, normalize all values to range
        between 0 and 1.

        If specified in the **kwargs, optionally set the scale with <f_scale>.
    """
    f_max = arr.max()
    f_min = arr.min()
    f_range = f_max - f_min
    arr_shifted = arr + -f_min
    arr_norm = arr_shifted / f_range
    for key, value in kwargs.iteritems():
        if key == 'scale': arr_norm *= value
    return arr_norm

def density(a_M, *args, **kwargs):
    """
    ARGS
        a_M                matrix to analyze

        *args[0]           optional mask matrix; if passed, calculate
                           density of a_M using non-zero elements of
                           args[0] as a mask.

    DESC
        Determine the "density" of a passed matrix. Two densities are returned:

            o f_actualDensity -- density of the matrix using matrix values
                                 as "mass"
            o f_binaryDensity -- density of the matrix irrespective of actual
                                 matrix values

        If the passed matrix contains only "ones", the f_binaryDensity will
        be equal to the f_actualDensity.

    """

    rows, cols  = a_M.shape
    a_Mmask     = ones( (rows, cols) )
    if len(args):
        a_Mmask = args[0]

    a_M *= a_Mmask
    # The "binary" density determines the density of nonzero elements,
    # irrespective of their actual value
    f_binaryMass    = float(size(nonzero(a_M)[0]))
    f_actualMass    = a_M.sum()

    f_area          = float(size(nonzero(a_Mmask)[0]))

    f_binaryDensity = f_binaryMass / f_area;
    f_actualDensity = f_actualMass / f_area;
    return f_actualDensity, f_binaryDensity


def cdf(arr, **kwargs):
    """
    ARGS
        arr                array to calculate cumulative distribution function

    **kwargs
        Passed directly to numpy.histogram. Typical options include:
        bins = <num_bins>
        normed = True|False

    DESC
        Determines the cumulative distribution function.
    """
    counts, bin_edges = histogram(arr, **kwargs)
    cdf = cumsum(counts)
    return cdf

def cdf_distribution(a_cdf, a_partitions):
    """
    ARGS
       a_cdf               vector         a vectors of values/observations
       a_partitions        int            the number of partitions

    DESC
        This function returns the indices of a passed cdf such that the
        the range of values across the indices is uniform across the
        number of partitions.

        Imagine you have a range of observations/values, and you'd
        like to partition the observations over 3 ranges. If you simply
        partition the range of values into three evenly spaced groups
        across the domain, you will most likely find all the dynamic range
        of values in each partition is non-uniform.

        By partitioning the cdf, however, the range of values in each
        partition is uniform. The "size" of each partition, however,
        is not.
    """
    f_range = a_cdf[-1] - a_cdf[0]
    f_rangePart = f_range / a_partitions
    lowerBound = a_cdf[0]
    vl = []
    for part in arange(0, a_partitions):
        # Due to possible cumulative rounding errors, relax the tolerance
        # on the final partition:
        if part == a_partitions - 1:
            subset = (a_cdf > lowerBound)
        else:
            subset = (a_cdf > lowerBound) & (a_cdf <= lowerBound + f_rangePart)
        indices = where(subset, 1, 0)
        v = where(indices == 1)
        vl.append(v)
        lowerBound += f_rangePart
    return vl

def com_find(ar_grid):
    """
    Find the center of mass in array grid <ar_grid>. Mass elements
    are grid index values.

    Return an array, in format (x, y), i.e. col, row!
    """
    f_x = 0
    f_y = 0
    f_m = 0

    for i in range(len(ar_grid)):
       for j in range(len(ar_grid[i])):
         if ar_grid[i][j]:
            # Since python arrays are zero indexed, we need to offset
            # the loop counters by 1 to account for mass in the 1st
            # column.
            f_x += (j+1) * ar_grid[i][j]
            f_y += (i+1) * ar_grid[i][j]
            f_m += ar_grid[i][j]
    f_com = array( (float(f_x)/f_m , float(f_y)/f_m) )
    return f_com

def com_find2D(ar_grid, **kwargs):
    """
    ARGS
    **kwargs
        ordering = 'rc' or 'xy'        order the return either in (x,y)
                                       or (row, col) order.
        indexing = 'zero' or 'one'     return positions relative to zero (i.e.
                                       python addressing) or one (i.e. MatLAB
                                       addressing)

    DESC
        Find the center of mass in 2D array grid <ar_grid>. Mass elements
        are grid index values.

        By using python idioms, his version is MUCH faster than the com_find()
    """
    b_reorder   = True
    b_oneOffset = True

    for key, value in kwargs.iteritems():
        if key == 'ordering' and value == 'rc':         b_reorder       = False
        if key == 'ordering' and value == 'xy':         b_reorder       = True
        if key == 'indexing' and value == 'zero':       b_oneOffset     = False
        if key == 'indexing' and value == 'one':        b_oneOffset     = True

    f_Smass = ar_grid.sum()
    f_comX = (ar_grid[nonzero(ar_grid)] * (nonzero(ar_grid)[1] + 1)).sum() / f_Smass
    f_comY = (ar_grid[nonzero(ar_grid)] * (nonzero(ar_grid)[0] + 1)).sum() / f_Smass

    if b_reorder:       ar_ret = array( (f_comX, f_comY) )
    if not b_reorder:   ar_ret = array( (f_comY, f_comX) )
    if not b_oneOffset: ar_ret -= 1.0
    return ar_ret

def array2DIndices_enumerate(arr):
        """
        DESC
            Given a 2D array defined by arr, prepare an explicit list
            of the indices.

        ARGS
            arr        in                 2 element array with the first
                                          element the rows and the second
                                          the cols

        RET
            A list of explicit 2D coordinates.
        """

        rows = arr[0]
        cols = arr[1]
        arr_index = zeros((rows * cols, 2))
        count = 0
        for row in arange(0, rows):
           for col in arange(0, cols):
               arr_index[count] = array([row, col])
               count = count + 1
        return arr_index

def error_exit(astr_func,
                        astr_action,
                        astr_error,
                        aexitCode):
        print("FATAL ERROR")
        print("\tSorry, some error seems to have occurred in <%s::%s>" %
              ('systemMisc', astr_func))
        print("\tWhile %s" % astr_action)
        print("\t%s" % astr_error)
        print("")
        print("Returning to system with error code %d" % aexitCode)
        sys.exit(aexitCode)

def printf(format, *args):
        sys.stdout.write(format % args)

def list_removeDuplicates(alist):
    """
    Removes duplicates from an input list
    """
    #d = {}
    #print alist
    #for x in alist:
      #d[x] = x
    #alist = d.values()

    alist = list(set(alist))
    return alist

def b10_convertFrom(anum10, aradix, *args):
    """
        ARGS
        anum10            in      number in base 10
        aradix            in      convert <anum10> to number in base
                                  + <aradix>

        OPTIONAL
        forcelength       in      if nonzero, indicates the length
                                  + of the return array. Useful if
                                  + array needs to be zero padded.

        DESC
        Converts a scalar from base 10 to base radix. Return
        an array.

        NOTE:
        "Translated" from a MatLAB script of the same name.
    """
    i = 0;
    k = 0;

    # Cycle up in powers of radix until the largest exponent is found.
    # This is required to determine the word length
    while (pow(aradix, i)) <= anum10:
        i = i + 1;
    forcelength = i

    # Optionally, allow user to specify word length
    if len(args): forcelength = args[0]

    # Check that word length is valid
    if(forcelength and (forcelength < i)):
        error_exit('b10_convertFrom',
                   'checking on requested return array',
                   'specified length is too small',
                   1)

    numm = anum10;
    num_r = zeros((forcelength));
    if(i):
        k = forcelength - i;
    else:
        k = forcelength - 1;

    if(anum10 == 1):
        num_r[(k)] = 1;
        return num_r;

    for j in arange(i, 0, -1):
        num_r[(k)] = fix(numm / pow(aradix, (j - 1)));
        numm = numm % pow(aradix, (j - 1));
        k = k + 1;
    return num_r

def tic():
    """
        Port of the MatLAB function of same name
    """
    global Gtic_start
    Gtic_start = time.time()

def toc(*args, **kwargs):
    """
        Port of the MatLAB function of same name

        Behaviour is controllable to some extent by the keyword
        args:


    """
    global Gtic_start
    f_elapsedTime = time.time() - Gtic_start
    for key, value in kwargs.items():
        if key == 'sysprint':   return value % f_elapsedTime
        if key == 'default':    return "Elapsed time = %f seconds." % f_elapsedTime
    return f_elapsedTime

def neighbours_findFast(a_dimension, a_depth, *args, **kwargs):
    """

        SYNOPSIS

            [A] = neighbours_findFast(a_dimension, a_depth, *args, **kwargs)

        ARGS

           INPUT
           a_dimension         int32           number of dimensions
           a_depth             int32           depth of neighbours to find

           OPTIONAL
           av_origin           array          row vector that defines the
                                              + origin in the <a_dimension>
                                              + space. Neighbours' locations
                                              + are returned relative to this
                                              + origin. Default is the zero
                                              + origin.

                                              If specified, this *must* be
                                              a 1xa_dimension nparray, i.e.
                                              np.array( [(x,y)] ) in the
                                              2D case.

           OUTPUT
           A                   array           a single array containing
                                                   all the neighbours. This
                                                   does not include the origin.

        Named keyword args
          "includeOrigin"    If True, return the origin in the set.
          "wrapGridEdges"    If True, wrap around the edges of grid.
                             If False, do not wrap around grid edges.
          "gridSize"         Specifies the gridSize for 'wrapEdges'.

          If "gridSize" is set, and "wrapEdges" is not, then the neighbors will
          not include coordinates "outside" of the grid.

        DESC
               This method determines the neighbours of a point in an
               n - dimensional discrete space. The "depth" (or ply) to
               calculate is `a_depth'.

        NOTE
               o Uses the 'itertools' module product() method for
                 MUCH faster results than the explicit neighbours_find()
                 method.

         PRECONDITIONS
               o The underlying problem is discrete.

         POSTCONDITIONS
               o Returns all neighbours

         HISTORY
         23 December 2011
         o Rewrote earlier method using python idioms and resulting
           in multiple order speed improvement.
    """
    if (a_depth < 1):
        A = None
        return A;

    # Process *kwargs and behavioural arguments
    b_includeOrigin = False # If True, include the "origin" in A
    b_wrapGridEdges = False # If True, wrap around edges of grid
    b_gridSize = False # Helper flag for tracking wrap

    for key, value in kwargs.iteritems():
        if key == 'includeOrigin':      b_includeOrigin = value
        if key == 'wrapGridEdges':      b_wrapGridEdges = value
        if key == 'gridSize':
            a_gridSize = value
            b_gridSize = True
            if type(a_gridSize).__name__ != "ndarray":
                error_exit("neighbours_find",
                           "checking on passed grid dimesnions",
                           "grid must be type ndarray.", 2)

    if b_wrapGridEdges and not b_gridSize:
        error_exit("neighbours_find",
                        "checking call options",
                        "no 'gridSize' was specified with 'wrapGridEdges'",
                        1)

    # Check on *args, i.e. an optional 'origin' point in N-space
    v_origin = zeros((a_dimension));
    b_origin = 0;
    if len(args):
        av_origin = args[0];
        if av_origin.size == a_dimension:
            v_origin = av_origin;
            b_origin = 1;

    A = array(list(itertools.product(arange(-a_depth, a_depth + 1),
                                        repeat=a_dimension)))
    if not b_includeOrigin:
        Wbool = A == 0
        W = Wbool.prod(axis=1)
        A = A[where(W == 0)]
    if b_origin: A += v_origin
    if b_gridSize: A = pointInGrid(A, a_gridSize, b_wrapGridEdges)
    return A

def pointInGrid(A_point, a_gridSize, *args):
    """
    SYNOPSIS

        [A_point] = pointInGrid(A_point, a_gridSize [, ab_wrapGridEdges])

    ARGS

        INPUT
        A_point        array of N-D points     points in grid space
        a_gridSize     array                   the size (rows, cols) of
                                               + the grid space

        OPTIONAL
        ab_wrapGridEdges        bool          if True, wrap "external"
                                              points back into grid

        OUTPUT
        A_point        array of N-D points     points that are within the
                                               grid.

    DESC
        Determines if set of N-dimensionals <A_point> is within a grid
        <a_gridSize>.

    PRECONDITIONS
        o Assumes strictly positive domains, i.e. points with negative
          locations are by definition out-of-range. If negative domains
          are valid in a particular problem space, the caller will need
          to offset <a_point> to be strictly positive first.

    POSTCONDITIONS
        o if <ab_wrapGridEdges> is False, returns only the subset of points
          in A_point that are within the <a_gridSize>.
        o if <ab_wrapGridEdges> is True, "wraps" any points in A_point
          back into a_gridSize first, and then checks for those that
          are still within <a_gridSize>.

    """
    b_wrapGridEdges = False # If True, wrap around edges of grid

    if len(args): b_wrapGridEdges = args[0]

    # Check for points "less than" grid space
    if b_wrapGridEdges:
        W = where(A_point < 0)
        A_point[W] += a_gridSize[W[1]]

    Wbool = A_point >= 0
    W = Wbool.prod(axis=1)
    A_point = A_point[where(W > 0)]

    # Check for points "more than" grid space
    A_inGrid = a_gridSize - A_point
    if b_wrapGridEdges:
        W = where(A_inGrid <= 0)
        A_point[W] = -A_inGrid[W]
        A_inGrid = a_gridSize - A_point

    Wbool = A_inGrid > 0
    W = Wbool.prod(axis=1)
    A_point = A_point[where(W > 0)]
#    A_point = abs(A_point)
    return A_point

def neighbours_find(a_dimension, a_depth, *args, **kwargs):
    """

        SYNOPSIS

            [I, D] = neighbours_find(a_dimension, a_depth, *args, **kwargs)

        ARGS

           INPUT
           a_dimension         int32           number of dimensions
           a_depth             int32           depth of neighbours to find

           OPTIONAL
           av_origin           array          row vector that defines the
                                              + origin in the <a_dimension>
                                              + space. Neighbours' locations
                                              + are returned relative to this
                                              + origin. Default is the zero
                                              + origin.

                                              If specified, this *must* be
                                              a 1xa_dimension nparray, i.e.
                                              np.array( [(x,y)] ) in the
                                              2D case.

           OUTPUT
           I                   list           a python list (per depth) of
                                                   "indirect" neighbour
                                                   information. Each index
                                                   of the list is a row - order
                                                   matrix of "index" distant
                                                   indirect neighbours
           D                   list           a python list (per depth) of
                                                   "direct" neighbour
                                                   information. Each index
                                                   of the list is a row - order
                                                   matrix of "index" distant
                                                   direct neighbours
                        - OR -
           A                   list           a single array that is the union
                                                   of I and D across all layers

        Named keyword args

          "returnUnion"      If True, will return A = I union D, flattened
                             including the origin point. In effect, this is
                             all combinations of the coordinates along the
                             axes.
          "wrapGridEdges"    If True, wrap around the edges of grid.
                             If False, do not wrap around grid edges.
          "gridSize"         Specifies the gridSize for 'wrapEdges'.

          If "gridSize" is set, and "wrapEdges" is not, then the neighbors will
          not include coordinates "outside" of the grid.

        DESC
               This method determines the neighbours of a point in an
               n - dimensional discrete space. The "depth" (or ply) to
               calculate is `a_depth'.

               Indirect neighbours are non-orthogonal.
               Direct neighbours are orthogonal.

               Note: this operation is identical to finding all the
               combinations of a given set of elements.

               The neighbours_findFast() method is several orders
               of magnitude faster, and should probably always be
               used over this method. This will remain mostly for
               historical/testing purposes. Also, this method does
               return neighbours as "indirect" and "direct" and
               per "layer" depth, which the ..._findFast does not.


         PRECONDITIONS
               o The underlying problem is discrete.

         POSTCONDITIONS
               o I cell array contains the Indirect neighbours
               o D cell array contains the Direct neighbours
               o size{I} = size{D}
               o size{I} = a_depth

         HISTORY
         20 December 2011
         o Translated from MatLAB script of same name.

    """
    if (a_depth < 1):
        l_D = []
        l_I = {}
        return l_I, l_D;

    # Process *kwargs and behavioural arguments
    b_returnUnion = False # If True, return A = I union D
    b_wrapGridEdges = False # If True, wrap around edges of grid
    b_gridSize = False # Helper flag for tracking wrap

    for key, value in kwargs.iteritems():
        if key == 'returnUnion':        b_returnUnion = value
        if key == 'wrapGridEdges':      b_wrapGridEdges = value
        if key == 'gridSize':
            a_gridSize = value
            b_gridSize = True
            if type(a_gridSize).__name__ != "ndarray":
                error_exit("neighbours_find",
                           "checking on passed grid dimesnions",
                           "grid must be type ndarray.", 2)

    if b_wrapGridEdges and not b_gridSize:
        error_exit("neighbours_find",
                        "checking call options",
                        "no 'gridSize' was specified with 'wrapGridEdges'",
                        1)

    # Check on *args, i.e. an optional 'origin' point in N-space
    v_origin = zeros((a_dimension));
    b_origin = 0;
    if len(args):
        av_origin = args[0];
        if av_origin.size == a_dimension:
            v_origin = av_origin;
            b_origin = 1;

    #
    # Data structure allocation.
    #
    # Although python provides some elegant mechanisms to dynamically
    # "grow" arrays and lists, pre-allocating memory is still by far
    # the fastest way for this method to run.

    # Pre-allocate space for lists containing direct and indirect neighbours
    l_D = [zeros(a_dimension)] * a_depth
    l_I = [zeros(a_dimension)] * a_depth

    # Pre-allocate space for all the possible neighbouring points
    d = 1;
    hypercube = pow((2 * d + 1), a_dimension);
    hypercubeInner = 1;
    orthogonals = 2 * a_dimension;
    l_D[0] = zeros((orthogonals, a_dimension))
    l_I[0] = zeros((hypercube - orthogonals - 1, a_dimension));
    for d in arange(2, a_depth + 1):
        hypercubeInner = hypercube;
        hypercube = pow((2 * d + 1), a_dimension);
        l_D[d - 1] = zeros((orthogonals, a_dimension))
        l_I[d - 1] = zeros((hypercube - orthogonals - hypercubeInner,
                                   a_dimension))
    # Offset and "current" vector
    M_bDoffset = ones((a_dimension)) * -a_depth;
    M_current = ones((a_dimension));
    M_currentAbs = ones((a_dimension));

    # Index counters -- one per "layer"
    # These keep track of the number of entries in each layer.
    M_ii = [0] * a_depth
    M_dd = [0] * a_depth

    # Now we loop through *each* element of the last hypercube
    # and assign it to the appropriate matrix in the I,D structures
    for i in arange(0, hypercube):
        str_progress = 'iteration %5d (of %5d) %3.2f' % \
                                (i, hypercube - 1, i / (hypercube - 1) * 100);
        M_current = arr_base10toN(i, (2 * a_depth + 1), a_dimension);
        M_current = M_current + M_bDoffset;
        M_currentAbs = abs(M_current);
        neighbour = max(M_currentAbs);
        if b_origin:
            M_current += v_origin
        if b_gridSize:
            # Check for points "less than" grid space
            if min(M_current) < 0:
                if not b_wrapGridEdges: continue
                else:
                    Wt = where(M_current < 0)
                    W = Wt[0]  # See help on 'where'
                    for el in arange(0, len(W)):
                        M_current[W[el]] += a_gridSize[W[el]]
            # Check for points "more than" grid space
            M_inGrid = a_gridSize - M_current
            if min(M_inGrid) <= 0:
                if not b_wrapGridEdges: continue
                else:
                    Wt = where(M_inGrid <= 0)
                    W = Wt[0]  # See help on 'where'
                    for el in arange(0, len(W)):
                        M_current[W[el]] = -M_inGrid[W[el]]
                    M_current = abs(M_current)
        idx = int(neighbour) - 1
        if(sum(M_currentAbs) > neighbour):
            l_I[idx][M_ii[idx]] = M_current
            M_ii[idx] += 1;
        else:
            if(sum(M_currentAbs) == neighbour and neighbour):
                l_D[idx][M_dd[idx]] = M_current
                M_dd[idx] += 1;

    if b_gridSize:
        # Here, we use the counters in M_ii and M_dd (per layer)
        # to determine how many actual indices were packed into
        # memory, and slice the layer accordingly.
        for layer in arange(0, a_depth, dtype=int):
            l_I[layer] = l_I[layer][0:M_ii[layer], :]
            l_D[layer] = l_D[layer][0:M_dd[layer], :]

    if b_returnUnion:
        l_A = []
        l_Al = v_origin
        for layer in arange(0, a_depth, dtype=int):
            # first stack each I and D, per layer
            l_A.append(vstack((l_I[layer], l_D[layer])))
            l_Al = vstack((l_Al, l_A[layer]))
        return l_Al

    return l_I, l_D

def arr_base10toN(anum10, aradix, *args):
    """
        ARGS
        anum10            in      number in base 10
        aradix            in      convert <anum10> to number in base
                                  + <aradix>

        OPTIONAL
        forcelength       in      if nonzero, indicates the length
                                  + of the return array. Useful if
                                  + array needs to be zero padded.

        DESC
        Converts a scalar from base 10 to base radix. Return
        an array.
    """

    new_num_arr = array(())
    current = anum10
    while current != 0:
        remainder = current % aradix
        new_num_arr = r_[remainder, new_num_arr]
        current = current / aradix

    forcelength = new_num_arr.size
    # Optionally, allow user to specify word length
    if len(args): forcelength = args[0]
    while new_num_arr.size < forcelength:
        new_num_arr = r_[0, new_num_arr]
    return new_num_arr

def base10toN(num, n):
    """Change a num to a base-n number.
    Up to base-36 is supported without special notation."""
    num_rep = {10:'a',
         11:'b',
         12:'c',
         13:'d',
         14:'e',
         15:'f',
         16:'g',
         17:'h',
         18:'i',
         19:'j',
         20:'k',
         21:'l',
         22:'m',
         23:'n',
         24:'o',
         25:'p',
         26:'q',
         27:'r',
         28:'s',
         29:'t',
         30:'u',
         31:'v',
         32:'w',
         33:'x',
         34:'y',
         35:'z'}
    new_num_string = ''
    new_num_arr = array(())
    current = num
    while current != 0:
        remainder = current % n
        if 36 > remainder > 9:
            remainder_string = num_rep[remainder]
        elif remainder >= 36:
            remainder_string = '(' + str(remainder) + ')'
        else:
            remainder_string = str(remainder)
        new_num_string = remainder_string + new_num_string
        new_num_arr = r_[remainder, new_num_arr]
        current = current / n
    print(new_num_arr)
    return new_num_string

def list_i2str(ilist):
    """
    Convert an integer list into a string list.
    """
    slist = []
    for el in ilist:
        slist.append(str(el))
    return slist

"""
The attribute* set of functions process strings/dictionaries of the
form:

        <key1>=<value1> <key2>=<value2> <key3>=<value3>

the separator in the above string is a space, although this can
be somewhat arbitrary.
"""

def attributes_toStr(**adict_attrib):
        strIO_attribute = StringIO()
        for attribute in adict_attrib.keys():
            str_text = ' %s="%s"' % (attribute, adict_attrib[attribute])
            strIO_attribute.write(str_text)
        str_attributes = strIO_attribute.getvalue()
        return str_attributes

def attributes_dictToStr(adict_attrib):
        strIO_attribute = StringIO()
        for attribute in adict_attrib.keys():
            str_text = ' %s="%s"' % (attribute, adict_attrib[attribute])
            if len(adict_attrib[attribute]):
                strIO_attribute.write(str_text)
        str_attributes = strIO_attribute.getvalue()
        return str_attributes

def attributes_strToDict(astr_attributes, astr_separator=" "):
  """
  This is logical inverse of the dictToStr method. The <astr_attributes>
  string *MUST* have <key>=<value> tuples separated by <astr_separator>.
  """
  adict = {}
  alist = str2lst(astr_attributes, astr_separator)
  for str_pair in alist:
    alistTuple = str2lst(str_pair, "=")
    adict.setdefault(alistTuple[0], alistTuple[1].strip(chr(0x22) + chr(0x27)))
  return adict

def str_blockIndent(astr_buf, a_tabs=1, a_tabLength=4, **kwargs):
    """
    For the input string <astr_buf>, replace each '\n'
    with '\n<tab>' where the number of tabs is indicated
    by <a_tabs> and the length of the tab by <a_tabLength>

    Trailing '\n' are *not* replaced.
    """
    str_tabBoundary = " "
    for key, value in kwargs.iteritems():
      if key == 'tabBoundary':  str_tabBoundary = value
    b_trailN = False
    length = len(astr_buf)
    ch_trailN = astr_buf[length - 1]
    if ch_trailN == '\n':
      b_trailN = True
      astr_buf = astr_buf[0:length - 1]
    str_ret = astr_buf
    str_tab = ''
    str_Indent = ''
    for i in range(a_tabLength):
        str_tab = '%s ' % str_tab
    str_tab = "%s%s" % (str_tab, str_tabBoundary)
    for i in range(a_tabs):
        str_Indent = '%s%s' % (str_Indent, str_tab)
    str_ret = re.sub('\n', '\n%s' % str_Indent, astr_buf)
    str_ret = '%s%s' % (str_Indent, str_ret)
    if b_trailN: str_ret = str_ret + '\n'
    return str_ret

def valuePair_fprint(astr_name, afvalue=None, leftCol=40, rightCol=40):
        if afvalue != None:
            print('%*s:%*f' % (leftCol, astr_name, rightCol, afvalue))
        else:
            printf('%*f', leftCol, astr_name)
def valuePair_sprint(astr_name, astr_value, leftCol=40, rightCol=40):
        if len(astr_value):
            print('%*s:%*s' % (leftCol, astr_name, rightCol, astr_value))
        else:
            printf('%*s', leftCol, astr_name)
def valuePair_dprint(astr_name, avalue=None, leftCol=40, rightCol=40):
        if avalue != None:
            print('%*s:%*d' % (leftCol, astr_name, rightCol, avalue))
        else:
            printf('%*d', leftCol, astr_name)

def html(astr_string, astr_tag="p"):
        print("""
        <%s>
        %s
        </%s>
        """ % (astr_tag, astr_string, astr_tag))

def PRE(astr_string):
        print("""
        <pre>
        %s
        </pre>
        """ % astr_string)

def P(astr_string):
        print("<p>%s</p>" % astr_string)

def system_eval(str_command, b_echoCommand=0):
        if b_echoCommand: printf('<p>str_command = %s</p>', str_command)
        fp_stdout = os.popen(str_command)
        str_stdout = ''
        while(1):
                str_line = fp_stdout.readline()
                if str_line:
                        str_stdout = str_stdout + str_line
                else:
                        break
        if b_echoCommand: printf('<p>str_line = %s</p>', str_line)
        if b_echoCommand: printf('<p>str_stdout = %s</p>', str_stdout)
        return str_stdout

def system_pipeRet(str_command, b_echoCommand=0):
        if b_echoCommand: printf('<p>str_command = %s</p>', str_command)
        fp_stdout = os.popen(str_command)
        str_stdout = ''
        while(1):
                str_line = fp_stdout.readline()
                if str_line:
                        str_stdout = str_stdout + str_line
                else:
                        break
        retcode = fp_stdout.close()
        if b_echoCommand: printf('<p>str_line = %s</p>', str_line)
        if b_echoCommand: printf('<p>str_stdout = %s</p>', str_stdout)
        return retcode, str_stdout

def system_procRet(str_command, b_echoCommand=0):
        """
        Run the <str_command> on the underlying shell. Any stderr stream
        is lost.

        RETURN

            Tuple (retcode, str_stdout)
            o retcode: the system return code
            o str_stdout: the standard output stream
        """
        if b_echoCommand: printf('<p>str_command = %s</p>', str_command)
        str_stdout = os.popen(str_command).read()
        retcode = os.popen(str_command).close()
        return retcode, str_stdout

def subprocess_eval(str_command, b_echoCommand=0):
    if b_echoCommand: printf('%s', str_command)
    b_OK = True
    retcode = -1
    p = Popen(string.split(str_command), stdout=PIPE, stderr=PIPE)
    str_stdout, str_stderr = p.communicate()
    try:
        str_forRet = str_command + " 2>/dev/null >/dev/null"
        retcode = call(str_forRet, shell=True)
    except OSError as e:
        b_OK = False
    return str_stdout, str_stderr, retcode

## start of http://code.activestate.com/recipes/52296/ }}}
## Some mods by RP
def makeNonBlocking(fd):
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    try:
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NDELAY)
    except AttributeError:
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NDELAY)


def shell(command, **kwargs):
    """
        Runs 'command' on the underlying shell and keeps the stdout and
        stderr stream separate.

        Returns [stdout, stderr, exitCode]
    """
    b_stdoutflush       = False
    b_stderrflush       = False
    b_waitForChild      = True
    for key, val in kwargs.iteritems():
        if key == 'stdoutflush':        b_stdoutflush   = val
        if key == 'stderrflush':        b_stderrflush   = val
        if key == 'waitForChild':       b_waitForChild  = val
    child = popen2.Popen3(command, 1) # capture stdout and stderr from command
    child.tochild.close()             # don't need to talk to child
    outfile = child.fromchild
    outfd = outfile.fileno()
    errfile = child.childerr
    errfd = errfile.fileno()
    makeNonBlocking(outfd)            # don't deadlock!
    makeNonBlocking(errfd)
    outdata = errdata = ''
    outeof = erreof = 0
    while b_waitForChild:
        ready = select.select([outfd,errfd],[],[]) # wait for input
        if outfd in ready[0]:
            outchunk = outfile.read()
            if b_stdoutflush: sys.stdout.write(outchunk)
            if outchunk == '': outeof = 1
            outdata = outdata + outchunk
        if errfd in ready[0]:
            errchunk = errfile.read()
            if b_stderrflush: sys.stderr.write(errchunk)
            if errchunk == '': erreof = 1
            errdata = errdata + errchunk
        if outeof and erreof: break
        select.select([],[],[],.1) # give a little time for buffers to fill
    err = child.wait()
    return outdata, errdata, err

def shellne(command):
    """
        Runs 'commands' on the underlying shell; any stderr is echo'd to the
        console.

        Raises a RuntimeException on any shell exec errors.
    """

    child = os.popen(command)
    data = child.read()
    err = child.close()
    if err:
        raise RuntimeError('%s failed w/ exit code %d' % (command, err))
    return data
## end of http://code.activestate.com/recipes/52296/ }}}

def mkdir(newdir, mode=0o775):
    """
    works the way a good mkdir should :)
        - already exists, silently complete
        - regular file in the way, raise an exception
        - parent directory(ies) does not exist, make them as well
    """
    if os.path.isdir(newdir):
        pass
    elif os.path.isfile(newdir):
        raise OSError("a file with the same name as the desired " \
                      "dir, '%s', already exists." % newdir)
    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head):
            mkdir(head)
        #print "_mkdir %s" % repr(newdir)
        if tail:
            os.mkdir(newdir)
            #print "chmod %d %s" % (mode, newdir)
            #os.chmod(newdir, mode)

def touch(fname, times=None):
    '''
    Emulates the UNIX touch command.
    '''
    with file(fname, 'a'):
        os.utime(fname, times)

# From stackoverflow, answered Sep 25 '08 at 21:43 by S.Lott
# http://stackoverflow.com/questions/136168/get-last-n-lines-of-a-file-with-python-similar-to-tail
def tail( f, window=20 ):
    BUFSIZ = 1024
    f.seek(0, 2)
    bytes = f.tell()
    size = window
    block = -1
    data = []
    while size > 0 and bytes > 0:
        if (bytes - BUFSIZ > 0):
            # Seek back one whole BUFSIZ
            f.seek(block*BUFSIZ, 2)
            # read BUFFER
            data.append(f.read(BUFSIZ))
        else:
            # file too small, start from begining
            f.seek(0,0)
            # only read what was not read
            data.append(f.read(bytes))
        linesFound = data[-1].count('\n')
        size -= linesFound
        bytes -= BUFSIZ
        block -= 1
    return '\n'.join(''.join(data).splitlines()[-window:])

def file_exists(astr_fileName):
    try:
        fd = open(astr_fileName)
        if fd: fd.close()
        return True
    except IOError:
        return False

def file_writeOnce(astr_fileName, astr_val, **kwargs):
    '''
    Simple "one-shot" writer. Opens <astr_fileName>
    and saves <astr_val> to file, then closes
    file.
    '''

    _str_mode = 'w'
    for key, val in kwargs.iteritems():
        if key == 'mode':   _str_mode   = val

    FILE = open(astr_fileName, _str_mode)
    FILE.write(astr_val)
    FILE.close()


def locate(pattern, root=os.curdir):
    '''Locate all files matching supplied filename pattern in and below
    supplied root directory.'''
    for path, dirs, files in os.walk(os.path.abspath(root)):
        for filename in fnmatch.filter(files, pattern):
            yield os.path.join(path, filename)

def find(pattern, root=os.curdir):
    '''Helper around 'locate' '''
    hits = ''
    for F in locate(pattern, root):
        hits = hits + F + '\n'
    l = hits.split('\n')
    if(not len(l[-1])): l.pop()
    if len(l) == 1 and not len(l[0]):
        return None
    else:
        return l

def exefile_existsOnPath(astr_fileName):
        try:
                return open(astr_fileName)
        except IOError:
                return None

def str_dateStrip(astr_datestr, astr_sep='/'):
  """
  Simple date strip method. Checks if the <astr_datestr>
  contains <astr_sep>. If so, strips these from the string
  and returns result.

  The actual stripping entails falling through two layers
  of exception handling... so it is something of a hack.
  """
  try:
    index = astr_datestr.index(astr_sep)
  except:
    return astr_datestr.encode('ascii')

  try:
    tm = time.strptime(astr_datestr, '%d/%M/%Y')
  except:
    try:
      tm = time.strptime(astr_datestr, '%d/%M/%y')
    except:
      error_exit('str_dateStrip', 'parsing date string',
                 'no conversion was possible', 1)
  tstr = time.strftime("%d%M%Y", tm)
  return tstr.encode('ascii')

def currentDate_formatted(astr_format='US', astr_sep='/'):
        str_year = time.localtime()[0]
        str_month = time.localtime()[1]
        str_day = time.localtime()[2]
        if astr_format == 'US':
            str_date = '%02d%s%02d%s%s' % \
                    (str_month, astr_sep, str_day, astr_sep, str_year)
        else:
            str_date = '%s%s%02d%s%02d' % \
                    (str_year, astr_sep, str_month, astr_sep, str_day)
        return string.strip(str_date)

def dict_init(al_key, avalInit=None):
  adict = {}
  if type(avalInit) is types.ListType:
      adict = dict(zip(al_key, avalInit))
  else:
      adict = dict.fromkeys(al_key, avalInit)
  return adict

def str2lst(astr_input, astr_separator=" "):
  """
  Breaks a string at <astr_separator> and joins into a
  list. Steps along all list elements and strips white
  space.

  The list elements are explicitly ascii encoded.
  """
  alistI = astr_input.split(astr_separator)
  alistJ = []
  for i in range(0, len(alistI)):
    alistI[i] = alistI[i].strip()
    alistI[i] = alistI[i].encode('ascii')
    if len(alistI[i]):
      alistJ.append(alistI[i])
  return alistJ

def make_xlat(*args, **kwds):
  """
  Replaces multiple patterns in a single pass.
  From "Python Cookbook", O'Reilly, pg39

  USAGE:
  translate     = make_xlat(adict)
  translate(text)
  """
  adict = dict(*args, **kwds)
  rx = re.compile("|".join(map(re.escape, adict)))
  def one_xlat(match):
    return adict[match.group(0)]
  def xlat(text):
    return rx.sub(one_xlat, text)
  return xlat

# This class provides 'switch/case' syntax.
# From: http://code.activestate.com/recipes/410692-readable-switch-construction-without-lambdas-or-di/
class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration

    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args: # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False
# HOWTO use:

#v = 'ten'
#for case in switch(v):
    #if case('one'):
        #print 1
        #break
    #if case('two'):
        #print 2
        #break
    #if case('ten'):
        #print 10
        #break
    #if case('eleven'):
        #print 11
        #break
    #if case(): # default, could also just omit condition or 'if True'
        #print "something else!"
        ## No need to break here, it'll stop anyway
