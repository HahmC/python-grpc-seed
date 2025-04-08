import grpc

class AuthGateway(grpc.AuthMetadataPlugin):
    def __init__(self, header, signature):
        self.header = header
        self.signature = signature

    def __call__(self, context, callback):
        """Implements authentication by passing metadata to a callback.

        Implementations of this method must not block.

        Args:
          context: An AuthMetadataContext providing information on the RPC that
            the plugin is being called to authenticate.
          callback: An AuthMetadataPluginCallback to be invoked either
            synchronously or asynchronously.
        """
        callback(((self.header, self.signature),), None)