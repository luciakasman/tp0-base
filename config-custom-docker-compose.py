import yaml
from sys import argv
from copy import deepcopy

CLIENT_AMOUNT_DEFAULT = 2

project_data = {
    "version": "'3.9'",
    "name": "tp0"
}

network_data = {
  "networks": {
    "testing_net": {
      "ipam": {
        "driver": "default",
        "config": [
          {
            "subnet": "172.25.125.0/24"
          }
        ]
      }
    }
  }
}

server_data = {
    "server": {
        "container_name": "server",
        "image": "server:latest",
        "entrypoint": "python3 /main.py",
        "environment": ["PYTHONUNBUFFERED=1", "LOGGING_LEVEL=DEBUG"],
        "networks": ["testing_net"],
        "volumes": ["./server:/config"]
    }
}

client_data = {
    "container_name": None,
    "image": "client:latest",
    "entrypoint": "/client",
    "environment": ["CLI_ID=1", "CLI_LOG_LEVEL=DEBUG"],
    "networks": ["testing_net"],
    "depends_on": ["server"],
    "volumes": ["./client:/config"]
}


def generate_docker_compose_file(client_amount):
    clients = {}

    for i in range(client_amount):
        client_name = f"client{i+1}"
        client_i_data = deepcopy(client_data)
        client_i_data["container_name"] = client_name
        client_i_data["environment"][0] = f"CLI_ID={i+1}"
        clients[client_name] = client_i_data

    services_data = server_data | clients
    services = {
        "services": services_data
    }
    docker_compose_data = project_data | services | network_data

    with open("docker-compose-custom.yaml", 'w') as file:
        yaml.dump(docker_compose_data, file, default_flow_style=False, sort_keys=False)


def main():
    client_amount = get_client_amount()
    generate_docker_compose_file(client_amount)


def get_client_amount():
    '''
    Receives as a command line argument the amount of clients to create,
    using the flag --client_amount.
    '''
    try:
        client_amount_index = argv.index('--client_amount')
        if client_amount_index + 1 < len(argv):
            client_amount = int(argv[client_amount_index + 1])
        else:
            print(f'El argumento --client_amount no tiene un valor. Se usa el valor default: {CLIENT_AMOUNT_DEFAULT}')
            client_amount = CLIENT_AMOUNT_DEFAULT
    except ValueError:
        print('El argumento --client_amount no se proporcionó.')
    return client_amount


if __name__ == "__main__":
    main()
