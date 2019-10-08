## How to build a frozen binary using PyInstaller

Install required libs:

```
pip install pyinstaller
pip install pysimplegui
pip install pillow
```

Create the single file executable:

```
pyinstaller -Fw stitch_images.py
```
