## How to build a frozen binary using PyInstaller

Install required libs:

```
pip install pyinstaller
pip install pylibdmtx
pip install pysimplegui
easy_install Pillow
```

Build and debug using pyinstaller:

```
pyinstaller --onedir --debug all rename_dm.py
```

Test:

```
dist\rename_dm\rename_dm.exe
```

To add the `libdmtx` dll file, change the `binaries` line in the spec file from:

```
binaries=[],
```

to:

```
binaries=[('C:\\ProgramData\\Anaconda3\\Lib\\site-packages\\pylibdmtx\\libdmtx-64.dll', '.')],
```

Or wherever the pylibdmtx is installed. 

Then, rebuild and test again:

```
pyinstaller rename_dm.spec
```

Once everything works ok, create single file executable:

```
pyinstaller -Fw rename_dm.py
```

Edit the `binaries` line of the spec file as above, and re-create the exe file:

```
pyinstaller rename_dm.spec
```

Note: these instructions can be simplified by editing the spec file.
