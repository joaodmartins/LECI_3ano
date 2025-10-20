#!/usr/bin/env python3
import sys
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
import math

def decrypt_file(enc_filename, privkey_filename, output_filename):
    # Load private key
    with open(privkey_filename, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )

    key_size_bytes = private_key.key_size // 8

    print(f"[*] Key size: {private_key.key_size} bits")
    print(f"[*] Encrypted block size: {key_size_bytes} bytes")

    with open(enc_filename, "rb") as infile:
        ciphertext = infile.read()

    decrypted_data = b""
    total_blocks = math.ceil(len(ciphertext) / key_size_bytes)
    print(f"[*] Decrypting {len(ciphertext)} bytes in {total_blocks} blocks...")

    for i in range(0, len(ciphertext), key_size_bytes):
        block = ciphertext[i:i + key_size_bytes]
        decrypted_block = private_key.decrypt(
            block,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA1()),
                algorithm=hashes.SHA1(),
                label=None
            )
        )
        decrypted_data += decrypted_block

    with open(output_filename, "wb") as outfile:
        outfile.write(decrypted_data)

    print(f"[+] File '{enc_filename}' decrypted successfully.")
    print(f"[+] Output written to '{output_filename}'.")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python rsa_decrypt.py <encrypted_file> <private_key_file> <output_file>")
        print("Example: python rsa_decrypt.py encrypted.bin priv.pem decrypted.txt")
        sys.exit(1)

    enc_filename = sys.argv[1]
    privkey_filename = sys.argv[2]
    output_filename = sys.argv[3]

    decrypt_file(enc_filename, privkey_filename, output_filename)
