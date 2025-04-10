import os
import json
import time
import math
import random
from typing import Iterator, List

from .logger import Logger
import shape_service_pb2 as ShapeService
import shape_service_pb2_grpc as ShapeServiceGrpc
from correlation_id_context import set_correlation_id

class ShapeServer(ShapeServiceGrpc.ShapeService):
    """
    Shape Server - gRPC server serving all the methods defined in proto/shape_service.proto
    """

    def __init__(self, logger: Logger, config: dict):
        self.logger: Logger = logger
        self.config: dict = config
        self.db_path: str = self.config['general']['json_path']
        self.max_height: int = int(self.config['shape']['max_height'])
        self.max_width: int = int(self.config['shape']['max_width'])

        # If database .json exists use that file, otherwise create a new one
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r') as json_file:
                    self.data = json.load(json_file)
            except IOError as e:
                logger.error(f"Could not load json file: {e}")
        else:
            self.data = {"Triangles": [], "Rectangles": [], "Pentagons":[]}

    def CreateShape(self, request: ShapeService.ShapeType, context) -> ShapeService.CreateShapeResponse:
        """
        Create the shape specified by the user, giving it an id and coordinates

        :param request: The type of shape to create
        :param context: context to support error codes
        :return: CreateShapeResponse - pre-defined proto response to this method containing a status code, message
        """

        # Extract metadata from context and set the correlation_id so that all logs from this invocation contain
        # the correlation_id of the call
        metadata = {key: value for key, value in context.invocation_metadata()}

        with set_correlation_id(metadata['x-correlation-id']):
            self.logger.info(f"CreateShape called with request: {request}")

            response: ShapeService.CreateShapeResponse = ShapeService.CreateShapeResponse(
                status_code=ShapeService.Code.OK,
                message=""
            )

            if request.shape_type == "Triangle":
                self.logger.info("Generating Triangle...")

                # Generate Triangle
                shape: ShapeService.Shape = self.__get_triangle()
                shape_json: dict = self.__get_json_from_shape(shape)
                self.data["Triangles"].extend([shape_json])

                self.logger.info(f"Triangle: {shape}")

                response.status_code = ShapeService.Code.OK
                response.message = f"Successfully Created Triangle: {shape_json}"
                response.shape.CopyFrom(shape)

            elif request.shape_type == "Rectangle":
                self.logger.info("Generating Rectangle...")

                # Generate Rectangle
                shape: ShapeService.Shape = self.__get_rectangle()
                shape_json: dict = self.__get_json_from_shape(shape)
                self.data["Rectangles"].extend([shape_json])

                self.logger.info(f"Rectangle: {shape}")

                response.status_code = ShapeService.Code.OK
                response.message = f"Successfully Created Rectangle: {shape_json}"
                response.shape.CopyFrom(shape)

            elif request.shape_type == "Pentagon":
                self.logger.info("Generating Pentagon...")

                # Generate Pentagon
                shape: ShapeService.Shape = self.__get_pentagon()
                shape_json: dict = self.__get_json_from_shape(shape)
                self.data["Pentagons"].extend([shape_json])

                self.logger.info(f"Pentagon: {shape}")

                response.status_code = ShapeService.Code.OK
                response.message = f"Successfully Created Pentagon: {shape_json}"
                response.shape.CopyFrom(shape)

            else:
                response.status_code = ShapeService.Code.INVALID_SHAPE
                response.message = f"shape_type {request.shape_type} is not supported at this time"

            # Write data back to db file
            try:
                with open(self.db_path, 'w') as json_file:
                    json.dump(self.data, json_file, indent=4)
                self.logger.info(f"Data successfully written to {self.db_path}")
            except IOError as e:
                self.logger.error(f"Error writing to file: {e}")

            return response

    def GetShape(self, request: ShapeService.ShapeId, context) -> ShapeService.GetShapeResponse:
        """
        Retrieves the requested shape from the database using the shape_id and returns it to the user if present,
        otherwise throws

        :param request: gRPC Request containing the id to lookup
        :param context:
        :return: GetShapeResponse - pre-defined proto response to this method containing a status code, message, and shape
                 if a shape was found
        """

        # Extract metadata from context and set the correlation_id so that all logs from this invocation contain
        # the correlation_id of the call
        metadata = {key: value for key, value in context.invocation_metadata()}

        with set_correlation_id(metadata['x-correlation-id']):
            self.logger.info(f"GetShape called with request: {request}")

            response: ShapeService.GetShapeResponse = ShapeService.GetShapeResponse(
                status_code=ShapeService.Code.OK,
                message=""
            )

            try:
                # Attempt to locate the given shape_id, if not found, ShapeService.Code statuses are used to record
                # the appropriate error
                shape: ShapeService.Shape = self.__get_shape_from_id(request.shape_id)

                response.status_code = ShapeService.Code.OK
                response.message = f"Successfully retrieved {request.shape_id}"
                response.shape.CopyFrom(shape)

            except LookupError as error:

                if int(str(error)) == ShapeService.Code.INVALID_SHAPE:
                    response.status_code = ShapeService.Code.INVALID_SHAPE
                    response.message = f"shape_id {request.shape_id} is not a valid shape_id"

                elif int(str(error)) == ShapeService.Code.SHAPE_NOT_FOUND:
                    response.status_code = ShapeService.Code.SHAPE_NOT_FOUND
                    response.message = f"shape_id {request.shape_id} not found in database"

            return response

    def GetPerimetersGreaterThan(self, request: ShapeService.MinPerimeter, context) -> Iterator[ShapeService.GetPerimetersGreaterThanResponse]:
        """
        Retrieves all the shapes with a perimeter greater than the specified value and returns them to the user

        :param request: minimum perimeter value
        :param context:
        :return: iterable object of all the shapes with a perimeter greater than the provided value
        """

        # Extract metadata from context and set the correlation_id so that all logs from this invocation contain
        # the correlation_id of the call
        metadata = {key: value for key, value in context.invocation_metadata()}

        with set_correlation_id(metadata['x-correlation-id']):
            self.logger.info(f"GetPerimetersGreaterThan called with {request}")

            if request.min_perimeter < 0:
                yield ShapeService.GetPerimetersGreaterThanResponse(
                    status_code=ShapeService.Code.INVALID_PERIMETER,
                    message=f"{request.min_perimeter} is an invalid perimeter value. Perimeters must be greater than or equal to 0"
                )

                return

            found_shape: bool = False

            for shape_type in self.data:
                self.logger.info(f"Calculating perimeters of {shape_type}.....")

                for s in self.data[shape_type]:
                    shape: ShapeService.Shape = self.__get_shape_from_json(s)
                    perimeter: float = round(self.__get_perimeter(shape), 2)

                    self.logger.info(f"{shape.shape_id} - P={perimeter} units")

                    if perimeter > request.min_perimeter:
                        found_shape = True

                        yield ShapeService.GetPerimetersGreaterThanResponse(
                            status_code=ShapeService.Code.OK,
                            message=f"{shape.shape_id} has a perimeter of {perimeter} units",
                            perimeter=perimeter,
                            shape=shape
                        )

                        time.sleep(1) # Added delay to visually see that the results are returned to the user as they become available

            # If no shapes found with perimeter greater than the specified minimum
            if not found_shape:
                yield ShapeService.GetPerimetersGreaterThanResponse(
                    status_code=ShapeService.Code.SHAPE_NOT_FOUND,
                    message=f"No shapes found with perimeter greater than {request.min_perimeter}."
                )

    def GetTotalArea(self, request: Iterator[ShapeService.ShapeId], context) -> ShapeService.GetTotalAreaResponse:
        """
        Given a list of shape_id, calculate and add up all the areas of all the existing shapes provided, and note which
        of the shape_ids requested do not exist

        :param request: List of shape_ids to sum the areas of
        :param context:
        :return: ShapeService.GetTotalAreaResponse - the total area of all the existing shape_ids provided
        """

        # Extract metadata from context and set the correlation_id so that all logs from this invocation contain
        # the correlation_id of the call
        metadata = {key: value for key, value in context.invocation_metadata()}

        with set_correlation_id(metadata['x-correlation-id']):
            self.logger.info(f"GetTotalArea called with a ShapeService.ShapeId iterator")

            total_area: float = 0.0
            invalid_ids: List[ShapeService.ShapeId] = []
            valid_ids: List[ShapeService.ShapeId] = []

            response: ShapeService.GetTotalAreaResponse = ShapeService.GetTotalAreaResponse(
                status_code=ShapeService.Code.OK,
                message=""
            )

            for shape_id in request:
                try:
                    # Attempt to locate the given shape_id, if not found, ShapeService.Code statuses are used to record
                    # the appropriate error
                    shape: ShapeService.Shape = self.__get_shape_from_id(shape_id.shape_id)
                    area = self.__get_area(shape)

                    total_area += area
                    valid_ids.append(shape_id)

                    self.logger.info(f"{shape_id.shape_id}: A={area} square units")
                except LookupError as error:
                    self.logger.error(f"{shape_id.shape_id} not in database")
                    if int(str(error)) == ShapeService.Code.INVALID_SHAPE or int(str(error)) == ShapeService.Code.SHAPE_NOT_FOUND:
                        invalid_ids.append(shape_id)

                self.logger.info(f"Total area at {total_area} square units")

            if total_area > 0:
                response.status_code = ShapeService.Code.OK
                response.message = f"Total area of shapes {total_area} square units."
                response.total_area = total_area
                response.valid_ids.extend(valid_ids)
                response.invalid_ids.extend(invalid_ids)
            else:
                response.status_code = ShapeService.Code.AREA_NOT_FOUND
                response.message = f"Invalid Area: {total_area}."
                response.invalid_ids.extend(invalid_ids)

            return response

    def GetAreas(self, request: Iterator[ShapeService.ShapeId], context) -> Iterator[ShapeService.GetAreasResponse]:
        """
        Given an iterator of shape_ids, return an iterator of the corresponding shape and it's area

        :param request: iterator of shape_ids
        :param context:
        :return: Iterator[ShapeService.GetAreasResponse]
        """

        # Extract metadata from context and set the correlation_id so that all logs from this invocation contain
        # the correlation_id of the call
        metadata = {key: value for key, value in context.invocation_metadata()}

        with set_correlation_id(metadata['x-correlation-id']):
            self.logger.info('GetAreas called with ShapeService.ShapeId iterator')

            for shape_id in request:
                response: ShapeService.GetAreasResponse = ShapeService.GetAreasResponse(
                    status_code=ShapeService.Code.OK,
                    message=""
                )

                try:
                    # Attempt to locate the given shape_id, if not found, ShapeService.Code statuses are used to record
                    # the appropriate error
                    shape: ShapeService.Shape = self.__get_shape_from_id(shape_id.shape_id)
                    area = self.__get_area(shape)

                    response.status_code = ShapeService.Code.OK
                    response.message = f"{shape.shape_id}: A={area} square units"
                    response.area = area
                    response.shape.CopyFrom(shape)

                    self.logger.info(f"{shape_id.shape_id}: A={area} square units")
                except LookupError as error:
                    self.logger.error(f"{shape_id.shape_id} not in database")
                    if int(str(error)) == ShapeService.Code.INVALID_SHAPE or int(str(error)) == ShapeService.Code.SHAPE_NOT_FOUND:
                        response.status_code = ShapeService.Code.AREA_NOT_FOUND
                        response.message = f"{shape_id.shape_id} does not exist"

                yield response

                time.sleep(1)

    def __get_shape_from_id(self, shape_id: str) -> ShapeService.Shape:
        """
        Provided a shape_id attempt to locate it in the database, otherwise throw a LookupError with the appropriate
        ShapeService.Code status code to indicate why the shape was not found

        :param shape_id: shape to lookup
        :return: ShapeService.Shape
        """
        shape: ShapeService.Shape = None

        shape_id: str = f"{shape_id[0].upper()}{shape_id[1:]}"  # Reformat shape_id
        shape_key: str = ""

        # Iterate over database trying to match the shape_type of the id to a shape_type in the database
        for key in self.data:
            if key[0] == shape_id[0]:
                shape_key = key

        if shape_key == "":
            raise LookupError(f"{ShapeService.Code.INVALID_SHAPE}")

        # Once the proper shape_type has been identified, search for the shape_id in that list of shapes
        for s in self.data[shape_key]:
            if s['shape_id'] == shape_id:
                shape = self.__get_shape_from_json(s)

        # Raise LookupError if a shape is not found in the database
        if shape is None:
            raise LookupError(f"{ShapeService.Code.SHAPE_NOT_FOUND}")

        return shape
    
    def __get_triangle (self) -> ShapeService.Shape:
        """
        Generates a triangle with a random width and height
    
        :return: ShapeService.Shape that is a triangle
        """
        width: int = 2*random.randint(1, self.max_width) # double the width to make division easy for middle point
        height: int = random.randint(1, self.max_height)
    
        coordinates: List[ShapeService.ShapeCoord] = [
            ShapeService.ShapeCoord(x=0, y=0),
            ShapeService.ShapeCoord(x=int(width/2), y=height),
            ShapeService.ShapeCoord(x=width, y=0)
        ]
    
        triangle: ShapeService.Shape = ShapeService.Shape(
            shape_id=f"T-{len(self.data['Triangles'])}",
            shape_type="Triangle"
        )
        triangle.coords.extend(coordinates)
    
        return triangle

    def __get_rectangle(self) -> ShapeService.Shape:
        """
        Generates a rectangle with a random width and height

        :return: ShapeService.Shape that is a rectangle
        """
        width: int = random.randint(1, self.max_width)  # double the height to make division easy for middle point
        height: int = random.randint(1, self.max_height)

        coordinates: List[ShapeService.ShapeCoord] = [
            ShapeService.ShapeCoord(x=0, y=0),
            ShapeService.ShapeCoord(x=0, y=height),
            ShapeService.ShapeCoord(x=width, y=height),
            ShapeService.ShapeCoord(x=width, y=0)
        ]

        rectangle: ShapeService.Shape = ShapeService.Shape(
            shape_id=f"R-{len(self.data['Rectangles'])}",
            shape_type="rectangle"
        )
        rectangle.coords.extend(coordinates)

        return rectangle

    def __get_pentagon(self) -> ShapeService.Shape:
        """
        Generates a pentagon with a random width and height

        :return: ShapeService.Shape that is a pentagon
        """
        width: int = 2 * random.randint(1, self.max_width)  # double the width to make division easy for middle point
        height: int = 2 * random.randint(1,
                                         self.max_height)  # double the height to make integer division easier for middle height

        coordinates: List[ShapeService.ShapeCoord] = [
            ShapeService.ShapeCoord(x=0, y=0),
            ShapeService.ShapeCoord(x=0, y=int(height / 2)),
            ShapeService.ShapeCoord(x=int(width / 2), y=height),
            ShapeService.ShapeCoord(x=width, y=int(height / 2)),
            ShapeService.ShapeCoord(x=width, y=0)
        ]

        pentagon: ShapeService.Shape = ShapeService.Shape(
            shape_id=f"P-{len(self.data['Pentagons'])}",
            shape_type="pentagon"
        )
        pentagon.coords.extend(coordinates)

        return pentagon

    def __get_json_from_shape(self, shape: ShapeService.Shape) -> dict:
        """
        Takes a gRCP server Shape and returns a serializable object

        :param shape: gRPC Shape
        :return: serializable object
        """
        shape_json: dict = {
            "shape_id": shape.shape_id,
            "shape_type": shape.shape_type,
            "coords": []
        }

        json_coords: List[dict] = []

        for c in shape.coords:
            json_coords.append({
                "x": c.x,
                "y": c.y
            })

        shape_json["coords"].extend(json_coords)

        return shape_json

    def __get_shape_from_json(self, json_shape: dict) -> ShapeService.Shape:
        """
        Takes a JSON object and converts it back to a gRPC Shape

        :param json_shape: JSON object to convert back to gRPC Shape
        :return: gRPC Shape
        """
        shape: ShapeService.Shape = ShapeService.Shape(
            shape_id=json_shape['shape_id'],
            shape_type=json_shape['shape_type']
        )

        shape_coords: List[ShapeService.ShapeCoord] = []

        for c in json_shape['coords']:
            shape_coords.append(
                ShapeService.ShapeCoord(x=int(c['x']), y=int(c['y']))
            )

        shape.coords.extend(shape_coords)

        return shape

    def __get_perimeter(self, shape: ShapeService.Shape) -> float:
        """
        Calculates the perimeter of the given shape

        :param shape: shape to calculate the perimeter of
        :return: float - the perimeter of the provided shape
        """
        perimeter: float = 0.0

        n: int = len(shape.coords)  # Number of coordinates in the shape

        # Calculate the distance between each set of points and add them up. i+1 % n connects the first point back to the last point
        for i in range(n):
            x_sq_diff: float = (shape.coords[(i + 1) % n].x - shape.coords[i].x) ** 2
            y_sq_diff: float = (shape.coords[(i + 1) % n].y - shape.coords[i].y) ** 2

            perimeter += math.sqrt(x_sq_diff + y_sq_diff)

        return perimeter

    def __get_area(self, shape: ShapeService.Shape) -> float:
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
            x1_y2: float = shape.coords[i].x * shape.coords[(i + 1) % n].y
            x2_y1: float = shape.coords[(i + 1) % n].x * shape.coords[i].y

            area += x1_y2 - x2_y1

        return abs(area) / 2
