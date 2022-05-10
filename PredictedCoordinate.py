class PredictedCoordinate:
    '''
    Class for representing one cameras prediction of a darts location. Used by CoordinateProjector.py.
    Needed when deleting bad coordinates while still knowing what camera is associated with the other coordinates.
    (easier to read the code this way imo)
    ''' 
    def __init__(self, x, y, camera_index):
        self.x = x
        self.y = y
        self.camera_index = camera_index

    def get_x(self):
        return self.x
    def get_y(self):
        return self.y
    def get_camera_index(self):
        return self.camera_index
