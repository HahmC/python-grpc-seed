import grpc_server_pb2 as GrpcServer

def get_area(shape: GrpcServer.Shape) -> float:
    """
    Calculates the area of the given shape using Gauss's Area formula for a polygon

    A = 1/2*abs(sum((x_i*y_i+1 - y_i*x_i+1)) + (x_n*y_1+y_n*x_1))

    :param shape: shape to calculate the area of
    :return: float - the area of the provided shape
    """
    area: float = 0.0

    n: int = len(shape.coords)  # Number of coordinates in the shape

    # Calculate the area of the shape using Gauss's area formula. i+1 % n connects the first point back to the last point
    for i in range(n):
        x1_y2: float = shape.coords[i].x * shape.coords[(i+1)%n].y
        x2_y1: float = shape.coords[(i+1)%n].x * shape.coords[i].y

        area += x1_y2 - x2_y1

    return abs(area) / 2
