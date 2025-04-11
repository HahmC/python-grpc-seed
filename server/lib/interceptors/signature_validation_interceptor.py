import grpc
from typing import Awaitable, Callable

class SignatureValidationInterceptor(grpc.aio.ServerInterceptor):
    """
    Signature Validation Interceptor used to intercept the incoming request and authenticate it with an expected
    header-value pair
    """
    def __init__(self, sig_header: str, sig_value: str):
        def abort(ignored_request, context):
            """
            Abort the current request when invoked

            :param ignored_request: request being ignored
            :param context: context to abort
            :return: None
            """
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid signature")

        self.signature_header = sig_header
        self.signature = sig_value
        self._abort_unary_unary = grpc.unary_unary_rpc_method_handler(abort)
        self._abort_unary_stream = grpc.unary_stream_rpc_method_handler(abort)
        self._abort_stream_unary = grpc.stream_unary_rpc_method_handler(abort)
        self._abort_stream_stream = grpc.stream_stream_rpc_method_handler(abort)

    def intercept_service(self, continuation: Callable[
            [grpc.HandlerCallDetails], Awaitable[grpc.RpcMethodHandler]
        ], handler_call_details: grpc.HandlerCallDetails):
        """
        Intercepts incoming request and attempts to authenticate it

        :param continuation: method to continue request once it has been validated
        :param handler_call_details: incoming request to validate
        :return: Awaitable[grpc.RpcMethodHandler] | None
        """

        expected_metadata: tuple = (self.signature_header, self.signature)

        # Extract the method type from the metatdata to invoke the proper abortion method
        method_type: str = dict(handler_call_details.invocation_metadata)['x-method-type']

        if expected_metadata in handler_call_details.invocation_metadata:
            return continuation(handler_call_details)

        # If unauthenticated, abort based on method_type
        else:
            if method_type == 'unary-unary':
                self._abort_unary_unary()
            elif method_type == 'unary-stream':
                self._abort_unary_stream()
            elif method_type == 'stream-unary':
                self._abort_stream_unary()
            elif method_type == 'stream-stream':
                self._abort_stream_stream()
            else:
                raise ValueError(f"Invalid method type provided {method_type}")