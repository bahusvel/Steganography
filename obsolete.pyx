cimport numpy as np
cimport cython
import numpy as np

DTYPE = np.uint8
ctypedef np.uint8_t DTYPE_t

@cython.boundscheck(False)
cdef void modencode(np.ndarray[unsigned char, ndim=1] pixel, DTYPE_t byte):
	pixel[0] = (pixel[0] & 248) ^ (byte & 224) >> 5
	pixel[1] = (pixel[1] & 248) ^ (byte & 28) >> 2
	pixel[2] = (pixel[2] & 248) ^ (byte & 3) << 1

@cython.boundscheck(False)
cdef str bytedecode(np.ndarray[unsigned char, ndim=1] pixel):
	return chr((((pixel[0] & 7) << 5) ^ ((pixel[1] & 7) << 2)) ^ ((pixel[2] & 6) >> 1))

@cython.boundscheck(False)
cpdef encode(np.ndarray[unsigned char, ndim=2] nparray, str data, unsigned char *md5, first=True, last=True):
	cdef np.ndarray[unsigned char, ndim=1] npedata
	cdef unsigned int i, length
	if first and last:
		npedata = np.fromstring(md5 + data + md5, dtype=DTYPE)
	elif first:
		npedata = np.fromstring(md5 + data, dtype=DTYPE)
	elif last:
		npedata = np.fromstring(data + md5, dtype=DTYPE)
	else:
		npedata = np.fromstring(data, dtype=DTYPE)
	for i in xrange(0, len(npedata)):
		modencode(nparray[i], npedata[i])
	return nparray

@cython.boundscheck(False)
def decode(np.ndarray[unsigned char, ndim=2] nparray):
	cdef list data
	cdef unsigned int i, eodset = 0
	cdef list EOD
	data = []
	for i in xrange(0, len(nparray)):
		data.append(bytedecode(nparray[i]))
		if eodset == 0 and i > 31:
			EOD = data[:32]
			eodset = 1
		if i > 32:
			if data[-32:] == EOD:
				return ''.join(data[32:-32]), ''.join(EOD)

@cython.boundscheck(False)
def multicodec(np.ndarray[unsigned char, ndim=2] image, str data, unsigned char*md5, unsigned int threads):
	from multiprocessing import Pool

	pool = Pool(threads)
	cdef list results = [], retbuffer = [], sdata = [], simage = []
	cdef unsigned int chunksize, x
	chunksize = len(data) // threads

	#first
	sdata.append(data[:chunksize])
	simage.append(image[:chunksize + 32])
	results.append(pool.apply_async(encode, args=(simage[0], sdata[0], md5),
									kwds={'first': True, 'last': False}))
	#intermediate
	for x in xrange(1, threads - 1):
		sdata.append(data[chunksize * x:chunksize * (x + 1)])
		simage.append(image[chunksize * x + 32:chunksize * (x + 1) + 32])
		results.append(pool.apply_async(encode, args=(simage[x], sdata[x], md5),
										kwds={'first': False, 'last': False}))
	#last
	sdata.append(data[chunksize * (threads - 1):])
	simage.append(image[chunksize * (threads - 1) + 32:])
	results.append(pool.apply_async(encode, args=(simage[threads - 1], sdata[threads - 1], md5),
									kwds={'first': False, 'last': False}))

	for x in xrange(threads):
		retbuffer.append(results[x].get())

	#print(simage)
	return np.concatenate(tuple(retbuffer))


@cython.boundscheck(False)
@cython.embedsignature(True)
@cython.wraparound(False)
cdef cencode(np.ndarray[unsigned char, ndim=2] image, np.ndarray[unsigned char, ndim=1] data):
	cdef long bound, index
	bound = len(data)
	for index in xrange(bound):
		image[index, 0] &= 248
		image[index, 1] &= 248
		image[index, 2] &= 248
		image[index, 0] ^= (data[index] & 224) >> 5
		image[index, 1] ^= (data[index] & 28) >> 2
		image[index, 2] ^= (data[index] & 3) << 1

@cython.boundscheck(False)
@cython.embedsignature(True)
@cython.wraparound(False)
cdef np.ndarray[unsigned char, ndim=1] cdecode(np.ndarray[unsigned char, ndim=2] image):
	cdef:
		unsigned long index, length = len(image)
		np.ndarray[unsigned char, ndim=1] ret = np.empty((length), dtype=np.uint8)

	for index in xrange(length):
		ret[index] = (((image[index, 0] & 7) << 5) ^ ((image[index, 1] & 7) << 2)) ^ ((image[index, 2] & 6) >> 1)
	return ret