# Copyright 2020 Matthew Maciejewski

from ac_bytes_to_png import ACBuilder

str_a = '4026c'
# str_b is 80 hex digits, of the form ascii character + 00
str_c = '00006d9050006800740068006900730069007300000000005fa1560075006c00630061006e0000000000000001003108'
# str_d is 15 2-digit hex codes corresponding to the color palette
str_e = '000a090000'
# str_f is 1024 hex characters encoding the texture
str_g = '0ec11ec11'


def generate_code(height, width, cluster_inds, custom_palette, base_filename):
    cluster_inds = cluster_inds.reshape(height*32, width*32)
    for i in range(height):
        for j in range(width):

            str_b = ''
            name = str(i)+'-'+str(j)
            for chr in name:
                str_b += "{0:02x}00".format(ord(chr))
            str_b = str_b + '0'*(80-len(str_b))

            str_d = ''.join(list(custom_palette))

            str_f = ''
            sub_inds = cluster_inds[i*32:(i+1)*32, j*32:(j+1)*32]
            int_list = list(sub_inds.reshape(1024))
            for idx in range(0, 1024, 2):
                str_f += "{0:01x}{1:01x}".format(int_list[idx+1], int_list[idx])

            ACBuilder(str_a + str_b + str_c + str_d + str_e + str_f + str_g,
                      base_filename+'_qr-{0}x{1}_code-{2}-{3}.png'.format(height, width, i, j))
