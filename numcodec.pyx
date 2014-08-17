cimport numpy as np
cimport cython
import numpy as np


@cython.boundscheck(False)
@cython.embedsignature(True)
def numdecode(np.ndarray[unsigned char, ndim=2] image):
	cdef:
		unsigned long index, length = len(image)
		np.ndarray[unsigned char, ndim=1] ndata = np.empty((length), dtype=np.uint8)

	for index in xrange(length):
		ndata[index] = (((image[index, 0] & 7) << 5) ^ ((image[index, 1] & 7) << 2)) ^ ((image[index, 2] & 6) >> 1)

	md5 = ndata[:32].tostring()
	retdata = ndata[32:].tostring()
	return retdata[:retdata.index(md5)], md5


@cython.boundscheck(False)
@cython.embedsignature(True)
@cython.wraparound(False)
cpdef numencode(np.ndarray[unsigned char, ndim=2] image, str data, unsigned char * md5):
	cdef:
		np.ndarray[unsigned char, ndim=1] npedata
		unsigned int i, length
		long bound, index
		unsigned char dref, ir, ig, ib, dr, dg, db

	npedata = np.fromstring(md5 + data + md5, dtype=np.uint8)
	bound = len(npedata)
	for index in xrange(bound):
		#image data sums
		ir = image[index, 0] & 7
		ig = image[index, 1] & 7
		ib = image[index, 2] & 7

		#localizing variables for speed
		dref = npedata[index]
		dr = (dref & 224) >> 5
		dg = (dref & 28) >> 2
		db = (dref & 3) << 1

		#encoding data into image
		image[index, 0] &= 248
		image[index, 1] &= 248
		image[index, 2] &= 248
		image[index, 0] ^= dr
		image[index, 1] ^= dg
		image[index, 2] ^= db

		#normalization:
		if ir > (dr + 4):
			image[index, 0] |= 8
		elif ir < (dr - 4):
			image[index, 0] &= 247

		if ig > (dg + 4):
			image[index, 1] |= 8
		elif ig < (dg - 4):
			image[index, 1] &= 247

		if ib > (db + 4):
			image[index, 2] |= 8
		elif ib < (db - 4):
			image[index, 2] &= 247
