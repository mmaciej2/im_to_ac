# Animal Crossing New Horizons Texture Generator

This is a set of functions to convert images into Animal Crossing New Horizons textures. This allows you to put your own images into the game as floor murals.

## There are two main functions to use:

#### img_to_animal_crossing_palette_info.py

This converts an image into a format that can be input into the game using the in-game color editor. This can be very tedious, but is capable of generating the highest-quality images and allow after-the-fact hand tuning if you want to modify the design.

#### img_to_animal_crossing_qrs.py

This converts an image into a format that can can be read into the game via QR codes mimicking the Animal Crossing New Leaf texture QR codes. The upsides is that this is very, very fast to get into the game. The downside is that there is a more restricted set of colors that can be used and the designs are unable to be edited once they are in the game.

## Requirements

These scripts require python 3 as well as the following packages:

numpy  
scikit-learn  
Pillow  
PyQRCode

## Usage

### img_to_animal_crossing_palette_info.py

TODO

### img_to_animal_crossing_qrs.py

TODO
