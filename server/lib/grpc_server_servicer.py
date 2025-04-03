import os
import json
import time
from typing import Iterator

import lib.functions as helpers
import grpc_server_pb2 as GrpcServer
import grpc_server_pb2_grpc as GrpcServerService
from .logger import Logger

class GrpcServerServicer(GrpcServerService.GrpcServerServicer):
    """
    GRPC Server Servicer - gRPC server serving all the methods defined in proto/grpc_server.proto
    """

    def __init__(self, logger, db_path, shape_limits):
        self.logger: Logger = logger
        self.db_path: str = db_path
        self.max_height: int = int(shape_limits['max_height'])
        self.max_width: int = int(shape_limits['max_width'])

        # If database .json exists use that file, otherwise create a new one
        if os.path.exists(db_path):
            try:
                with open(db_path, 'r') as json_file:
                    self.data = json.load(json_file)
            except IOError as e:
                logger.error(f"Could not load json file: {e}")
        else:
            self.data = {"Triangles": [], "Rectangles": [], "Pentagons":[]}

    def CreateShape(self, request: GrpcServer.ShapeType, context) -> GrpcServer.CreateShapeResponse:
        """
        Create the shape specified by the user, giving it an id and coordinates

        :param request: The type of shape to create
        :param context: context to support error codes
        :return: CreateShapeResponse - pre-defined proto response to this method containing a status code, message
        """
        self.logger.info(f"CreateShape called with request: {request}")

        response: GrpcServer.CreateShapeResponse = GrpcServer.CreateShapeResponse(
            status_code=GrpcServer.Code.OK,
            message=""
        )

        if request.shape_type == "Triangle":
            self.logger.info("Generating Triangle...")

            # Generate Triangle
            shape: GrpcServer.Shape = helpers.get_triangle(len(self.data["Triangles"]), self.max_width, self.max_height)
            shape_json: dict = helpers.get_json_from_shape(shape)
            self.data["Triangles"].extend([shape_json])

            self.logger.info(f"Triangle: {shape}")

            response.status_code = GrpcServer.Code.OK
            response.message = f"Successfully Created Triangle: {shape_json}"

        elif request.shape_type == "Rectangle":
            self.logger.info("Generating Rectangle...")

            # Generate Rectangle
            shape: GrpcServer.Shape = helpers.get_rectangle(len(self.data["Rectangles"]), self.max_width, self.max_height)
            shape_json: dict = helpers.get_json_from_shape(shape)
            self.data["Rectangles"].extend([shape_json])

            self.logger.info(f"Rectangle: {shape}")

            response.status_code = GrpcServer.Code.OK
            response.message = f"Successfully Created Rectangle: {shape_json}"

        elif request.shape_type == "Pentagon":
            self.logger.info("Generating Pentagon...")

            # Generate Pentagon
            shape: GrpcServer.Shape = helpers.get_pentagon(len(self.data["Pentagons"]), self.max_width, self.max_height)
            shape_json: dict = helpers.get_json_from_shape(shape)
            self.data["Pentagons"].extend([shape_json])

            self.logger.info(f"Pentagon: {shape}")

            response.status_code = GrpcServer.Code.OK
            response.message = f"Successfully Created Pentagon: {shape_json}"

        else:
            response.status_code = GrpcServer.Code.INVALID_SHAPE
            response.message = f"shape_type {request.shape_type} is not supported at this time"

        # Write data back to db file
        try:
            with open(self.db_path, 'w') as json_file:
                json.dump(self.data, json_file, indent=4)
            self.logger.info(f"Data successfully written to {self.db_path}")
        except IOError as e:
            self.logger.error(f"Error writing to file: {e}")

        return response

    def GetShape(self, request: GrpcServer.ShapeId, context) -> GrpcServer.GetShapeResponse:
        """
        Retrieves the requested shape from the database using the shape_id and returns it to the user if present,
        otherwise throws

        :param request: gRPC Request containing the id to lookup
        :param context:
        :return: GetShapeResponse - pre-defined proto response to this method containing a status code, message, and shape
                 if a shape was found
        """
        self.logger.info(f"GetShape called with request: {request}")

        shape_id: str = f"{request.shape_id[0].upper()}{request.shape_id[1:]}" # Reformat shape_id

        response: GrpcServer.GetShapeResponse = GrpcServer.GetShapeResponse(
            status_code=GrpcServer.Code.OK,
            message=""
        )

        shape: GrpcServer.Shape = None

        # Iterate through database looking for the given shape id
        if shape_id[0] == "T":
            for t in self.data["Triangles"]:
                if t['shape_id'] == shape_id:
                    shape: GrpcServer.Shape = helpers.get_shape_from_json(t)
                    break

        elif shape_id[0] == "R":
            for t in self.data["Rectangles"]:
                if t['shape_id'] == shape_id:
                    shape: GrpcServer.Shape = helpers.get_shape_from_json(t)
                    break

        elif shape_id[0] == "P":
            for t in self.data["Pentagons"]:
                if t['shape_id'] == shape_id:
                    shape: GrpcServer.Shape = helpers.get_shape_from_json(t)
                    break

        else:
            response.status_code = GrpcServer.Code.INVALID_SHAPE
            response.message = f"shape_id {request.shape_id} is not a valid shape_id"

        if shape:
            response.status_code = GrpcServer.Code.OK
            response.message = f"Successfully retrieved {shape_id}"
            response.shape.CopyFrom(shape)

        else:
            response.status_code = GrpcServer.Code.SHAPE_NOT_FOUND
            response.message = f"shape_id {request.shape_id} not found in database"

        return response

    def GetPerimetersGreaterThan(self, request: GrpcServer.MinPerimeter, context) -> Iterator[GrpcServer.GetPerimetersGreaterThanResponse]:
        """
        Retrieves all the shapes with a perimeter greater than the specified value and returns them to the user

        :param request: minimum perimeter value
        :param context:
        :return: iterable object of all the shapes with a perimeter greater than the provided value
        """

        if request.min_perimeter < 0:
            yield GrpcServer.GetPerimetersGreaterThanResponse(
                status_code=GrpcServer.Code.INVALID_PERIMETER,
                message=f"{request.min_perimeter} is an invalid perimeter value. Perimeters must be greater than or equal to 0"
            )

            return

        found_shape: bool = False

        for shape_type in self.data:
            self.logger.info(f"Calculating perimeters of {shape_type}.....")

            for s in self.data[shape_type]:
                shape: GrpcServer.Shape = helpers.get_shape_from_json(s)
                perimeter: float = helpers.get_perimeter(shape)

                self.logger.info(f"{shape.shape_id} - P={round(perimeter, 2)} units")

                if perimeter > request.min_perimeter:
                    found_shape = True

                    yield GrpcServer.GetPerimetersGreaterThanResponse(
                        status_code=GrpcServer.Code.OK,
                        message=f"{shape.shape_id} has a perimeter of {round(perimeter, 2)} units",
                        shape=shape
                    )

                    time.sleep(1) # Added delay to visually see that the results are returned to the user as they become available

        # If no shapes found with perimeter greater than the specified minimum
        if not found_shape:
            yield GrpcServer.GetPerimetersGreaterThanResponse(
                status_code=GrpcServer.Code.SHAPE_NOT_FOUND,
                message=f"No shapes found with perimeter greater than {request.min_perimeter}."
            )