
# Loop folders in hotfolder
Get-ChildItem –Path "c:\hotfolder" -Recurse -Filter *.dng |
  Foreach-Object {
  echo $_.FullName
    ## IPTC Creator: Smithsonian Digitization
    ./exiftool.exe -XMP-dc:creator="Smithsonian Digitization" -overwrite_original $_.FullName

      ## IPTC Creator: Job Title: SI – Imaging Services Program Office
      ./exiftool.exe -XMP-Photoshop:AuthorsPosition="SI - Imaging Services Program Office" -overwrite_original $_.FullName

      ## IPTC City: Washington, DC
      ./exiftool.exe -iptc:city="Washington, DC" -overwrite_original $_.FullName

      ## IPTC State:
      ./exiftool.exe -iptc:Province-State="" -overwrite_original $_.FullName

      ## IPTC Keywords:
      ./exiftool.exe -iptc:keywords="" -overwrite_original $_.FullName

      ## IPTC Source: National Museum of African Art
      ./exiftool.exe -iptc:source="National Museum of African Art" -overwrite_original $_.FullName

      ## IPTC Copyright Notice: This image was obtained from the Smithsonian Institution. Unless otherwise noted, this image or its contents may be protected by international copyright laws.
      ./exiftool.exe -iptc:copyrightnotice="This image was obtained from the Smithsonian Institution. Unless otherwise noted, this image or its contents may be protected by international copyright laws." -overwrite_original $_.FullName

      ## IPTC Rights Usage Terms: https://www.si.edu/termsofuse
      ./exiftool.exe -xmp:usageterms="https://www.si.edu/termsofuse" -overwrite_original $_.FullName
  }

  Get-ChildItem –Path "c:\hotfolder" -Recurse -Filter *.tif |
    Foreach-Object {
    echo $_.FullName
      ## IPTC Creator: Smithsonian Digitization
      ./exiftool.exe -XMP-dc:creator="Smithsonian Digitization" -overwrite_original $_.FullName

        ## IPTC Creator: Job Title: SI – Imaging Services Program Office
        ./exiftool.exe -XMP-Photoshop:AuthorsPosition="SI - Imaging Services Program Office" -overwrite_original $_.FullName

        ## IPTC City: Washington, DC
        ./exiftool.exe -iptc:city="Washington, DC" -overwrite_original $_.FullName

        ## IPTC State:
        ./exiftool.exe -iptc:Province-State="" -overwrite_original $_.FullName

        ## IPTC Keywords:
        ./exiftool.exe -iptc:keywords="" -overwrite_original $_.FullName

        ## IPTC Source: National Museum of African Art
        ./exiftool.exe -iptc:source="National Museum of African Art" -overwrite_original $_.FullName

        ## IPTC Copyright Notice: This image was obtained from the Smithsonian Institution. Unless otherwise noted, this image or its contents may be protected by international copyright laws.
        ./exiftool.exe -iptc:copyrightnotice="This image was obtained from the Smithsonian Institution. Unless otherwise noted, this image or its contents may be protected by international copyright laws." -overwrite_original $_.FullName

        ## IPTC Rights Usage Terms: https://www.si.edu/termsofuse
        ./exiftool.exe -xmp:usageterms="https://www.si.edu/termsofuse" -overwrite_original $_.FullName
    }


# Copy to network share
robocopy f:\hotfolder k:\is\test_project\ /z /j /mir /mon:1 /MT:4
