#!/usr/bin/python3

import sys
import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding, utils
from cryptography.hazmat.primitives import serialization, hashes

def load_rsa_pub_key( file ):
    try:
        with open( file, "rb" ) as fd:
            key = serialization.load_pem_public_key( fd.read() )
    except:
        print( "File %s doesn´t have a valid PEM encoding of a public key" % (file) )
        return None

    if isinstance( key, rsa.RSAPublicKey ) == False:
        print( "File %s doesn´t have a valid PEM encoding of an RSA public key" % (file) )
        return None

    return key

def verify( key, padding_alg, digest_func, fd_file, fd_sig ):
    # Setup the padding function
    
# TODO: add your code here
# until here

    # Since we don't know the size of the input file, we will prehash it in 4K chunks

# TODO: add your code here
# until here
        
    # Read the signature

# TODO: add your code here
# until here
        
    # Now we can sign the digest with the intended padding

    try:
        key.verify( signature, digest, padding_func, utils.Prehashed( digest_func ) )
        print( "The signature is valid" )
    except Exception as e:
        print( "The signature is invalid!: %s" % (e) )

def main( argv ):
    padding_list = list()
    padding_list = ( ["PKCS1", "PSS"] )
    digest_dict = { "SHA-256":hashes.SHA256(), "SHA-384":hashes.SHA384(), "SHA-512":hashes.SHA512() }

    if len(argv) < 4 or argv[2] not in padding_list or argv[3] not in digest_dict:
        print ( "Usage: %s priv_file padding_scheme digest_func [file to sign] [signature file]" % (argv[0]) )
        print ( "       padding_scheme can be either PKCS1 or PSS" )
        print ( "       digest_func can be either SHA-256, SHA-384 or SHA-512" )
        return 0

    pub_key = load_rsa_pub_key( argv[1] )

    if pub_key == None:
        return 0

    # Open the signed file

    try:
        fd_file = open( argv[4], "rb" )
    except Exception as e:
        print ( "Cannot read from file %s: %s" % (argv[4], e) )
        return 0
    
    # If there is a file with the signature, use it, otherwise use stdin (reopened in binary mode)

    if len(argv) > 5:
        try:
            fd_sig = open( argv[5], "rb" )
        except Exception as e:
            print ( "Cannot read from file %s: %s" % (argv[5], e ) )
            return 0
    else:
        fd_sig = os.fdopen( sys.stdin.fileno(), "rb" )

    verify( pub_key, argv[2], digest_dict[argv[3]], fd_file, fd_sig )

    return 1

if __name__ == "__main__":
    main( sys.argv )
