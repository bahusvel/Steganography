__author__ = 'denislavrov'
import zipfile
from cStringIO import StringIO
import os


def f2zip(path):
	memout = StringIO()
	with zipfile.ZipFile(memout, mode='w', compression=zipfile.ZIP_DEFLATED) as zipout:
		if os.path.isdir(path):
			for dir in os.walk(path):
				zipout.write(dir[0])
				for file in dir[2]:
					zipout.write(dir[0] + '/' + file)
		else:
			zipout.write(path)
	return memout.getvalue()


def zipextractall(data):
	memin = StringIO()
	memin.write(data)

	with zipfile.ZipFile(memin, mode='r', compression=zipfile.ZIP_DEFLATED) as zipout:
		zipout.extractall(path='./extracted')


def t2zip(text):
	memout = StringIO()
	with zipfile.ZipFile(memout, mode='w', compression=zipfile.ZIP_DEFLATED) as zipout:
		zipout.writestr('text', text)
	return memout.getvalue()


def retrivetext(data):
	memin = StringIO()
	memin.write(data)
	with zipfile.ZipFile(memin, mode='r', compression=zipfile.ZIP_DEFLATED) as zipout:
		out = zipout.read('text')
	return out