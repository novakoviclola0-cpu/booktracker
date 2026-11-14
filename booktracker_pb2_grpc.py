import grpc

import booktracker_pb2 as pb


class BookServiceStub:
    def __init__(self, channel):
        self.GetBooks = channel.unary_unary(
            "/booktracker.BookService/GetBooks",
            request_serializer=pb.BooksRequest.SerializeToString,
            response_deserializer=pb.BooksResponse.FromString,
        )
        self.GetBook = channel.unary_unary(
            "/booktracker.BookService/GetBook",
            request_serializer=pb.BookRequest.SerializeToString,
            response_deserializer=pb.Book.FromString,
        )
        self.GetStatistics = channel.unary_unary(
            "/booktracker.BookService/GetStatistics",
            request_serializer=pb.StatisticsRequest.SerializeToString,
            response_deserializer=pb.StatisticsResponse.FromString,
        )
        self.StreamBooks = channel.unary_stream(
            "/booktracker.BookService/StreamBooks",
            request_serializer=pb.BooksRequest.SerializeToString,
            response_deserializer=pb.Book.FromString,
        )


class BookServiceServicer:
    def GetBooks(self, request, context):
        raise NotImplementedError()

    def GetBook(self, request, context):
        raise NotImplementedError()

    def GetStatistics(self, request, context):
        raise NotImplementedError()

    def StreamBooks(self, request, context):
        raise NotImplementedError()


def add_BookServiceServicer_to_server(servicer, server):
    handlers = {
        "GetBooks": grpc.unary_unary_rpc_method_handler(
            servicer.GetBooks,
            request_deserializer=pb.BooksRequest.FromString,
            response_serializer=pb.BooksResponse.SerializeToString,
        ),
        "GetBook": grpc.unary_unary_rpc_method_handler(
            servicer.GetBook,
            request_deserializer=pb.BookRequest.FromString,
            response_serializer=pb.Book.SerializeToString,
        ),
        "GetStatistics": grpc.unary_unary_rpc_method_handler(
            servicer.GetStatistics,
            request_deserializer=pb.StatisticsRequest.FromString,
            response_serializer=pb.StatisticsResponse.SerializeToString,
        ),
        "StreamBooks": grpc.unary_stream_rpc_method_handler(
            servicer.StreamBooks,
            request_deserializer=pb.BooksRequest.FromString,
            response_serializer=pb.Book.SerializeToString,
        ),
    }
    server.add_generic_rpc_handlers((grpc.method_handlers_generic_handler("booktracker.BookService", handlers),))
