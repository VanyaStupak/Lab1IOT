from marshmallow import Schema, fields
from domain.gps import Gps
from my_schema.gps_schema import GpsSchema

class ParkingSchema(Schema):
    free_parking = fields.Boolean()
    gps = fields.Nested(GpsSchema)