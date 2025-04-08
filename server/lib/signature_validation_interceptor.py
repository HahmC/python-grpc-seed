import grpc
from typing import Awaitable, Callable

class SignatureValidationInterceptor(grpc.aio.ServerInterceptor):
    def __init__(self, sig_header: str, sig_value: str):
        def abort(ignored_request, context):
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid signature")

        self.signature_header = sig_header
        self.signature = sig_value
        self._abort_unary_unary = grpc.unary_unary_rpc_method_handler(abort)
        self._abort_unary_stream = grpc.unary_stream_rpc_method_handler(abort)
        self._abort_stream_unary = grpc.stream_unary_rpc_method_handler(abort)
        self._abort_stream_stream = grpc.stream_stream_rpc_method_handler(abort)
        self._abortion = self._abort_unary_unary

    def intercept_service(self, continuation: Callable[
            [grpc.HandlerCallDetails], Awaitable[grpc.RpcMethodHandler]
        ], handler_call_details: grpc.HandlerCallDetails):
        expected_metadata: tuple = (self.signature_header, self.signature)

        if expected_metadata in handler_call_details.invocation_metadata:
            return continuation(handler_call_details)
        else:
            self._abortion()