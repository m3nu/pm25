PORT=8250
IMAGE_NAME=pm25
INSTANCE_NAME=pm25

all:

build:
	sudo docker build -t ${INSTANCE_NAME} .

restart:
	sudo docker restart ${INSTANCE_NAME}

run:
	sudo docker run --name ${INSTANCE_NAME} --rm \
	-v /opt/pm25/pm25:/opt/pm25:ro \
	-p ${PORT}:11211 \
	-t ${IMAGE_NAME}