# coding=utf-8
"""
    Module handling robot's Inner Speech based on knowledge.

    (C) 2022 Sophia Corvaia, University of Palermo, Palermo, Italy
    Released under GNU Public License (GPL)
    Contacts: sophia.corvaia@unipa.it
"""
from utils.Logger import Logger
from model.Knowledge import Knowledge


class InnerVoice:
    """Class handle Robot's Inner Speech"""

    def __init__(self, onto: Knowledge, configuration: dict = None, robot: bool = False,
                 speak: bool = False, log: Logger = None, lang: str = 'en'):
        """Constructor method.

        :param onto: Ontology base knowledge
        :type onto: Knowledge
        :param configuration: Gesture configuration in external animated speech
        :type configuration: dict
        :param robot: If robot interface is enabled
        :type robot: bool
        :param speak: If robot speak loudly
        :type speak: bool
        """
        self.onto = onto
        self.robot = robot
        self.speak = speak
        self.configuration = configuration
        self.log = log
        self.gr = Grammar(lang=lang)
        if robot:  # Initialize Pepper API for interaction
            from NaoQi.API import Audio, SensorsLed, Motion
            self.tts = Audio.ALTextToSpeech()
            self.tts.setLanguage(self.tts.LANGUAGE)
            self.tts.setParameter("speed", 90.0)
            self.led = SensorsLed.ALLeds()
            self.ats = Audio.ALAnimatedSpeech()
            self.ps = Motion.ALRobotPosture()
            self.speak = speak

    @property
    def get_speak(self):
        return self.speak

    def think(self, body: str, reactions: list = None, causes: list = None) -> str:
        """Generate thought sentence based on sentence comments in ontology
        associated with causes or reactions.

        :param body: Body part to be analyzed
        :type body: str
        :param reactions: List of reactions to be analyzed
        :type reactions: list
        :param causes: List of causes to be analyzed
        :type causes: list
        :return: Custom sentence
        :rtype: str
        """
        body_class = self.onto.get_class_by_name(body)
        sentence = self.onto.get_comment(body_class)

        if reactions:
            sentence = self.gr.grammar_reaction(sentence)
            for reaction in reactions:
                sentence = sentence + self.onto.get_comment(reaction) + ", "
        if causes:
            sentence = self.gr.grammar_causes(sentence)
            for cause in causes:
                sentence = sentence + self.onto.get_comment(self.onto.infer_class(cause)) + ", "
        sentence = sentence + "."
        return sentence

    def produce(self, sentence: str, configuration: dict = None):
        """Produce sentence to be spoken or thought by robot.

        :param sentence: Sentence to be produced
        :type sentence: str
        :param configuration: Gesture configuration in external animated speech
        :type configuration: dict
        """
        if self.speak:
            self.__produce_outer(sentence, configuration)
        else:
            self.__produce_inner(sentence)
            if self.robot:
                self.__set_outer()  # Return to outer configuration

    def __produce_inner(self, sentence: str):
        """Produce inner voice from robot.

        :param sentence: Sentence to reproduce
        :type sentence: str
        """
        if not self.robot:
            if self.log:
                self.log.warning("InnerVoice.produce_inner(): Cannot use produce_inner. Robot Interface not found!")
            else:
                print(Exception("InnerVoice.produce_inner(): Cannot use produce_inner. Robot Interface not found!"))
            return
        self.tts.setParameter("speed", 80.0)
        self.tts.setParameter("pitchShift", 1.0)
        self.tts.setParameter("doubleVoice", 1.2)
        self.tts.setParameter("doubleVoiceLevel", 1.0)
        self.tts.setParameter("doubleVoiceTimeShift", 0.1)
        self.led.randomEyes(0.3)
        self.led.setIntensity("ChestLedsRed", 0.0)
        self.tts.say(sentence)
        self.led.off("FaceLeds")
        self.led.on("FaceLeds")
        self.led.off("ChestLeds")
        self.led.on("ChestLeds")
        self.ps.goToPosture("Stand", 1.0)

    def __set_outer(self):
        """Setting parameter for robot real voice"""
        self.tts.setParameter("speed", 90.0)
        self.tts.setParameter("pitchShift", self.tts.STANDARD_PITCH)
        self.tts.setParameter("doubleVoice", self.tts.STANDARD_DVOICE)
        self.tts.setParameter("doubleVoiceLevel", self.tts.STANDARD_DVOICE_LEVEL)
        self.tts.setParameter("doubleVoiceTimeShift", self.tts.STANDARD_DVOICE_TS)

    def __produce_outer(self, sentence: str, configuration: dict = None):
        """Produce outer voice from robot in default anime configuration.

        :param sentence: Sentence to reproduce
        :type sentence: str
        :param configuration: Voice configuration
        :type configuration: dict
        """
        if not self.robot:
            if self.log:
                self.log.warning("InnerVoice.produce_outer(): Cannot use produce_inner. Robot Interface not found!")
            else:
                print(Exception("InnerVoice.produce_outer(): Cannot use produce_inner. Robot Interface not found!"))
            return
        self.__set_outer()
        if not configuration:
            self.ats.say(sentence, self.configuration)
        else:
            self.ats.say(sentence, configuration)
        self.ps.goToPosture("Stand", 1.0)


class Grammar:
    """Handle grammar in Inner Speech process."""

    def __init__(self, lang: str):
        self._lang = lang

    def grammar_reaction(self, sentence: str):
        if self._lang == 'it':
            return f"Sto reagendo in questo modo probabilmente perchè "
        else:
            return f"{sentence} probably because of "

    def grammar_causes(self, sentence: str):
        if self._lang == 'it':
            return f"{sentence} perchè "
        else:
            return f"{sentence} caused by "
