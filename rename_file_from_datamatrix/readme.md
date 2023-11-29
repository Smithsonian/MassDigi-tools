## Rename Files Tool

These two tools will rename image files according to the code in a data matrix barcode in the image. This allows to easily rename files automatically so that they match the data matrix barcode. 

The original files are not deleted, the renamed files are written to a subfolder called `export`.

### Rename File Pairs from Data Matrix Tool

Rename file pairs using the data matrix barcode in the tif file. The tool requires two subfolders in the selected folder:

 * tifs
 * raws

Both the tif and raw files are copied to a subfolder called `export`. 

### Rename File from Data Matrix Tool

This tool copies TIF/JPG image files to a subfolder called `export` renaming the files using the data matrix barcode in the image.

### Download binaries

These tools were converted to Windows 10 executable files by using PyInstaller, which "freezes (packages) Python applications into stand-alone executables." Download the current versions here:

 * [rename_dm_pairs.exe](https://www.dropbox.com/s/qp8gqn4uaolwg7u/rename_dm_pairs.exe?dl=0)
 * [rename_dm.exe](https://www.dropbox.com/s/4ny8awz27qnrci5/rename_dm.exe?dl=0)
