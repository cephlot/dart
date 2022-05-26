class PredictedCoordinate:
    """Class for representing one cameras prediction of a dart's location. Used 
    by CordinateProjector. Needed when deleting bad coordinates while still 
    knowing what camera is assoctated with the other coordinates (easier to read
    the code this way)
    """
    def __init__(self, x, y, camera_index):
        self.x = x
        self.y = y
        self.camera_index = camera_index

    def get_x(self):
        """Gets the x value

        :return: x value of self
        :rtype: int
        """

        return self.x

    def get_y(self):
        """Gets the y value

        :return: y value of self
        :rtype: int
        """

        return self.y

    def get_camera_index(self):
        """Gets camera index

        :return: camera index of self
        :rtype: int
        """

        return self.camera_index
