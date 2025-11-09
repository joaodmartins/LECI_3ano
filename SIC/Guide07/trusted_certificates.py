#!/usr/bin/python3

import sys
import os
import re
from cryptography import x509
from datetime import datetime, timezone

def add_trusted_certificate( file, cert_list ):
    try:
        with open( file, "rb" ) as fd:
            certificate = x509.load_pem_x509_certificate( fd.read() )
    except Exception as e:
        print( f"Cannot load certificate from file {file}: {e}" )
        return
    
    # Subjects are named with Distinguished Names (DN).
    # These are names that are sequences of attributes, similar to a teble row.
    #
    # Each attribute (or column in the table metaphore) is tagged with an OID (Object Identifier).
    # Object identifiers are semantic identifiers, that state what the attribute means.
    # For instance, 2.5.4.6 is CountryName (or C), 2.5.4.3 is CommonName (CN), etc.
    #
    # The RFC 4519 regulates the short names (such as C for CountryName and CN for CommonName), which are more user-friendly when
    # dealing with these names (as in RFC 4514).
    #
    # The usual way DNs are presented as a single string is as a continuous sequence of Identifier=Value pairs separated by slashes (/) or commas (,):
    #     /C=US/O-Digicert Inc/OU=www.digicert.com/CN=DigiCert Global Root CA
    #     C=US,O-Digicert Inc,OU=www.digicert.com,CN=DigiCert Global Root CA
# TODO: add your code here
    now = datetime.now(timezone.utc)
    try:
        not_before = certificate.not_valid_before_utc
        not_after = certificate.not_valid_after_utc
    except AttributeError:
        not_before = certificate.not_valid_before.replace(tzinfo=timezone.utc)
        not_after = certificate.not_valid_after.replace(tzinfo=timezone.utc)

    # Check certificate validity
    if now < not_before or now > not_after:
        print(f"Certificate {file} is not valid at this time (expired or not yet valid).")
        return

    # Extract readable subject name
    subject = certificate.subject.rfc4514_string()
    subject = re.sub(r'\s+', ' ', subject.strip())

    if subject not in cert_list:
        cert_list[subject] = certificate
        print(f"Added trusted certificate: {subject}")
    else:
        print(f"Duplicate certificate ignored: {subject}")
# until here

def main( argv ):
    if len(argv) < 2:
        print( "Usage: %s directory" % (argv[0]) )
        return

    cert_list = {}

# TODO: add your code here
    with os.scandir(argv[1]) as d:
            for entry in d:
                if entry.is_file() and entry.name.lower().endswith((".pem", ".crt", ".cer")):
                    add_trusted_certificate(entry.path, cert_list)
# until here

    print( "%d valid trusted certificates found" % (len(cert_list)) )

if __name__ == "__main__":
    main( sys.argv )
