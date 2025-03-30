import pandas as pd
from datetime import datetime
from domain.aggregated_data import AggregatedData
from domain.accelerometer import Accelerometer
from domain.gps import Gps
from domain.parking import Parking

class FileDatasource:
    def __init__(self, accelerometer_filename: str, gps_filename: str, parking_filename: str) -> None:
        self.accelerometer_filename = accelerometer_filename
        self.gps_filename = gps_filename
        self.parking_filename = parking_filename

        self.accelerometer_data = None
        self.gps_data = None
        self.parking_data = None

        self.gps_row_amount = 0
        self.accelerometr_row_amount = 0
        self.parking_row_amount = 0

        self.gps_counter = 0
        self.accelerometr_counter = 0
        self.parking_counter = 0

    def read_aggregated_data(self) -> AggregatedData:
        """Read data from files and return AggregatedData instance."""
        
        self.read_accelerometer_data()
        self.read_gps_data()
        self.read_parking_data()
        return AggregatedData(accelerometer=self.accelerometer_data, gps=self.gps_data, time=datetime.now(), parking=self.parking_data)

    def read_parking_data(self) -> Parking:
        self.read_gps_data()
        self.read_parking_data_from_csv()
        return self.parking_data
    
    def startReading(self, *args, **kwargs):
        """Метод повинен викликатись перед початком читання даних"""
        self.accelerometer_df = pd.read_csv(self.accelerometer_filename)
        self.gps_df = pd.read_csv(self.gps_filename)
        self.parking_df = pd.read_csv(self.parking_filename)

        self.gps_row_amount = self.gps_df.shape[0]
        self.accelerometr_row_amount = self.accelerometer_df.shape[0]
        self.parking_row_amount = self.parking_df.shape[0]


    def stopReading(self, *args, **kwargs):
        """Метод повинен викликатись для закінчення читання даних"""
        # No need to close files explicitly with pandas

    def read_accelerometer_data(self):
        """Read accelerometer data from file."""
        row = self.accelerometer_df.iloc[self.accelerometr_counter] # Read the first row
        self.accelerometer_data = Accelerometer(int(row[0]), int(row[1]), int(row[2]))
        self.accelerometr_counter += 1
        self.accelerometr_counter %= self.accelerometr_row_amount

    def read_gps_data(self):
        """Read GPS data from file."""
        row = self.gps_df.iloc[self.gps_counter] # Read the first row
        self.gps_data = Gps(float(row[0]), float(row[1]))
        self.gps_counter += 1
        self.gps_counter %= self.gps_row_amount

    def read_parking_data_from_csv(self):
        """Read GPS data from file."""
        row = self.parking_df.iloc[self.parking_counter] # Read the first row
        self.parking_data = Parking( bool(row[0]), self.gps_data)
        self.parking_counter += 1
        self.parking_counter %= self.parking_row_amount

  