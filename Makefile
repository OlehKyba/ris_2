build:
	docker-compose build ris-image
test:
	docker-compose up --scale ris-image=0 --abort-on-container-exit