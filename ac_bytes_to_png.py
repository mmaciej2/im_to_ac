import pyqrcode
from pyqrcode.builder import QRCodeBuilder, _png
from pyqrcode import tables
import io

# this is hacked together from pieces of QRCodeBuilder

class ACBuilder(QRCodeBuilder):
    def __init__(self, data, filename):

        version = 19
        mode = 'binary'
        error = 'M'

        """See :py:class:`pyqrcode.QRCode` for information on the parameters."""
        #Set what data we are going to use to generate
        #the QR code
        self.data = data

        #Check that the user passed in a valid mode
        if mode in tables.modes:
            self.mode = tables.modes[mode]
        else:
            raise ValueError('{0} is not a valid mode.'.format(mode))

        #Check that the user passed in a valid error level
        if error in tables.error_level:
            self.error = tables.error_level[error]
        else:
            raise ValueError('{0} is not a valid error '
                             'level.'.format(error))

        if 1 <= version <= 40:
            self.version = version
        else:
            raise ValueError("Illegal version {0}, version must be between "
                             "1 and 40.".format(version))

        #Look up the proper row for error correction code words
        self.error_code_words = tables.eccwbi[version][self.error]

        #This property will hold the binary string as it is built
        self.buffer = io.StringIO()

        #Create the binary data block
        cleaned = bytes.hex(bytes.fromhex(data))
        bytestream = ('{0:0'+str(len(cleaned)*4)+'b}').format(int(cleaned,16))
        self.buffer.write(bytestream)

        data = [int(''.join(x),2)
                    for x in self.grouper(8, self.buffer.getvalue())]

        #This is the error information for the code
        error_info = tables.eccwbi[self.version][self.error]

        #This will hold our data blocks
        data_blocks = []

        #This will hold our error blocks
        error_blocks = []

        #Some codes have the data sliced into two different sized blocks
        #for example, first two 14 word sized blocks, then four 15 word
        #sized blocks. This means that slicing size can change over time.
        data_block_sizes = [error_info[2]] * error_info[1]
        if error_info[3] != 0:
            data_block_sizes.extend([error_info[4]] * error_info[3])

        #For every block of data, slice the data into the appropriate
        #sized block
        current_byte = 0
        for n_data_blocks in data_block_sizes:
            data_blocks.append(data[current_byte:current_byte+n_data_blocks])
            current_byte += n_data_blocks
        
        #I am not sure about the test after the "and". This was added to
        #fix a bug where after delimit_words padded the bit stream, a zero
        #byte ends up being added. After checking around, it seems this extra
        #byte is supposed to be chopped off, but I cannot find that in the
        #standard! I am adding it to solve the bug, I believe it is correct.
        if current_byte < len(data):
            raise ValueError('Too much data for this code version.')

        #DEBUG CODE!!!!
        #Print out the data blocks
        #print('Data Blocks:\n{0}'.format(data_blocks))

        #Calculate the error blocks
        for n, block in enumerate(data_blocks):
            error_blocks.append(self.make_error_block(block, n))

        #DEBUG CODE!!!!
        #Print out the error blocks
        #print('Error Blocks:\n{0}'.format(error_blocks))

        #Buffer we will write our data blocks into
        data_buffer = io.StringIO()

        #Add the data blocks
        #Write the buffer such that: block 1 byte 1, block 2 byte 1, etc.
        largest_block = max(error_info[2], error_info[4])+error_info[0]
        for i in range(largest_block):
            for block in data_blocks:
                if i < len(block):
                    data_buffer.write(self.binary_string(block[i], 8))

        #Add the error code blocks.
        #Write the buffer such that: block 1 byte 1, block 2 byte 2, etc.
        for i in range(error_info[0]):
            for block in error_blocks:
                data_buffer.write(self.binary_string(block[i], 8))

        self.buffer = data_buffer

        #Create the actual QR code
        self.make_code()

        _png(self.code, version, filename, 6, (0, 0, 0, 255), (255, 255, 255, 255), 4)
