init:
	pip3 install -r requirements.txt

test_game:
	python3 -m alice_battleship.test.game

run:
	REDIS_URL="redis://localhost:6379/0" \
	FLASK_APP=alice_battleship.skill \
	FLASK_ENV=development \
	BASE_URL=https://home.yumaa.dev:13443 \
	flask run \
		--cert certs/fullchain.pem \
		--key certs/privkey.pem \
		--host 0.0.0.0 \
		--port 13443

run_local:
	FLASK_APP=alice_battleship.skill \
	FLASK_ENV=development \
	flask run

format:
	black launcher.py alice_battleship

build:
	docker build \
		--rm --no-cache --compress \
		--tag yumaa/alice-battleship-skill:latest \
		.

push:
	docker push yumaa/alice-battleship-skill:latest

serve:
	docker run --rm -p5000:80 \
		-e "REDIS_URL=redis://host.docker.internal:6379/0" \
		-e "BASE_URL=http://localhost:5000" \
		--name alice-battleship-skill \
		yumaa/alice-battleship-skill:latest

.PHONY: init test_game run run_local format build serve
