# Guide Utilisateur – OpenFactory SDK
Guide pour l’installation, la configuration et l’utilisation du SDK OpenFactory pour simuler ou connecter des appareils industriels via MTConnect et déployer des applications.

## Prérequis
Avant de commencer, il faut s'assurer d’avoir les éléments suivants installés :
- Docker Desktop
- WSL v2 (pour Windows)
- Ubuntu activé dans Docker
→ Paramètres → Ressources → Intégration WSL → Activer Ubuntu (pour Windows)
- Le repo clôné dans le disque dur virtuel Linux (pour Windows)

## Configuration de l’environnement
### Étape 1 : Modifier devcontainer.json
Ajouter les lignes suivantes dans la section features du fichier devcontainer.json **si elles ne sont pas déjà là**:
```
"features": {
    "ghcr.io/devcontainers/features/docker-in-docker:2": {},

    "ghcr.io/openfactoryio/openfactory-sdk/infra": {
      "openfactory-version": "main"
    }
}
```
[devcontainer.json](.devcontainer/devcontainer.json)

### Étape 2 : Ouvrir le projet dans VSCode
Une notification **« Reopen in container »** devrait apparaître. Cliquer dessus pour ouvrir le projet dans un container Docker.

## Lancer OpenFactory
Pour démarrer les containers d’infrastructure OpenFactory :
`spinup`

## Arrêter OpenFactory
Pour arrêter les containers d’infrastructure OpenFactory :
`teardown`

## Accéder à la base de données ksqldb
Pour effectuer des queries et visualiser l'état de la base de données ksqldb (streams des assets, etc.):
`ksql`

## Ajouter et lancer un appareil MTConnect
Fichiers requis
- Fichier XML : structure de l’appareil (conforme à MTConnect Standard)
- Fichier YML : configuration OpenFactory de l’appareil

### Strcuture du fichier YML
```
devices:
  my-device:
    uuid: <UUID_DU_APPAREIL>

    uns:
      workcenter: <NOM_WORKCENTER>
      asset: <NOM_ASSET>

    connector:
      type: mtconnect
      agent:
        port: <PORT_AGENT>
        device_xml: <NOM_FICHIER_XML>
        adapter:
          ip: <IP_ADAPTATEUR>
          port: <PORT_MTCONNECT>

      supervisor:
        image: ghcr.io/openfactoryio/opcua-supervisor:${OPENFACTORY_VERSION}
        adapter:
          ip: <IP_ADAPTATEUR>
          port: <PORT_OPCUA>
          environment:
            - NAMESPACE_URI=<NAMESPACE_OPCUA>
            - BROWSE_NAME=<NOM_BROWSE_OPCUA>
            - KSQLDB_URL=http://ksqldb-server:8088
```
L'agent est celui qui achemine l'information de l'équipement à OpenFactory. Le supervisor sert à envoyer des commandes à l'équipement par protocole OPC-UA et n'est pas toujours nécessaire (comme dans le cas de la CNC).

#### Exemples de fichiers .yml
- [Fichier .yml pour le iVAC](/openfactory/adapter/ivac.yml)
- [Fichier .yml pour la CNC](/openfactory/adapter/cnc.yml)


### Lancer l’appareil
`$ofa device up <CHEMIN_VERS_FICHIER_YML>`

### Arrêter l'appareil
`$ofa device down <CHEMIN_VERS_FICHIER_YML>`

## Simuler un appareil iVAC ou CNC
Si l’appareil physique iVAC n’est pas disponible, il est possible de simuler l’adaptateur dans
`cd openfactory/virtual/<EQUIPEMENT_SIMULÉ>`.
### Lancer l'appareil simulé
`docker compose up -d`

Il faut s'assurer que l’adresse IP utilisée dans le fichier de configuration .yml de l'équipement (dans `openfactory/adapter/device.yml`) correspond à celle du conteneur de l'équipement simulé. Cette adresse est définie dans le fichier de configuration .yml de l'adapteur virtuel (dans `openfactory/virtual/<EQUIPEMENT_SIMULÉ>/vdevice.yml`).

## Ajouter et lancer des applications OpenFactory
Fichiers requis
- Fichier YML : configuration des applications
- Dockerfile : pour construire l’image
- Code de l’application : doit hériter de la classe Asset
### Structure du fichier YML
```
apps:
  app_name:
    uuid: <UUID_APP>
    image: <NOM_IMAGE>
```
[Exemple de fichier .yml](/openfactory/apps/apps.yml)

#### Construire les applications
`$cd openfactory/apps/<APP>`
`$docker build -t <NOM_IMAGE> <CHEMIN_VERS_DOCKERFILE>`

#### Lancer les applications
`$ofa apps up <CHEMIN_VERS_FICHIER_YML>`

#### Arrêter les applications
`$ofa apps down <CHEMIN_VERS_FICHIER_YML>`

### OpenFactory-API
Cette application OpenFactory sert de couche de service pour accéder aux données en temps réel à partir des assets déployés sur OpenFactory. 
#### S'abonner à un device
En se connectant au endpoint `ws://ofa-api:8000/ws/devices/<device_uuid>`, l'app permet à un client WebSocket de recevoir des updates en temps réel pour le device demandé (qui correspond à un asset OpenFactory). L'application s'occupe de créer un stream dérivé dédié à cet asset lors de la connection d'un nouveau client.
#### Format d'un message 
```
{
  'asset_uuid': 'IVAC',
  'data': {
            'ID': 'A2BlastGate',
            'VALUE': 'CLOSED',
            'TIMESTAMP': '2025-07-21T09:14:49.829000000'
          }
}
```
*ID correspond au dataitem_id






