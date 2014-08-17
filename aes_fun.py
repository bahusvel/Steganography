__author__ = 'denislavrov'

from Crypto.Cipher import AES
from Crypto import Random
import hashlib


def md5(inp):
    return hashlib.md5(inp).hexdigest()


def encrypt(message, password):
    key = md5(password)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CFB, iv)
    return iv + cipher.encrypt(message)


def decrypt(data, password):
    key = md5(password)
    iv = data[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CFB, iv)
    return cipher.decrypt(data[AES.block_size:])

