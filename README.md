Персональный менеджер аккаунтов, в котором могут храниться аккаунты для авторизации 
в различные сервисы. Публичная версия [тут](https://176.109.100.7/ "Менеджер аккаунтов") 
(не оставляйте в публичной версии чувствительные данные, разместите их в локальной версии менеджера).

Вся настройка осуществляется переменными окружения в файлах __.env__

Для запуска потребуется ключи для генерации токенов авторизации
```shell
CERTS_DIR="certs"

# Private key
openssl genrsa -out "$CERTS_DIR/auth-jwt-private.pem" 2048

# Public key
openssl rsa -in "$CERTS_DIR/auth-jwt-private.pem" -outform PEM -pubout -out "$CERTS_DIR/auth-jwt-public.pem"
```

И сборка docker-контейнеров
```shell
export $(grep -v '^#' .env | tr '\r' '\0' | xargs -d '\n')

docker image build -t "$NGINX_IMAGE_TAG" ./nginx
docker image build -t "$APP_IMAGE_TAG" ./

docker stack deploy --with-registry-auth -c <(docker-compose config) account-manager
```
