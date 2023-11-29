# CR2 to DNG

This process converts CR2 files into DNG using:

 * Adobe DNG Converter
 * Linux running Wine

## Installation

This particular instance will run headless, so a different setup will be needed:

```bash
# Based on https://superuser.com/a/948200
sudo apt-get install xvfb
Xvfb :0 -screen 0 1024x768x16 &

# Install Wine
sudo dpkg --add-architecture i386
sudo add-apt-repository -y ppa:ubuntu-wine
sudo apt-get update
sudo apt-get install wine

```
