# Read data matrix - Command line tools

This folder has command line tools for:

 * `read_datamatrix.py` - Read a data matrix barcode in the image
 * `rename_file.py` - Rename a file according to the data matrix barcode 

Searching for a data matrix in a large image can take several seconds. To make this process faster, the script `read_datamatrix.py` can take three more arguments to search the barcode in a particular section of the image:

 * -q: How to subdivide the image in rows and columns
 * -r: Row in which the datamatrix is in
 * -c: Column in which the datamatrix is in

For example, looking for the data matrix in a TIF image 2820x1680 took 7.69 seconds. When subdivided using `-q 3`, it took 1.23 seconds.
