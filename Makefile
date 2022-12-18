build:
	docker-compose build ris-image
run:
	docker-compose up --scale ris-image=0 --scale test=0
test:
	docker-compose run test