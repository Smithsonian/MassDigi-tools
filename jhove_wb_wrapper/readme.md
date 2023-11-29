# JHOVE White Balance wrapper

This script was written to avoid an error from JHOVE when the only issue is the white balance value. JHOVE 1.20 returns an error if WB is not 0/1, but cameras are using other values now. 

To use, rename `settings.py.template` to `settings.py` and set the location of jhove, for example:

```
jhove_path = "usr/bin/jhove/jhove"
```

Then run the script with the image to check:

```bash
$ ./jhove_wb.py wb_5.tif
Well-Formed, but not valid; WhiteBalance value out of range: 5

$ echo $?
0

$ ./jhove_wb.py ok_file.tif
Well-Formed and valid

$ echo $?
0
```