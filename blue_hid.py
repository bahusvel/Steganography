import optparse

from PIL import Image

import aes_fun as aes

from codec import encodebyte, decodebyte


def check_size(filename):
	img = Image.open(filename)
	if img.mode in 'RGBA':
		img = img.convert('RGBA')
		datas = img.getdata()
	else:
		datas = []
	return len(datas) - 64 - 16


def bytehide(filename, message, md5):
	img = Image.open(filename)
	d_bytes = md5 + message + md5
	if img.mode in 'RGBA':
		img = img.convert('RGBA')
		new_data = []
		digit = 0
		append = new_data.append
		for item in img.getdata():
			if digit < len(d_bytes):
				append(encodebyte(item[0], item[1], item[2], item[3], d_bytes[digit]))
				digit += 1
			else:
				append(item)
		img.putdata(new_data)
		img.save(filename, "PNG")
		return "Completed!"

	return "Incorrect Image Mode, Couldn't Hide"


#@profile
def byteretr(filename):
	img = Image.open(filename)
	bytes_out = ''
	if img.mode in 'RGBA':
		img = img.convert('RGBA')
		for item in img.getdata():
			bytes_out += decodebyte(item[0], item[1], item[2])
			if len(bytes_out) > 31:
				EOD = bytes_out[:32]
				if bytes_out[-32:] == EOD and len(bytes_out) > 32:
					print "Success"
					return bytes_out[32:-32], EOD
		return bytes_out[32:], EOD
	return "Incorrect Image Mode, Couldn't Retrieve"



parser = optparse.OptionParser('usage %prog ' + \
							   '-e/-d <target file>')
parser.add_option('-e', dest='hide', type='string',
				  help='target picture path to hide text')
parser.add_option('-d', dest='retr', type='string',
				  help='target picture path to retrieve text')
parser.add_option("-c", "--check",
				  action="store_true", dest="check", default=False,
				  help="Check how much data can be put into file")
parser.add_option("-n", "--no-aes",
				  action="store_false", dest="aes", default=True,
				  help="Whether to use AES Encryption or not.")
parser.add_option('-i', dest='input', type='string',
				  help='input file')
parser.add_option('-o', dest='output', type='string',
				  help='output file')

(options, args) = parser.parse_args()

if options.check and ((options.hide is not None) or (options.retr is not None)):
	print("You can stuff " + str(check_size(options.hide)) + " Bytes of data into it.")

if options.hide is not None:
	if options.input is not None:
		try:
			with open(options.input, 'rb') as f:
				text = f.read()
		except IOError:
			print("The input file specified does not exist.")
			text = raw_input("Enter a message to hide: ")
	else:
		text = raw_input("Enter a message to hide: ")
	md5 = aes.md5(text)
	if options.aes:
		text = aes.encrypt(text, raw_input("Enter a password: "))
	print bytehide(options.hide, text, md5)

elif options.retr is not None:
	output, md5 = byteretr(options.retr)
	if options.aes:
		output = aes.decrypt(output, raw_input("Enter a password: "))
	if aes.md5(output) != md5:
		print("Data did not decrypt successfully.")
	if options.output is not None:
		try:
			with open(options.output, 'wb+') as f:
				f.write(output)
		except IOError:
			print("Could not write to file")
	else:
		print output
		pass

else:
	print parser.usage
	exit(0)

