#!/usr/bin/env bash

# primero hay que hacer: docker network create testing_net
docker run --rm --network="tp0_testing_net" bash:latest bash -c "echo "testing-was-successful" | nc -v server 12345"


