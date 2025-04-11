import grpc

class AuthGateway(grpc.AuthMetadataPlugin):
    """
    AuthGateway assigns the provided header and signature to every grpc request so that it can be properly authenticated
    """
    def __init__(self, header, signature):
        self.header = header
        self.signature = signature

    def __call__(self, context, callback):
        """
        Implements authentication by passing metadata to a callback.

        Implementations of this method must not block.

        Args:
          context: An AuthMetadataContext providing information on the RPC that
            the plugin is being called to authenticate.
          callback: An AuthMetadataPluginCallback to be invoked either
            synchronously or asynchronously.
        """
        callback(((self.header, self.signature),), None)