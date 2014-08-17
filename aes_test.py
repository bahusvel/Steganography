__author__ = 'denislavrov'

import aes_fun as aes

text = raw_input("Enter text: ")
password = raw_input("Enter password: ")
print("Text size: " + str(len(text)))
ciphertext = aes.encrypt(text, password)
print("Cipher text is: " + ciphertext)
print("Cipher text size: " + str(len(ciphertext)))