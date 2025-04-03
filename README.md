# python-grpc-seed
Python gRPC Seed project building out the basic functionality of the different gRPC method types.

## gRPC Methods Supported
* CreateShape - Basic RPC
* GetShape - Basic RPC

## Proto Repository
The `proto` package contains the `.proto` file that specifies the service, supported methods,
and message definitions used in this project.

The way this repository is constructed, once the gRPC python files have been generated, you must go
into the `SERVICE_NAME_pb2_grpc.py` module and update the import of the `SERVICE_NAME_pb2.py` module
to be `SERVICE_NAME_pb2.py` so that the imports work properly when used in the `server` and `client` packages

## Server
The `server` package contains `server.py`, the module specifying the creation of an asynchronous
gRPC server.

The `server/lib` packages contains the module `grpc_server_servicer.py` which is the class definition
of the gRPC service defined in the `.proto` file and is responsible for the implementation of each of
the support service methods.

Locally, the server uses a basic JSON file to store and retrieve data as requested by the client but
this can easily be extended to a database connection, either a server or cloud-based.

## Client
The `client` package contains `client.py`, the module specifying a local, console-based client to
interact with the gRPC server.

This client uses `grpc_client_config.json` to specify the client-side configuration of our gRPC
connection. Specifically, this client includes retries to handle the event of the server not
being active at the time of the request.