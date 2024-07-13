Ключи для генерации JWT

```shell
CERTS_DIR="certs"

# Private key
openssl genrsa -out "$CERTS_DIR/auth-jwt-private.pem" 2048

# Public key
openssl rsa -in "$CERTS_DIR/auth-jwt-private.pem" -outform PEM -pubout -out "$CERTS_DIR/auth-jwt-public.pem"
```

```shell
export $(grep -v '^#' .env | tr '\r' '\0' | xargs -d '\n')

docker image build -t "$NGINX_IMAGE_TAG" ./nginx
docker image build -t "$APP_IMAGE_TAG" ./

docker stack deploy --with-registry-auth -c <(docker-compose config) account-manager
```

docker image rm "$NGINX_IMAGE_TAG"
docker image rm "$APP_IMAGE_TAG"

sudo docker stack ps account-manager
sudo docker stack rm account-manager

```powelshell
$APP_IMAGE_TAG="acc_manager:latest"
$NGINX_IMAGE_TAG="acc_manager__nginx:latest"
$APP_PORT=4433

docker image build -t "$NGINX_IMAGE_TAG" ./nginx
docker image build -t "$APP_IMAGE_TAG" ./
```
