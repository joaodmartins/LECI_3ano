import sys
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def generate_rsa_key_pair(pub_filename, priv_filename, key_size):
	private_key = rsa.generate_private_key(
		public_exponent=65537,
		key_size=key_size
	)

	public_key = private_key.public_key()

	pem_private = private_key.private_bytes(
		encoding=serialization.Encoding.PEM,
		format=serialization.PrivateFormat.TraditionalOpenSSL,
		encryption_algorithm=serialization.NoEncryption()
	)

	pem_public = public_key.public_bytes(
		encoding=serialization.Encoding.PEM,
		format=serialization.PublicFormat.SubjectPublicKeyInfo
	)

	with open(priv_filename, "wb") as priv_file:
		priv_file.write(pem_private)

	with open(pub_filename, "wb") as pub_file:
        	pub_file.write(pem_public)

	print(f"RSA key pair ({key_size} bits) generated successfully.")
	print(f"Private key saved to: {priv_filename}")
	print(f"Public key saved to: {pub_filename}")

if __name__ == "__main__":
	if len(sys.argv) != 4:
        	print("Usage: python keygen.py <public_key_filename> <private_key_filename> <key_size>")
        	print("Example: python keygen.py pub.pem priv.pem 2048")
        	sys.exit(1)

	pub_filename = sys.argv[1]
	priv_filename = sys.argv[2]
	key_size = int(sys.argv[3])

	if key_size not in [1024, 2048, 3072, 4096]:
		print("Error: key size must be one of 1024, 2048, 3072, or 4096.")
		sys.exit(1)

	generate_rsa_key_pair(pub_filename, priv_filename, key_size)
