#!/usr/bin/env python3
import sys
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
import math

def encrypt_file(input_filename, pubkey_filename, output_filename):
    # Load public key
    with open(pubkey_filename, "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )

    key_size_bytes = public_key.key_size // 8
    # For OAEP with SHA1: padding overhead = 42 bytes
    max_block_size = key_size_bytes - 42

    print(f"[*] Key size: {public_key.key_size} bits")
    print(f"[*] Maximum plaintext block size: {max_block_size} bytes")

    with open(input_filename, "rb") as infile:
        plaintext = infile.read()

    encrypted_data = b""
    total_blocks = math.ceil(len(plaintext) / max_block_size)
    print(f"[*] Encrypting {len(plaintext)} bytes in {total_blocks} blocks...")

    for i in range(0, len(plaintext), max_block_size):
        block = plaintext[i:i + max_block_size]
        encrypted_block = public_key.encrypt(
            block,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA1()),
                algorithm=hashes.SHA1(),
                label=None
            )
        )
        encrypted_data += encrypted_block

    with open(output_filename, "wb") as outfile:
        outfile.write(encrypted_data)

    print(f"[+] File '{input_filename}' encrypted successfully.")
    print(f"[+] Output written to '{output_filename}'.")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python rsa_encrypt.py <input_file> <public_key_file> <output_file>")
        print("Example: python rsa_encrypt.py message.txt pub.pem message.enc")
        sys.exit(1)

    input_filename = sys.argv[1]
    pubkey_filename = sys.argv[2]
    output_filename = sys.argv[3]

    encrypt_file(input_filename, pubkey_filename, output_filename)