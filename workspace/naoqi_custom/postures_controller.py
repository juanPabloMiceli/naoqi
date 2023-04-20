
import qi
from argparse import ArgumentParser, RawTextHelpFormatter
import sys

from workspace.naoqi_custom.nao_properties import NaoProperties

class PosturesController:

    __raw_string_to_valid_string_dict = {
            "standinit": "StandInit",
            "sitrelax": "SitRelax",
            "standzero": "StandZero",
            "lyingbelly": "LyingBelly",
            "lyingback": "LyingBack",
            "stand": "Stand",
            "crouch": "Crouch",
            "sit": "Sit",
        }

    def __init__(self, session):
        self.service = session.service("ALRobotPosture")

    def move_to(self, posture_raw_string):
        posture_valid_string = self.__parse_posture_raw_string(posture_raw_string)
        self.service.goToPosture(posture_valid_string, 1.0)

    def stand_init(self):
        self.move_to("StandInit")

    def sit_relax(self):
        self.move_to("SitRelax")

    def stand_zero(self):
        self.move_to("StandZero")

    def lying_belly(self):
        self.move_to("LyingBelly")

    def lying_back(self):
        self.move_to("LyingBack")

    def stand(self):
        self.move_to("Stand")

    def crouch(self):
        self.move_to("Crouch")

    def sit(self):
        self.move_to("Sit")

    def demo_loop(self):
        self.stand_init()
        self.sit_relax()
        self.stand_zero()
        self.lying_belly()
        self.lying_back()
        self.stand()
        self.crouch()
        self.sit()
        self.stand_init()

    def __parse_posture_raw_string(self, posture_raw_string):
        return self.__raw_string_to_valid_string_dict[posture_raw_string.lower()]



def main(session, posture):
    postures_controller = PosturesController(session)
    postures_controller.move_to(posture)


if __name__ == "__main__":
    parser = ArgumentParser(formatter_class=RawTextHelpFormatter)
    parser.add_argument("--posture", type=str, default="standInit",
                        help="Robot goal posture. Default: StandInit\n" +
                             "Posible postures (case insensitive): \n" +
                             "StandInit \n" +
                             "SitRelax \n" +
                             "StandZero \n" +
                             "LyingBelly \n" +
                             "LyingBack \n" +
                             "Stand \n" +
                             "Crouch \n" +
                             "Sit \n"
                        )

    
    IP, PORT = NaoProperties().get_connection_properties()
    args = parser.parse_args()
    session = qi.Session()
    try:
        session.connect("tcp://" + IP + ":" + str(PORT))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + IP + "\" on port " + str(PORT) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    main(session, args.posture)
