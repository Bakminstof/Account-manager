Ключи для генерации JWT

```shell
CERTS_DIR="certs"

# Private key
openssl genrsa -out "$CERTS_DIR/auth-jwt-private.pem" 4096

# Public key
openssl rsa -in "$CERTS_DIR/auth-jwt-private.pem" -outform PEM -pubout -out "$CERTS_DIR/auth-jwt-public.pem"
```

