#!/usr/bin/env python

import os
from PIL import Image
import numpy as np
from sklearn.cluster import KMeans
import argparse
from generate_qr_code import generate_code


def cluster(image):
    h, w, _ = image.shape
    image = image.reshape(h*w, 3)

    kmeans = KMeans(n_clusters=15).fit(image)
    cluster_inds = kmeans.labels_
    means = kmeans.cluster_centers_

    colors = np.load('qr_colors.npz')
    palette = colors['rgb_values'].astype('float64')
    hex_codes = colors['hex_codes']

    means = np.expand_dims(means, axis=1).repeat(len(palette), axis=1)
    palette = np.tile(palette, (15, 1, 1))
    distance = np.linalg.norm(means-palette, axis=-1)
    inds = np.argmin(distance, axis=-1)
    custom_palette = hex_codes[inds]

    color_image = colors['rgb_values'][inds][cluster_inds]
    color_image = color_image.reshape(h, w, 3)

    return color_image, cluster_inds, custom_palette

def main(args):
    im_in = Image.open(args.file_in).convert('RGBA')
    im_prc = Image.new('RGB', im_in.size, (255,255,255))
    im_prc.paste(im_in, mask=im_in.split()[3])
    im_prc = im_prc.resize((args.w*32, args.h*32), resample=Image.LANCZOS)

    np_im = np.array(im_prc)

    img, cluster_inds, custom_palette = cluster(np_im)
    img = np.repeat(np.repeat(img, 64, axis=0), 64, axis=1)

    im_prc = Image.fromarray(img)
    file_out = (os.path.splitext(args.file_in)[0] +
                "_qr-{0}x{1}-custom".format(args.h, args.w) +
                ".png")
    im_prc.save(file_out)

    generate_code(args.h, args.w, cluster_inds, custom_palette, os.path.splitext(args.file_in)[0])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="""This converts an image to Animal Crossing textures. It generates QR codes to be used with the Switch companion app. As a result the textures are non-editable and have a reduced color palette but do not need to be manually entered.""")

    parser.add_argument("file_in", metavar="file-in", type=str,
                        help="Input file")

    parser.add_argument("--h", type=int,
                        help="Number of blocks high for multi-texture images.",
                        default=1)
    parser.add_argument("--w", type=int,
                        help="Number of blocks wide for multi-texture images.",
                        default=1)

    args = parser.parse_args()
    main(args)
