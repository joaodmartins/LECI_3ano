#!/usr/bin/python3

import sys
import os
from cryptography.hazmat.primitives.asymmetric import ec, padding, utils
from cryptography.hazmat.primitives import serialization, hashes

def load_ec_pub_key( file ):
    try:
        with open( file, "rb" ) as fd:
            key = serialization.load_pem_public_key( fd.read() );
    except:
        print( "File %s doesn´t have a valid PEM encoding of a public key" % (file) )
        return None

    if isinstance( key, ec.EllipticCurvePublicKey ) == False:
        print( "File %s doesn´t have a valid PEM encoding of an EC public key" % (file) )
        return None

    return key

def verify( key, digest_func, fd_file, fd_sig ):
    # Since we don't know the size of the input file, we will prehash it in 4K chunks

# TODO: add your code here
# until here

    # Read the signature

# TODO: add your code here
# until here
        
    # Now we can sign the digest with the intended padding

    try:
        key.verify( signature, digest, ec.ECDSA( utils.Prehashed( digest_func ) ) )
        print( "The signature is valid" )
    except Exception as e:
        print( "The signature is invalid!: %s" % (e) )

def main( argv ):
    digest_dict = { "SHA-256":hashes.SHA256(), "SHA-384":hashes.SHA384(), "SHA-512":hashes.SHA512() }

    if len(argv) < 4 or argv[2] not in digest_dict:
        print ( "Usage: %s pub_file digest_func signed_file [signature file]" % (argv[0]) )
        print ( "       digest_func can be either SHA-256, SHA-384 or SHA-512" )
        return 0

    pub_key = load_ec_pub_key( argv[1] )

    if pub_key == None:
        return 0

    # Open the signed file

    try:
        fd_file = open( argv[3], "rb" )
    except Exception as e:
        print ( "Cannot read from file %s: %s" % (argv[3], e) )
        return 0
    
    # If there is a file with the signature, use it, otherwise use stdin (reopened in binary mode)

    if len(argv) > 4:
        try:
            fd_sig = open( argv[4], "rb" )
        except Exception as e:
            print ( "Cannot read from file %s: %s" % (argv[4], e ) )
            return 0
    else:
        fd_sig = os.fdopen( sys.stdin.fileno(), "rb" )

    verify( pub_key, digest_dict[argv[2]], fd_file, fd_sig )

    return 1

if __name__ == "__main__":
    main( sys.argv )
