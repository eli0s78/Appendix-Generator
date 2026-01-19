#!/usr/bin/env python3
"""Generate self-signed certificate for local HTTPS development."""

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from datetime import datetime, timedelta
import os

def generate_self_signed_cert():
    """Generate a self-signed certificate for localhost."""

    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # Certificate subject and issuer
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Local"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"Local"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Appendix Generator Dev"),
        x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
    ])

    # Build certificate
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName(u"localhost"),
            x509.DNSName(u"127.0.0.1"),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256())

    # Create certs directory if it doesn't exist
    os.makedirs('.streamlit/certs', exist_ok=True)

    # Write private key
    with open('.streamlit/certs/key.pem', 'wb') as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # Write certificate
    with open('.streamlit/certs/cert.pem', 'wb') as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    print("Self-signed certificate generated successfully!")
    print("  - Certificate: .streamlit/certs/cert.pem")
    print("  - Private Key: .streamlit/certs/key.pem")
    print("\nNote: Your browser will show a security warning because this is a self-signed certificate.")
    print("This is normal for local development. Click 'Advanced' and 'Proceed to localhost' to continue.")

if __name__ == '__main__':
    generate_self_signed_cert()
