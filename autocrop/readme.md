# autocrop

Crop an image by removing the area that matches a corner:

 * top-left
 * top-right
 * bottom-left
 * bottom-right 

Usage:

```bash
./autocrop.py <image filename>
        <corner: top-left top-right bottom-left or bottom-right> 
        <edge_size: integer>
```

For example:

```bash
./autocrop.py file.tif top-left 0
```
