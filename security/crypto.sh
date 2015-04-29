import crypto
import sys
sys.modules['Crypto'] = crypto
from crypto.Cipher import AES
import base64
PADDING = '{'
BLOCK_SIZE = 32
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)


def encrypt(text_to_encrypt, secret_key):
    cipher = AES.new(secret_key)
    encoded = EncodeAES(cipher, text_to_encrypt)
    print 'Encrypted string:', encoded

def decrypt(encoded_string, secret_key):
    cipher = AES.new(secret_key)
    decoded = DecodeAES(cipher, encoded_string)
    print 'Decrypted string:', decoded


text = """
text_goes_here
"""
decrypt(text, 'key_goes_here')
