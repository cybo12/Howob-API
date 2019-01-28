cp -R /var/www/mmo_api_dev/discord ./discord
docker build -t discord_py .
docker-compose up -d
rm -Rf discord
