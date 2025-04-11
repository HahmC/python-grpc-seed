# python-grpc-seed
Python gRPC Seed project building out a basic server and client to demonstrate the capabilities of gRPC. More
documentation around the different capabilities and options provided by gRPC can be found here: https://grpc.io/docs/guides/

<b>Implemented Functionality</b>

* Server
  * Logging
    * Detailed logs of server operations
    * CorrelationID support for request tracking
  * SSL Auth
  * Async Server
  * Interceptor
    * Signature Interceptor used for custom client auth
  * All four gRPC Method types
    * Unary-Unary
    * Unary-Stream
    * Stream-Unary
    * Stream-Stream
  * grpc-health.v1 Implementation
    * Implementation of the gRPC provided health-check API
* Client
  * SSL Auth
  * Custom Signature
    * custom metadata key-value pair expected by the server for additional authentication
  * Basic Console application
  * Correlation-Id generation
  * Robust Server Health-Checking

## gRPC Methods Supported
* GetShape - Unary-Unary RPC
  * Takes a `ShapeId` and returns the corresponding shape
* CreateShape - Unary-Unary RPC
  * Creates one of the supported shape types of a random size
* GetAreas - Stream-Stream RPC
  * Given an Iterator of `ShapeId` returns and Iterator of `GetAreasResponse` items that contain
  the shape and it's area among other return values
* GetTotalArea - Stream-Unary RPC
  * Given an Iterator of `ShapeId` returns the sum of the areas of the specified shapes
* GetPerimetersGreaterThan - Unary-Stream RPC
  * Given a minimum perimeter value, returns an Iterator of all the `Shape` items with a perimeter
  greater than the specified value

## Proto Repository
The `proto` package contains the `.proto` file that specifies the service, supported methods,
and message definitions used in this project.

It also contains `build_grpc.txt` which contains the commands to build the specialized python files
in the server and client directories if run from the repositories root directory

## Server
The `server` package contains `server.py`, the module specifying the creation of an asynchronous
gRPC server.

The `server/lib/services` packages contains the module `shape_service.py` which is the class definition
of the gRPC service defined in the `.proto` file and is responsible for the implementation of each of
the support service methods.

Locally, the server uses a basic JSON file to store and retrieve data as requested by the client but
this can easily be extended to a database connection, either a server or cloud-based.

The server implements SSL authentication using the server certificate and key provided in the gRPC example
at https://github.com/grpc/grpc/blob/v1.71.0/examples/python/auth/tls_server.py. For additional authentication,
an `Interceptor` is also created to review each incoming request for the `x-signature` header and compare the
value of that header to the defined value in the config.

## Client
The `client` package contains `client.py`, the module specifying the creation of an asynchronous, local, console-based
client.

The `grpc_client_config.json` file contains the `grpc.Channel` configuration specifying service/method timeouts,
retry policies, and a health check config.

### Health Check Policy
Before the client calls any of the methods defined by the server, it calls the `Check` method of 
the grpc-health.v1 API to ensure the server is active directly before the method call. In the `config.ini` you can 
configure the maximum amount of failed health checks allowed before the client stops attempting to make the request to 
the server. Currently, the health check logic is also configured so that every other failed health check, the 
`grpc.Channel` is recreated to ensure that the channel connection has not gone stale.

**Note: The `Check` method is generally intended for situations where the call will not be made many consecutive times
as it does not scale to support a fleet of gRPC clients constantly making health checks. In that situation it is best
to use the `Watch` method which streams health updates back to the client. This specific client implements health
checks using the `Check` method only due to its small scale and the synchronous functionality of a console-based app. At
scale, for how health-checks are used in this client it would generally be better to use the `Watch` endpoint to
receive a stream of health-updates

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

The "healthCheckConfig" portion of the config specifies the services you would like to monitor the health of with your
client. This allows the client to invoke the `Watch` method of the health check service on when a connection is
established and prevents requests from being sent until a healty status for the service being called is received.