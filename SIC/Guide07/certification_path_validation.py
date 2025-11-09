#!/usr/bin/python3

import sys
import os
from cryptography import x509
from cryptography.x509 import ocsp
from cryptography.hazmat.primitives import hashes, serialization
from datetime import datetime, timezone
import base64
from urllib import request

def load_certificate( file ):
    try:
        with open( file, "rb" ) as fd:
            return x509.load_pem_x509_certificate( fd.read() )
    except Exception as e:
        print( f"Cannot load certificate from file {file}: {e}" )
        return None

def load_certificate_from_url( url ):
# TODO: add your code here
# until here

# Check Basic Constraints extension for CA allowance (and its criticality)
def verify_constraint( certificate ):
    basic_constraints = certificate.extensions.get_extension_for_class( x509.BasicConstraints )
# TODO: add your code here
# until here
 
# Check Key Usage extension for CA allowance (and its criticality)
def key_usage( certificate ):
    key_usage = certificate.extensions.get_extension_for_class( x509.KeyUsage )
# TODO: add your code here
# until here

def valid_signature( certificate, issuer ):
# TODO: add your code here
# until here

def revoked( certificate, issuer ):
    print( "\t\tOCSP validation:" )
    try:
        extension = certificate.extensions.get_extension_for_class( x509.AuthorityInformationAccess )
    except:
        print( "\t\t\tNo OCSP information" )
        return

    ocsp_status = {
        ocsp.OCSPResponseStatus.MALFORMED_REQUEST : 'malformed request',
        ocsp.OCSPResponseStatus.INTERNAL_ERROR : 'internal error',
        ocsp.OCSPResponseStatus.TRY_LATER : 'try later',
        ocsp.OCSPResponseStatus.SIG_REQUIRED : 'signature required',
        ocsp.OCSPResponseStatus.UNAUTHORIZED : 'not authorized' }
        
    for ad in extension.value:
        if ad.access_method.dotted_string == "1.3.6.1.5.5.7.48.1": # OCSP
# TODO: add your code here
# until here

            # In theory, we can use GET or POST
            # For GET, we must use a Base64 encoding of the OCSP Request, but with /s replaced by their HTML encoding (%2F)
            # For POST, we can use the binary raw bytes of the OCSP Request
            # Unfortunately, some OCSP servers do not accept long GET URLs, so POST is safer

            http_req = request.Request( url, method="POST" )
            http_req.add_header( 'Content-Type', 'application/ocsp-request' )
            try:
                response = request.urlopen( http_req, data=ocsp_request )
                ocsp_response = ocsp.load_der_ocsp_response( response.read() )

                if ocsp_response.response_status == ocsp.OCSPResponseStatus.SUCCESSFUL:
                    print( "\t\t\tOCSP status is valid" )
                else:
                    print( "\t\t\tOCSP status error: %s" % (ocsp_status[ocsp_response.response_status]) )
                return
            except Exception as e:
                print( f"OCSP server error: {e}" )
                return

    print( "\t\t\tNo OCSP information" )

def validate_chain( certificate ):
    if certificate.subject == certificate.issuer:
        print( "The chain ended, this is a self-certified certificate" )
        return  # Cannot continue

    try:
        extension = certificate.extensions.get_extension_for_class( x509.AuthorityInformationAccess )
    except:
        return # Cannot continue

    for ad in extension.value:
        if ad.access_method.dotted_string == "1.3.6.1.5.5.7.48.2": # CA_ISSUERS
            issuer = load_certificate_from_url( ad.access_location.value ) # The value should be a URL
            if certificate.issuer != issuer.subject:
                print( "Wrong issuer certificate" )
                return
            break

    print( "\t%s" % (issuer.subject.rfc4514_string()) )

    valid_signature( certificate, issuer )
    verify_constraint( issuer )
    key_usage( issuer )
    revoked( certificate, issuer )

    validate_chain( issuer )

def main( argv ):
    if len(argv) < 2:
        print( "Usage: %s certificate_file" % (argv[0]) )
        return

    certificate = load_certificate( argv[1] )
    if certificate != None:
        print( "Validate path for %s" % (certificate.subject.rfc4514_string()) )
        validate_chain( certificate )

if __name__ == "__main__":
    main( sys.argv )
