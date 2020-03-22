#!/usr/bin/env python
# Copyright 2020 Matthew Maciejewski

import os
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import argparse

color_palettes = np.load('color_palettes.npz', allow_pickle=True)

def cluster(image):
    h, w, _ = image.shape
    image = image.reshape(h*w, 3)

    kmeans = KMeans(n_clusters=15).fit(image)
    cluster_inds = kmeans.labels_
    means = kmeans.cluster_centers_

    palette = color_palettes['all_colors']
    means = np.expand_dims(means, axis=1).repeat(len(palette), axis=1)
    palette = np.tile(palette, (15, 1, 1))
    distance = np.linalg.norm(means-palette, axis=-1)
    inds = np.argmin(distance, axis=-1)
    custom_palette = color_palettes['color_info'][inds]
    color_img = color_palettes['all_colors'][inds][cluster_inds]
    palette_img = color_palettes['all_colors'][inds]

    palette_img = np.tile(palette_img, (64, 1)).reshape(64, 15, 3).transpose(1, 0, 2).reshape(64*15, 3)
    palette_img = np.expand_dims(palette_img, axis=0).repeat(64, axis=0)
    color_img = color_img.reshape(h, w, 3)
    cluster_inds = cluster_inds.reshape(h, w)
    return color_img, palette_img, cluster_inds, custom_palette

def quantize(image, palette):
    h, w, _ = image.shape
    image = image.reshape(h*w, 3)
    image = np.expand_dims(image, axis=1).repeat(len(palette), axis=1)
    palette = np.tile(palette, (h*w, 1, 1))
    distance = np.linalg.norm(image-palette, axis=-1)
    color_inds = np.argmin(distance, axis=-1)
    inds0, _, inds2 = np.indices(palette.shape)
    image_out = palette[inds0[:,0,:], color_inds[...,None].repeat(3, axis=-1), inds2[:,0,:]]
    image_out = np.reshape(image_out, (h, w, 3))
    color_inds = color_inds.reshape(h, w)
    return image_out, color_inds

def write_text(palette_inds, file_out):
    with open(file_out, 'w') as outF:
        for row in range(len(palette_inds)):
            if not row % 32:
                outF.write("="*(3*len(palette_inds[0])-1+2*len(palette_inds[0])//16) + '\n')
            elif not row % 16:
                outF.write("-"*(3*len(palette_inds[0])-1+2*len(palette_inds[0])//16) + '\n')
            for col in range(len(palette_inds[0])):
                if not col % 32:
                    outF.write("I ")
                elif not col % 16:
                    outF.write("| ")
                outF.write("{:02d} ".format(palette_inds[row, col]+1))
            outF.write('\n')

def main(args):
    im_in = Image.open(args.file_in).convert('RGBA')
    im_prc = Image.new('RGB', im_in.size, (255,255,255))
    im_prc.paste(im_in, mask=im_in.split()[3])
    im_prc = im_prc.resize((args.w*32, args.h*32), resample=Image.LANCZOS)

    np_im = np.array(im_prc)

    if args.custom_palette:
        img, palette_img, inds, palette = cluster(np_im)

        # Save color image
        img = np.repeat(np.repeat(img, 16, axis=0), 16, axis=1)
        im_prc = Image.fromarray(img.astype('uint8'), 'RGB')
        file_out = (os.path.splitext(args.file_in)[0] +
                    "_cp-{0}x{1}-custom".format(args.h, args.w) +
                    ".png")
        im_prc.save(file_out)

        # Save pic of custom palette
        im_prc = Image.fromarray(palette_img.astype('uint8'), 'RGB')
        file_out = (os.path.splitext(args.file_in)[0] +
                    "_cp-{0}x{1}-palette".format(args.h, args.w) +
                    ".png")
        im_prc.save(file_out)

        # Print custom palette info
        file_out = (os.path.splitext(args.file_in)[0] +
                    "_cp-{0}x{1}-palette-code".format(args.h, args.w) +
                    ".txt")
        with open(file_out, 'w') as outF:
            outF.write(" color    hue   viv   bright\n number   /30   /15    /15\n-----------------------------------\n")
            i = 1
            for palette_info in palette:
                outF.write("   {:02d}      {:02d}    {:02d}     {:02d}\n".format(i, palette_info[0], palette_info[1], palette_info[2]))
                i += 1

        # Print ascii image
        file_out = (os.path.splitext(args.file_in)[0] +
                    "_cp-{0}x{1}-image-code".format(args.h, args.w) +
                    ".txt")
        write_text(inds, file_out)

    else:  # use a default palette

        if args.palette > 0 and args.palette < 15:
            palette = args.palette
            q_im, inds = quantize(np_im, color_palettes['palettes'].item()[palette])

            q_im = np.repeat(np.repeat(q_im, 16, axis=0), 16, axis=1)
            im_prc = Image.fromarray(q_im.astype('uint8'), 'RGB')

            file_out = (os.path.splitext(args.file_in)[0] + 
                        "_dp-{0}x{1}-{2}".format(args.h, args.w, palette) +
                        ".png")
            im_prc.save(file_out)

            file_out = (os.path.splitext(args.file_in)[0] + 
                        "_dp-{0}x{1}-{2}".format(args.h, args.w, palette) +
                        ".txt")
            write_text(inds, file_out)

        else:
            for i in range(1, 15):
                palette = i
                q_im, inds = quantize(np_im, color_palettes['palettes'].item()[i])

                q_im = np.repeat(np.repeat(q_im, 16, axis=0), 16, axis=1)
                im_prc = Image.fromarray(q_im.astype('uint8'), 'RGB')

                file_out = (os.path.splitext(args.file_in)[0] + 
                            "_dp-{0}x{1}-{2}".format(args.h, args.w, palette) +
                            ".png")
                im_prc.save(file_out)

                file_out = (os.path.splitext(args.file_in)[0] + 
                            "_dp-{0}x{1}-{2}".format(args.h, args.w, palette) +
                            ".txt")
                write_text(inds, file_out)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="""This converts an image to Animal Crossing template. Enable the custom palette flag to generate a custom palette for the image. Otherwise supply the palette number you would like to use. A value of -1 generates output for every default palette.""")

    parser.add_argument("file_in", metavar="file-in", type=str,
                        help="Input file")

    parser.add_argument("--custom-palette", action='store_true',
                        help="Generate a custom palette.")
    parser.add_argument("--palette", type=int,
                        help="Palette to use for image. If -1, does all.",
                        default=-1)
    parser.add_argument("--h", type=int,
                        help="Number of blocks high for multi-texture images.",
                        default=1)
    parser.add_argument("--w", type=int,
                        help="Number of blocks wide for multi-texture images.",
                        default=1)

    args = parser.parse_args()
    main(args)
