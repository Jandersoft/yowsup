import curve25519
import os
import ctypes

from djbec import DjbECPrivateKey, DjbECPublicKey
from eckeypair import ECKeyPair

ctypes.cdll.LoadLibrary("/home/tarek/Projects/yowsup/libs/x86_64/libcurve25519.so")
_curve = ctypes.CDLL("/home/tarek/Projects/yowsup/libs/x86_64/libcurve25519.so")


class Curve:

    DJB_TYPE = 5

    # always DJB curve25519 keys
    @staticmethod
    def generateKeyPair():
        privateKey = curve25519.keys.Private()
        publicKey = privateKey.get_public()
        return ECKeyPair(DjbECPublicKey(publicKey.public), DjbECPrivateKey(privateKey.private))

    @staticmethod
    def decodePoint(bytes, offset=0):
        type = bytes[0] # byte appears to be automatically converted to an integer??

        if type == Curve.DJB_TYPE:
            type = bytes[offset] & 0xFF
            if type != Curve.DJB_TYPE:
                raise Exception("InvalidKeyException Unknown key type: " + str(type) )
            keyBytes = bytes[offset+1:][:32]
            return DjbECPublicKey(str(keyBytes))
        else:
            raise Exception("InvalidKeyException Unknown key type: " + str(type) )

    @staticmethod
    def decodePrivatePoint(bytes):
        return DjbECPrivateKey(str(bytes))


    @staticmethod
    def calculateAgreement(publicKey, privateKey):
        out = ctypes.c_char_p(str(bytearray(32)))
        _curve.curve25519_donna(out, privateKey.getPrivateKey(), publicKey.getPublicKey())
        return out.value

    @staticmethod
    def xcalculateAgreement(publicKey, privateKey):
        #key = curve25519.keys.Private(secret=privateKey)
        #return key.get_shared_key(curve25519.keys.Public(publicKey), lambda x: x)
        secret = ''.join(privateKey.getPrivateKey()) #because for some reason keysPrivate changes 1st byte of secret to 32
        key = curve25519.keys.Private(secret = secret)
        publicKey = publicKey.getPublicKey()
        l = len(publicKey)
        return key.get_shared_key(curve25519.keys.Public(publicKey), lambda  x: x)

    @staticmethod
    def verifySignature(ecPublicSigningKey, message, signature):
        return _curve.curve25519_verify(signature, ecPublicSigningKey.serialize()[1:], message, len(message)) == 0
        # pk = ecPublicSigningKey.serialize()
        #return ed.checkvalid(signature, message, ecPublicSigningKey.serialize()[1:])
        #return ed2.checkvalid(signature, message, ecPublicSigningKey.serialize()[1:])
        # raise Exception("IMPL ME")

    @staticmethod
    def calculateSignature(ecPrivateSigningKey, message):
        rand = os.urandom(64)
        out = ctypes.c_char_p('')
        res = _curve.curve25519_sign(out, ecPrivateSigningKey.serialize(), message, len(message), rand)
        return out.value
        #return _curve.curve25519_sign()
        #signature =  ed.signature(message, ecPrivateSigningKey.serialize(), rand)
        #return signature
        #signingKey = ed25519.SigningKey(ecPrivateSigningKey.serialize())
        #return signingKey.sign(message)