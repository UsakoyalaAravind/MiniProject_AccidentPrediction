from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
import base64

# Generate private key
private_key = ec.generate_private_key(ec.SECP256R1())

# Derive public key
public_key = private_key.public_key()

# Encode keys
private_key_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

public_key_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

print("----- PRIVATE KEY -----")
print(private_key_pem.decode())
# MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgsl58YRyeBuB5LAhzQNFJCROmCsfMKIlE7FlEwEt2TH6hRANCAATn2d4n79/io7U6jQPGnJ2isf8U8Ic65y4Y7yljM+ppfb4JS5/Jo6FW/IO92paA6KygA+QKR+YHiW3PglOAsGC3

print("----- PUBLIC KEY -----")
print(public_key_pem.decode())
# MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE59neJ+/f4qO1Oo0DxpydorH/FPCHOucuGO8pYzPqaX2+CUufyaOhVvyDvdqWgOisoAPkCkfmB4ltz4JTgLBgtw==
