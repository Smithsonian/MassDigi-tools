# check_barcodes

This script checks for images in a directory for how many datamatrix barcodes are in the image. Usually, none or more than one means there was a problem.

## Requirements

Download and install lib from https://github.com/dmtx/libdmtx

```bash
./autogen.sh
./configure
make
sudo make install
```

## Running

```bash
./check_barcodes.py [FOLDER] [NO_WORKERS]
```
