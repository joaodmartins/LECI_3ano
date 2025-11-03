#!/usr/bin/python3

import sys
import os
from cryptography.hazmat.primitives.asymmetric import ec, padding, utils
from cryptography.hazmat.primitives import serialization, hashes

def load_ec_priv_key( file ):
    try:
        with open( file, "rb" ) as fd:
            key = serialization.load_pem_private_key( fd.read(), password=None );
    except:
        print( "File %s doesn´t have a valid PEM encoding of a private key" % (file) )
        return None

    if isinstance( key, ec.EllipticCurvePrivateKey ) == False:
        print( "File %s doesn´t have a valid PEM encoding of an EC private key" % (file) )
        return None

    return key

def sign( key, digest_func, fd_in, fd_out ):
    # Since we don't know the size of the input file, we will prehash it in 4K chunks

# TODO: add your code here

# until here
        
    # Now we can sign the digest with the intended padding

    signature = key.sign( digest, ec.ECDSA( utils.Prehashed( digest_func ) ) )
    fd_out.write( signature )

def main( argv ):
    digest_dict = { "SHA-256":hashes.SHA256(), "SHA-384":hashes.SHA384(), "SHA-512":hashes.SHA512() }

    if len(argv) < 3 or argv[2] not in digest_dict:
        print ( "Usage: %s priv_file digest_func [file to sign] [signature file]" % (argv[0]) )
        print ( "       digest_func can be either SHA-256, SHA-384 or SHA-512" )
        return 0

    pub_key = load_ec_priv_key( argv[1] )

    if pub_key == None:
        return 0

    # If there is a file to sign, use it, otherwise use stdin (reopened in binary mode)

    if len(argv) > 3:
        try:
            fd_in = open( argv[3], "rb" )
        except Exception as e:
            print ( "Cannot read from file %s: %s" % (argv[3], e ) )
            return 0
    else:
        fd_in = os.fdopen( sys.stdin.fileno(), "rb" )
    
    # If there is a file to store the signature, use it, otherwise use stdout (reopened in binary mode)

    if len(argv) > 4:
        try:
            fd_out = open( argv[4], "wb" )
        except Exception as e:
            print ( "Cannot write to file %s: %s" % (argv[4], e ) )
            return 0
    else:
        fd_out = os.fdopen( sys.stdout.fileno(), "wb" )

    sign( pub_key, digest_dict[argv[2]], fd_in, fd_out )

    return 1

if __name__ == "__main__":
    main( sys.argv )
