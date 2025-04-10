# python-grpc-seed
Python gRPC Seed project building out the basic functionality of the different gRPC method types.

## gRPC Methods Supported
* CreateShape - Basic RPC
* GetShape - Basic RPC

## Proto Repository
The `proto` package contains the `.proto` file that specifies the service, supported methods,
and message definitions used in this project.

It also contains `build_grpc.txt` which contains the commands to build the specialized python files
in the server and client directories if run from the repositories root directory

## Server
The `server` package contains `server.py`, the module specifying the creation of an asynchronous
gRPC server.

The `server/lib` packages contains the module `shape_server.py` which is the class definition
of the gRPC service defined in the `.proto` file and is responsible for the implementation of each of
the support service methods.

Locally, the server uses a basic JSON file to store and retrieve data as requested by the client but
this can easily be extended to a database connection, either a server or cloud-based.

## Client
The `client` package contains `client.py`, the module specifying a local, console-based client to
interact with the gRPC server.

### gRPC Client Config
This client uses `grpc_client_config.json` to specify the client-side configuration of our gRPC
connection. Specifically, this client includes retries to handle the event of the server not
being active at the time of the request. In the "methodConfig" block of the json configuration, a
list of configurations is taken, allowing multiple configurations for different services or even
different methods. 

`"name": [{}]` - Apply configuration to all services and methods

`"name": [ {"service": "Service1"}, {"service": "Service2"}.... ]` - Apply configuration to all methods of the
listed services

`"name": [{"service": "SERVICE_NAME", "method": "METHOD_NAME"}]` - Apply the configuration to the listed methods

You can also mix specifying services and specific methods for a given configuration such that the name block looks
like the following:

`"name": [{"service": "Service1", "method": "Method2"}, {"service": "Service2"}]`

which would apply the given configuration to `Service1.Method2` and all the methods of `Service2`