# openfactory-sdk
This repo offers a use case example of the [OpenFactory-SDK](https://github.com/Demo-Smart-Factory-Concordia-University/OpenFactory-SDK.git)

## Setting up the environment
### Requirements
- DockerDesktop
- WSL v2 (if on Windows)
- Ubuntu enabled in Settings --> Resources --> WSL Integration on Docker (if on Windows)
### Steps
1. Make sure to add the image of the latest OpenFactory version under the features section in the devcontainer.json file like so:
```
"features": {
    "docker-in-docker": {
      "version": "latest"
    },
    "ghcr.io/demo-smart-factory-concordia-university/openfactory-sdk/infra:latest": {
      "openfactory-version": "main"
    }
  },
```
2. In VSCode, a 'Reopen in container' notification should appear (click on it).

## Run OpenFactory
To start the openfactory-infra containers : `spinup` .

### MTConnect
To add a MTConnect device, both the .xml and .yml config files should be added in the directory.
The .xml file or MTConnect device file provides the structure and semantics for any given device(s) complying with the MTConnect Information Model (see [MTConnect Standard](https://docs.mtconnect.org/MTC_Part2_0_Devices_1_4_0.pdf) ).
The .yml file is the OpenFactory config file for the device and should look like this:
```
devices:
  my-device:
    uuid: <DEVICE_UUID>

    agent:
      port: <AGENT_PORT>
      device_xml: <DEVICE_XML_FILE_NAME>
      adapter:
        ip: <ADAPTER_IP>
        port: <ADAPTER_MTCONNECT_PORT>

    supervisor:
      image: ghcr.io/demo-smart-factory-concordia-university/opcua-supervisor
      adapter:
        ip: <ADAPTER_IP>
        port: <ADAPTER_OPCUA_PORT>
        environment:
          - NAMESPACE_URI= <OPCUA_NAMESPACE>
          - BROWSE_NAME= <OPCUA_BROWSA_NAME>
          - KSQLDB_URL=http://ksqldb-server:8088"features": {
    "docker-in-docker": {
      "version": "latest"
    },
    "ghcr.io/demo-smart-factory-concordia-university/openfactory-sdk/infra:latest": {
      "openfactory-version": "main"
    }
  },
```

To run the device: `$openfactory-sdk device up <PATH_TO_YML_FILE>`. 


### OpenFactory apps
To add an app for analytics/monitoring of a device (or any other OpenFactory app) a .yml config file,  a Dockerfile and the app (should inherit Asset class) need to be added to the project. The .yml file is the OpenFactory configuration file and should look like this:
```
apps:
  app_name:
    uuid: <APP_UUID>
    image: <IMAGE_NAME>
```

To build an image for the app  `$docker build -t <IMAGE_NAME> <PATH_TO_DOCKERFILE>`. And to run the app: `$openfactory-sdk app up <PATH_TO_YML_FILE>`.


** If the physical ivac device is not available, it is possible to simulate the adapter by going to openfactory/virtual/iVAC and running the command: `docker compose up -d`.
The IP address in ivac.yml needs to be changed to virtual-ivac-tool-plus-adapter.