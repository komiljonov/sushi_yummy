uv pip freeze > requirements.txt

docker-compose up -d --build

docker exec -it django /bin/sh

docker restart $(docker ps -q)

docker down $(docker ps -q)

find . -path "*/migrations/*.py" -not -name "__init__.py" -delete