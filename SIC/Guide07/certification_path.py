#!/usr/bin/python3

import sys
import os
from cryptography import x509
from datetime import datetime, timezone
import urllib.request

def load_certificate( file ):
    try:
        with open( file, "rb" ) as fd:
            return x509.load_pem_x509_certificate( fd.read() )
    except Exception as e:
        print( f"Cannot load certificate from file {file}: {e}" )
        return None

def get_issuer_certificate( url ):
# TODO: add your code here
    try:
        print(f"Downloading issuer certificate from: {url}")
        with urllib.request.urlopen(url) as response:
            data = response.read()

            try:
                cert = x509.load_pem_x509_certificate(data)
            except Exception:
                cert = x509.load_der_x509_certificate(data)

            return cert

    except Exception as e:
        print(f"Cannot download or parse issuer certificate from {url}: {e}")
        return None
# until here

def build_cert_path( certificate ):
    if certificate.subject == certificate.issuer:
        print( "The chain ended, this is a self-certified certificate" )
        return  # Cannot continue

# TODO: add your code here
    try:
        aia = certificate.extensions.get_extension_for_oid(
            x509.OID_AUTHORITY_INFORMATION_ACCESS
        ).value
    except Exception:
        print("No Authority Information Access (AIA) extension found.")
        return

    issuer_urls = [
        desc.access_location.value
        for desc in aia
        if desc.access_method == x509.AuthorityInformationAccessOID.CA_ISSUERS
    ]

    if not issuer_urls:
        print("No issuer URL found in AIA extension.")
        return

    issuer_cert = None
    for url in issuer_urls:
        issuer_cert = get_issuer_certificate(url)
        if issuer_cert:
            break

    if issuer_cert is None:
        print("Could not obtain issuer certificate.")
        return

    print(f"Issuer: {issuer_cert.subject.rfc4514_string()}")

    build_cert_path(issuer_cert)
# until here

def main( argv ):
    if len(argv) < 2:
        print( "Usage: %s certificate_file" % (argv[0]) )
        return

    certificate = load_certificate( argv[1] )
    if certificate != None:
        print( "Built path for %s" % (certificate.subject.rfc4514_string()) )

        build_cert_path( certificate )

if __name__ == "__main__":
    main( sys.argv )
