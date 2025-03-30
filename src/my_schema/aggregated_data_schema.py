from marshmallow import Schema, fields
from my_schema.accelerometer_schema import AccelerometerSchema
from my_schema.gps_schema import GpsSchema
from my_schema.parking_schema import ParkingSchema
from domain.aggregated_data import AggregatedData

class AggregatedDataSchema(Schema):
    accelerometer = fields.Nested(AccelerometerSchema)
    gps = fields.Nested(GpsSchema)
    time = fields.DateTime('iso')
    parking = fields.Nested(ParkingSchema)