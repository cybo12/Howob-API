cp -R /var/www/mmo_api_dev/flask ./flask
docker build --rm -t api .
docker-compose up -d
rm -Rf flask
