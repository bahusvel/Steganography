import optparse
from PIL import Image
import aes_fun as aes
import numpy as np
import file2zipstring as f2string
from numcodec import numdecode, numencode


def check_size(filename):
	img = Image.open(filename)
	if img.mode in 'RGBA':
		img = img.convert('RGBA')
		datas = img.getdata()
	else:
		datas = []
	return len(datas) - 64 - 16

#@profile
def numhide(filename, message, md5):
	img = Image.open(filename)
	img = img.convert('RGBA')
	nparray = np.array(img, dtype=np.uint8)
	shape = nparray.shape
	nparray = nparray.reshape(-1, 4)

	numencode(nparray, message, md5)

	Image.fromarray(nparray.reshape(shape)).save(filename, "PNG")

#@profile
def numretr(filename):
	img = Image.open(filename)
	nparray = np.array(img, dtype=np.uint8)
	nparray = nparray.reshape(-1, 4)

	return numdecode(nparray)


parser = optparse.OptionParser('usage %prog ' + \
							   '-e/-d <target file>')
parser.add_option("-e", "--encrypt",
				  action="store_true", dest="hide", default=False,
				  help="Option to hide data into an image")
parser.add_option("-d", "--decrypt",
				  action="store_true", dest="retr", default=False,
				  help="Option to hide data into an image")
parser.add_option("-c", "--check",
				  action="store_true", dest="check", default=False,
				  help="Check how much data can be put into file")
parser.add_option("-o", "--output",
				  action="store_true", dest="output", default=False,
				  help="Tell the decrypter to output encrypted files")
parser.add_option("-n", "--no-aes",
				  action="store_false", dest="aes", default=True,
				  help="Whether to use AES Encryption or not.")
parser.add_option('-i', dest='input', type='string',
				  help='input file')


(options, args) = parser.parse_args()


if options.check and ((options.hide is not None) or (options.retr is not None)):
	print("You can stuff " + str(check_size(options.hide)) + " Bytes of data into it.")

if options.hide:
	# Encrypting
	if options.input is not None:
		# Check if there is an input file encrypt it, if not encrypt input text.
		try:
			text = f2string.f2zip(options.input)
		except IOError:
			print("The input file specified does not exist.")
			text = raw_input("Enter a message to hide: ")
	else:
		text = raw_input("Enter a message to hide: ")
		text = f2string.t2zip(text)
	md5 = aes.md5(text)
	if options.aes:
		# Encrypt with AES if needed.
		text = aes.encrypt(text, raw_input("Enter a password: "))

	#Run the function and print the result one line.
	print numhide(args[0], text, md5)

elif options.retr:
	output, md5 = numretr(args[0])
	if options.aes:
		output = aes.decrypt(output, raw_input("Enter a password: "))
	else:
		output = ''.join(output)
	if aes.md5(output) != md5:
		print("Data did not decrypt successfully.")
	if options.output:
		try:
			f2string.zipextractall(output)
		except IOError:
			print("Could not write to file")
	else:
		print f2string.retrivetext(output)


else:
	print parser.usage
	exit(0)

