# SMS AUTOMATE
It is built using python program and uses adb to send and receive sms

## Send SMS
To send an sms we have a `docker-send.yaml` file which is a compose file which can be used to run the container and send sms using the mobile connected via USB cable.

The Following are the commands neccessary to start stop or kill the containers

### Start the Container

```bash
docker-compose -f docker-send.yaml up
```

### Stop the Container
```bash
docker-compose -f docker-send.yaml stop
```

### Kill the Container
```bash
docker-compose -f docker-send.yaml down
```

## Receive SMS
To get all the sms of a specific number we have a `docker-reply.yaml` file, it is used to run and retrieve all the sms from the mobile of the number that was sent and store it in a `.csv` file and stored at `generated-csv` directory.

The number can be changed in the `docker-reply.yaml` file
```bash
environment:
  - PHONE_NUMBER=<phone_number>
```

The Following are the commands neccessary to start, stop or kill the containers

### Start the Container

```bash
docker-compose -f docker-reply.yaml up
```

### Stop the Container
```bash
docker-compose -f docker-reply.yaml stop
```

### Kill the Container
```bash
docker-compose -f docker-reply.yaml down
```

## Updates
To container can be updated using this command

```bash
docker pull rajasgh18/sms-automate
```