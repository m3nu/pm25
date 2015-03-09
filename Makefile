PORT=8250
IMAGE_NAME=pm25
INSTANCE_NAME=pm25

all:

build:
	sudo docker build -t $INSTANCE_NAME .

run:
	sudo docker rm -f $INSTANCE_NAME
	sudo docker run --name $INSTANCE_NAME --rm \
	-p $PORT:11211 \
	-t $IMAGE_NAME