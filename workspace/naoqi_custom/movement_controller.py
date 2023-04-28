from workspace.location.locator_and_mapper import LocatorAndMapper
from workspace.naoqi_custom.video_controller import VideoController
from workspace.sonar.sonar_adapter import SonarAdapter
from workspace.sonar.map_display_adapter import MapDisplayAdapter
from workspace.location.qr_detector import QrDetector
from workspace.utils.geometry import distance, direction
import numpy as np

"""
Estrategia de movimiento:
    Supongamos que estamos en (Xs, Ys) y queremos ir a (Xe, Ye).

    1. Si estamos "cerca" de (Xe, Ye), terminamos, si no, ir al paso 2. 
    2. Conseguir el vector resultante de ir desde (Xs, Ys) hasta (Xe, Ye), llamemoslo 'v'.
    3. 
        * Si el angulo entre el pecho del Nao y 'v' es "chico", caminar "un poco" e ir al paso 1.
        * Si no, ir al paso 4.
    4. Girar el pecho del Nao hasta que el ángulo formado entre su cuerpo y el vector 'v' sea lo suficientemente chico.
    5. Ir al paso 1.
"""


class MovementController:
    """
    The class `MovementController` provides a simple API to control the movement of the robot.

    Attributes
    ----------
    locator_and_mapper : LocatorAndMapper
        The locator and mapper instance to localize the robot's position.
    video_controller : VideoController
        The video controller instance to get the robot's point of view images.
    sonar_enable : bool
        Whether the sonar sensors are enabled or not.
    sonar_adapter : SonarAdapter
        The sonar adapter instance to process the sonar data.
    map_display_enable : bool
        Whether the map display is enabled or not.
    map_display_adapter : MapDisplayAdapter
        The map display adapter instance to display the robot's location on the map.

    """

    def __init__(self, session, ip, port, sonar_enable=False, map_display_enable=False):
        # type: (qi.Session, str, int, bool, bool) -> MovementController
        """
        Initializes a new instance of `MovementController`.

        Parameters
        ----------
        session : qi.Session
            The session object to connect to the robot.
        ip : str
            The IP address of the robot.
        port : int
            The port number to connect to the robot.
        sonar_enable : bool, optional
            Whether to enable the sonar sensors or not (default is False).
        map_display_enable : bool, optional
            Whether to enable the map display or not (default is False).

        """
        # subscribe to the motion service of the NAO
        self.service = session.service("ALMotion")

        self.locator_and_mapper = LocatorAndMapper()
        self.video_controller = VideoController(ip, port)
        self.sonar_enable = sonar_enable
        self.sonar_adapter = SonarAdapter()
        self.map_display_enable = map_display_enable
        self.map_display_adapter = MapDisplayAdapter()

        # execute the first location information inquiry
        self.__add_information()

    def __add_information(self):
        # type: () -> None
        """
        Adds information to the locator and mapper instance.

        """
        # get the grey image from the pov of the robot
        gray_image = self.video_controller.get_current_gray_pov()

        # extract all qr data on that image onto a list
        qrs_data = QrDetector.get_qrs_information(gray_image)

        # add the extracter qr data to the locator and mapper
        self.locator_and_mapper.add_information(qrs_data)

        # update displays (if enabled)
        self.__update_sonar_and_map_dislay(qrs_data)

    def __update_sonar_and_map_dislay(self, qrs_data):
        # type: (list[QRData]) -> None
        """
        Updates the sonar and map display data.

        Parameters
        ----------
        qrs_data : list of QRData
            The QR codes data.
        """
        # write the qrs data on the sonar if enable
        if self.sonar_enable:
            self.sonar_adapter.write_data(qrs_data)

        # write the qrs data and nao location on the sonar if enable
        if self.map_display_enable:
            self.map_display_adapter.write_data(
                self.locator_and_mapper.get_nao_location(),
                self.locator_and_mapper.qrs_data,
            )

    def __close_enough(nao_location, target_location):
        # type: (tuple[int, int], tuple[int, int]) -> bool
        """
        Decides whether the NAO is close enough to the desired location

        Parameters
        ----------
        nao_location : tuple[int, int]
            Nao's current location
        target_location : tuple[int, int]
            Desired location

        Returns
        -------
        bool
            Whether the NAO is close enough to the desired location
        """
        return distance(nao_location, target_location) < 10

    def go_to(self, target_location):
        # type: (tuple[int, int]) -> bool
        """
        Move to the new target location.
        It decide wheter it is in said lcoation via the definition of close enough.

        Parameters
        ----------
        target_location : tuple of int
            The desired location to move
        """
        # get the current nao location
        nao_location = self.locator_and_mapper.get_nao_location()

        # if close enough to the desired location return true
        if self.__close_enough(nao_location, target_location):
            return True

        # else get the target direction to move to it
        target_direction = direction(nao_location, target_location)

        # TODO: is something missing here?
