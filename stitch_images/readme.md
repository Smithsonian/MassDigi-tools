## Stitch Images

These tool will stitch two image files into a third file. This allows to easily join images, for example, of both sides of an object. 

The tool allows to stitch the images in three ways:

 * horizontal 
 * vertical
 * automatic - if the images are wider than they are tall, the stitch is vertical, horizontal otherwise

Currently the tool accepts TIF files as the input and exports a JPG. 

The first image needs to be coded with a specific suffix, different than the second image. For example:

 * OBJID01234_A.tif and OBJID01234_B.tif
 * OBJID01234_1.tif and OBJID01234_2.tif
 * OBJID01234_front.tif and OBJID01234_back.tif

### Download binaries

This tool was converted to Windows 10 executable files by using PyInstaller, which "freezes (packages) Python applications into stand-alone executables." Download the current version here:

 * [stitch_images.exe](https://www.dropbox.com/s/4m1r3o5b7u0rdal/stitch_images.exe?dl=0)
