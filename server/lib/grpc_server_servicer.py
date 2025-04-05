import os
import json
import time
from typing import Iterator, List

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
            response.shape.CopyFrom(shape)

        elif request.shape_type == "Rectangle":
            self.logger.info("Generating Rectangle...")

            # Generate Rectangle
            shape: GrpcServer.Shape = helpers.get_rectangle(len(self.data["Rectangles"]), self.max_width, self.max_height)
            shape_json: dict = helpers.get_json_from_shape(shape)
            self.data["Rectangles"].extend([shape_json])

            self.logger.info(f"Rectangle: {shape}")

            response.status_code = GrpcServer.Code.OK
            response.message = f"Successfully Created Rectangle: {shape_json}"
            response.shape.CopyFrom(shape)

        elif request.shape_type == "Pentagon":
            self.logger.info("Generating Pentagon...")

            # Generate Pentagon
            shape: GrpcServer.Shape = helpers.get_pentagon(len(self.data["Pentagons"]), self.max_width, self.max_height)
            shape_json: dict = helpers.get_json_from_shape(shape)
            self.data["Pentagons"].extend([shape_json])

            self.logger.info(f"Pentagon: {shape}")

            response.status_code = GrpcServer.Code.OK
            response.message = f"Successfully Created Pentagon: {shape_json}"
            response.shape.CopyFrom(shape)

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

        response: GrpcServer.GetShapeResponse = GrpcServer.GetShapeResponse(
            status_code=GrpcServer.Code.OK,
            message=""
        )

        try:
            # Attempt to locate the given shape_id, if not found, GrpcServer.Code statuses are used to record
            # the appropriate error
            shape: GrpcServer.Shape = self.__get_shape_from_id(request.shape_id, self.data)

            response.status_code = GrpcServer.Code.OK
            response.message = f"Successfully retrieved {request.shape_id}"
            response.shape.CopyFrom(shape)

        except LookupError as error:

            if int(str(error)) == GrpcServer.Code.INVALID_SHAPE:
                response.status_code = GrpcServer.Code.INVALID_SHAPE
                response.message = f"shape_id {request.shape_id} is not a valid shape_id"

            elif int(str(error)) == GrpcServer.Code.SHAPE_NOT_FOUND:
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

        self.logger.info(f"GetPerimetersGreaterThan called with {request}")

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
                perimeter: float = round(helpers.get_perimeter(shape), 2)

                self.logger.info(f"{shape.shape_id} - P={perimeter} units")

                if perimeter > request.min_perimeter:
                    found_shape = True

                    yield GrpcServer.GetPerimetersGreaterThanResponse(
                        status_code=GrpcServer.Code.OK,
                        message=f"{shape.shape_id} has a perimeter of {perimeter} units",
                        perimeter=perimeter,
                        shape=shape
                    )

                    time.sleep(1) # Added delay to visually see that the results are returned to the user as they become available

        # If no shapes found with perimeter greater than the specified minimum
        if not found_shape:
            yield GrpcServer.GetPerimetersGreaterThanResponse(
                status_code=GrpcServer.Code.SHAPE_NOT_FOUND,
                message=f"No shapes found with perimeter greater than {request.min_perimeter}."
            )

    def GetTotalArea(self, request: Iterator[GrpcServer.ShapeId], context) -> GrpcServer.GetTotalAreaResponse:
        """
        Given a list of shape_id, calculate and add up all the areas of all the existing shapes provided, and note which
        of the shape_ids requested do not exist

        :param request: List of shape_ids to sum the areas of
        :param context:
        :return: GrpcServer.GetTotalAreaResponse - the total area of all the existing shape_ids provided
        """

        self.logger.info(f"GetTotalArea called with a GrpcServer.ShapeId iterator")

        total_area: float = 0.0
        invalid_ids: List[GrpcServer.ShapeId] = []
        valid_ids: List[GrpcServer.ShapeId] = []

        response: GrpcServer.GetTotalAreaResponse = GrpcServer.GetTotalAreaResponse(
            status_code=GrpcServer.Code.OK,
            message=""
        )

        for shape_id in request:
            try:
                # Attempt to locate the given shape_id, if not found, GrpcServer.Code statuses are used to record
                # the appropriate error
                shape: GrpcServer.Shape = self.__get_shape_from_id(shape_id.shape_id)
                area = helpers.get_area(shape)

                total_area += area
                valid_ids.append(shape_id)

                self.logger.info(f"{shape_id.shape_id}: A={area} square units")
            except LookupError as error:
                self.logger.error(f"{shape_id.shape_id} not in database")
                if int(str(error)) == GrpcServer.Code.INVALID_SHAPE or int(str(error)) == GrpcServer.Code.SHAPE_NOT_FOUND:
                    invalid_ids.append(shape_id)

            self.logger.info(f"Total area at {total_area} square units")

        if total_area > 0:
            response.status_code = GrpcServer.Code.OK
            response.message = f"Total area of shapes {total_area} square units."
            response.total_area = total_area
            response.valid_ids.extend(valid_ids)
            response.invalid_ids.extend(invalid_ids)
        else:
            response.status_code = GrpcServer.Code.AREA_NOT_FOUND
            response.message = f"Invalid Area: {total_area}."
            response.invalid_ids.extend(invalid_ids)

        return response

    def GetAreas(self, request: Iterator[GrpcServer.ShapeId], context) -> Iterator[GrpcServer.GetAreasResponse]:
        """
        Given an iterator of shape_ids, return an iterator of the corresponding shape and it's area

        :param request: iterator of shape_ids
        :return: Iterator[GrpcServer.GetAreasResponse]
        """

        self.logger.info('GetAreas called with GrpcServer.ShapeId iterator')

        for shape_id in request:
            response: GrpcServer.GetAreasResponse = GrpcServer.GetAreasResponse(
                status_code=GrpcServer.Code.OK,
                message=""
            )

            try:
                # Attempt to locate the given shape_id, if not found, GrpcServer.Code statuses are used to record
                # the appropriate error
                shape: GrpcServer.Shape = self.__get_shape_from_id(shape_id.shape_id)
                area = helpers.get_area(shape)

                response.status_code = GrpcServer.Code.OK
                response.message = f"{shape.shape_id}: A={area} square units"
                response.area = area
                response.shape.CopyFrom(shape)

                self.logger.info(f"{shape_id.shape_id}: A={area} square units")
            except LookupError as error:
                self.logger.error(f"{shape_id.shape_id} not in database")
                if int(str(error)) == GrpcServer.Code.INVALID_SHAPE or int(str(error)) == GrpcServer.Code.SHAPE_NOT_FOUND:
                    response.status_code = GrpcServer.Code.AREA_NOT_FOUND
                    response.message = f"{shape_id.shape_id} does not exist"

            yield response

            time.sleep(1)

    def __get_shape_from_id(self, shape_id: str) -> GrpcServer.Shape:
        """
        Provided a shape_id attempt to locate it in the database, otherwise throw a LookupError with the appropriate
        GrpcServer.Code status code to indicate why the shape was not found

        :param shape_id: shape to lookup
        :return: GrpcServer.Shape
        """
        shape: GrpcServer.Shape = None

        shape_id: str = f"{shape_id[0].upper()}{shape_id[1:]}"  # Reformat shape_id
        shape_key: str = ""

        # Iterate over database trying to match the shape_type of the id to a shape_type in the database
        for key in self.data:
            if key[0] == shape_id[0]:
                shape_key = key

        if shape_key == "":
            raise LookupError(f"{GrpcServer.Code.INVALID_SHAPE}")

        # Once the proper shape_type has been identified, search for the shape_id in that list of shapes
        for s in self.data[shape_key]:
            if s['shape_id'] == shape_id:
                shape = helpers.get_shape_from_json(s)

        # Raise LookupError if a shape is not found in the database
        if shape is None:
            raise LookupError(f"{GrpcServer.Code.SHAPE_NOT_FOUND}")

        return shape
