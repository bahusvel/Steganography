__author__ = 'denislavrov'


hexrange = [hex(x)[-1] for x in range(16)]
rlower = hexrange[:8]
rupper = hexrange[8:]

def hide(filename, message, md5):
    img = Image.open(filename)
    bmd5 = pad(str2bin(md5))
    binary = bmd5 + str2bin(message) + bmd5
    if img.mode in ('RGBA'):
        img = img.convert('RGBA')
        datas = img.getdata()
        newData = []
        digit = 0
        append = newData.append
        for item in datas:
            if (digit < len(binary)):
                newpix = encode(rgb2hex(item[0], item[1], item[2]), binary[digit])
                if newpix == None:
                    append(item)
                else:
                    r, g, b = hex2rgb(newpix)
                    append((r, g, b, 255))
                    digit += 1
            else:
                append(item)
        img.putdata(newData)
        img.save(filename, "PNG")
        return "Completed!"

    return "Incorrect Image Mode, Couldn't Hide"



def retr(filename):
    img = Image.open(filename)
    binary = ''

    if img.mode in ('RGBA'):
        img = img.convert('RGBA')
        datas = img.getdata()

        for item in datas:
            digit = decode(rgb2hex(item[0], item[1], item[2]))
            if digit == None:
                pass
            else:
                binary += digit
                if len(binary) > 255:
                    EOD = binary[:256]
                    if binary[-256:] == EOD and len(binary) > 257:
                        print "Success"
                        return bin2str(binary[256:-256]), bin2str(EOD)
        return bin2str(binary), bin2str(EOD)
    return "Incorrect Image Mode, Couldn't Retrieve"

def decode(hexcode):
    if hexcode[-1] in ('0', '1'):
        return hexcode[-1]
    else:
        return None


def encode(hexcode, digit):
    if hexcode[-1] in rlower:
        hexcode = hexcode[:-1] + digit
        return hexcode
    elif hexcode[-1] in rupper and hexcode[-2] != 'f':
            hexcode = hexcode[:-2] + hexrange[int(hexcode[-2], 16)+1] + digit
            return hexcode
    else:
        return None

def check_helper(item):
    hexcode = rgb2hex(item[0], item[1], item[2])
    hx = hexcode[-1]
    if (hx in rlower) or (hx in rupper and hexcode[-2] != 'f'):
        return 1
    else:
        return 0

def rgb2hex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)


def hex2rgb(hexcode):
    return tuple(map(ord, hexcode[1:].decode('hex')))


def str2bin(message):
    binary = bin(int(binascii.hexlify(message), 16))
    return binary[2:]


def bin2str(binary):
    message = binascii.unhexlify('%x' % (int(binary, 2)))
    return message


def parity(byte):
    byte = ord(byte)
    c = 0
    while byte:
        c ^= byte & 1
        byte >>= 1
    return c