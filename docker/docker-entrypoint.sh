#!/bin/bash
set -e

echo "=== DISCOVER Docker Entrypoint ==="
echo "TLS Setting: ${DISCOVER_USE_TLS}"
echo "Host: ${DISCOVER_HOST}"
echo "Port: ${DISCOVER_PORT}"
echo "Command to execute: $@"
echo "===================================="

# Certificate paths (where DISCOVER expects them - in the installed package)
DISCOVER_PKG_DIR="/opt/discover-venv/lib/python3.12/site-packages/discover"
CERT_PATH="${DISCOVER_PKG_DIR}/discover_cert.pem"
KEY_PATH="${DISCOVER_PKG_DIR}/discover_key.pem"

# Check if TLS is enabled
if [ "${DISCOVER_USE_TLS}" = "true" ]; then
    echo "TLS enabled, checking for certificates..."

    # If certificates don't exist, generate self-signed
    if [ ! -f "$CERT_PATH" ] || [ ! -f "$KEY_PATH" ]; then
        echo "No certificates found, generating self-signed certificates..."

        # Determine hostname/IP for certificate
        HOSTNAME="${DISCOVER_HOST:-localhost}"

        # Build SAN (Subject Alternative Name) based on hostname
        if [ "$HOSTNAME" = "0.0.0.0" ] || [ "$HOSTNAME" = "localhost" ]; then
            # For localhost/0.0.0.0, only use DNS and localhost IP
            SAN="DNS:localhost,IP:127.0.0.1"
        else
            # For specific IP/hostname, include it in SAN
            SAN="DNS:localhost,DNS:${HOSTNAME},IP:127.0.0.1,IP:${HOSTNAME}"
        fi

        openssl req -x509 -newkey rsa:2048 -keyout "$KEY_PATH" -out "$CERT_PATH" \
            -days 365 -nodes \
            -subj "/CN=${HOSTNAME}" \
            -addext "subjectAltName=${SAN}"

        echo "Self-signed certificates generated successfully"
    else
        echo "Using existing certificates from mounted volume"
    fi
fi

# Execute the CMD
echo "Starting DISCOVER with command: $@"
exec "$@"
