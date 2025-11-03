#!/usr/bin/python3

import sys
import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding, utils
from cryptography.hazmat.primitives import serialization, hashes

def load_rsa_priv_key( file ):
    try:
        with open( file, "rb" ) as fd:
            key = serialization.load_pem_private_key( fd.read(), password=None );
    except:
        print( "File %s doesn´t have a valid PEM encoding of a private key" % (file) )
        return None

    if isinstance( key, rsa.RSAPrivateKey ) == False:
        print( "File %s doesn´t have a valid PEM encoding of an RSA private key" % (file) )
        return None

    return key

def sign( key, padding_alg, digest_func, fd_in, fd_out ):
    # Setup the padding function
    if padding_alg == "PKCS1":
        padding_func = padding.PKCS1v15()
    elif padding_alg == "PSS":
        padding_func = padding.PSS(
            mgf=padding.MGF1(digest_func),
            salt_length=padding.PSS.MAX_LENGTH
        )
    else:
        print("Unsupported padding algorithm")
        return
    
    hasher = hashes.Hash(digest_func)
    while True:
        chunk = fd_in.read(4096)
        if not chunk:
            break
        hasher.update(chunk)
    digest = hasher.finalize()
        
    # Now we can sign the digest with the intended padding

    signature = key.sign( digest, padding_func, utils.Prehashed( digest_func ) )
    fd_out.write( signature )

def main( argv ):
    padding_list = list()
    padding_list = ( ["PKCS1", "PSS"] )
    digest_dict = { "SHA-256":hashes.SHA256(), "SHA-384":hashes.SHA384(), "SHA-512":hashes.SHA512() }

    if len(argv) < 4 or argv[2] not in padding_list or argv[3] not in digest_dict:
        print ( "Usage: %s priv_file padding_scheme digest_func [file to sign] [signature file]" % (argv[0]) )
        print ( "       padding_scheme can be either PKCS1 or PSS" )
        print ( "       digest_func can be either SHA-256, SHA-384 or SHA-512" )
        return 0

    pub_key = load_rsa_priv_key( argv[1] )

    if pub_key == None:
        return 0

    # If there is a file to sign, use it, otherwise use stdin (reopened in binary mode)

    if len(argv) > 4:
        try:
            fd_in = open( argv[4], "rb" )
        except Exception as e:
            print ( "Cannot read from file %s: %s" % (argv[4], e ) )
            return 0
    else:
        fd_in = os.fdopen( sys.stdin.fileno(), "rb" )
    
    # If there is a file to store the signature, use it, otherwise use stdout (reopened in binary mode)

    if len(argv) > 5:
        try:
            fd_out = open( argv[5], "wb" )
        except Exception as e:
            print ( "Cannot write to file %s: %s" % (argv[5], e ) )
            return 0
    else:
        fd_out = os.fdopen( sys.stdout.fileno(), "wb" )

    sign( pub_key, argv[2], digest_dict[argv[3]], fd_in, fd_out )

    return 1

if __name__ == "__main__":
    main( sys.argv )
