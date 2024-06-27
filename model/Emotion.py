# coding=utf-8
"""
    Module handling robot external emotional reaction to an input.

    (C) 2022 Sophia Corvaia, University of Palermo, Palermo, Italy
    Released under GNU Public License (GPL)
    Contacts: sophia.corvaia@unipa.it
"""
from time import sleep
from owlready2 import Thing
from model.Knowledge import Knowledge
from model.InnerVoice import InnerVoice
from NaoQi.API import Core, address, robot
from typing import Tuple
from pandas import read_csv, DataFrame, concat
from numpy import array
from numpy.linalg import norm
from sys import float_info
import matplotlib.pyplot as plt
from matplotlib.patches import ConnectionPatch

# Constants
EMOTION_TYPE = {0: "Primary", 1: "Secondary"}


class Emotion:
    """Class handle external emotion reaction"""

    def __init__(self, onto: Knowledge, iv: InnerVoice = None):
        """Constructor method.

        :param onto: Ontology base knowledge
        :type onto: Knowledge
        :param iv: Inner Voice system handler
        :type iv: InnerVoice
        """
        self.onto = onto
        self.iv = iv
        self.tabletService = Core.ALTabletService()


        with self.onto.ontology:

            class anger(Thing):
                @classmethod
                def emotion_react(cls, parent):
                    sentence = parent.onto.get_comment(cls)
                    parent.show_image('anger', sentence)
                    return sentence

            class disgust(Thing):
                @classmethod
                def emotion_react(cls, parent):
                    sentence = parent.onto.get_comment(cls)
                    parent.show_image('disgust', sentence)
                    return sentence

            class happiness(Thing):
                @classmethod
                def emotion_react(cls, parent):
                    sentence = parent.onto.get_comment(cls)
                    parent.show_image('happiness', sentence)
                    return sentence

            class sadness(Thing):
                @classmethod
                def emotion_react(cls, parent):
                    sentence = parent.onto.get_comment(cls)
                    parent.show_image('sadness', sentence)
                    return sentence

            class neutral(Thing):
                @classmethod
                def emotion_react(cls, parent):
                    sentence = parent.onto.get_comment(cls)
                    parent.show_image('neutral', sentence)
                    return sentence

            class fear(Thing):
                @classmethod
                def emotion_react(cls, parent):
                    sentence = parent.onto.get_comment(cls)
                    parent.show_image('fear', sentence)
                    return sentence

    def emotion_react(self, individual: object) -> str:
        """Retrieve emotion react from a class emotion of the ontology.

        :param individual: emotion class to be analyzed
        :type individual: object
        :return: Sentenced produced by emotion reaction
        :rtype: str
        """
        return individual.emotion_react(self)

    def show_image(self, emotion: str, sentence: str = None) -> None:
        """Show local emotion image in Pepper tablet producing optional sentence.

        :param emotion: Emotion associated with image to be show
        :type emotion: str
        :param sentence: Sentence to be produce with image
        :type sentence: str
        """
        try:
            if robot != 'pepper':
                raise ValueError("Emotion.show_image(): cannot show image on NAO interface!")

            self.tabletService.showImage("http://{}/apps/aldebaran/{}_title.png".format(address, emotion))
            if sentence:
                self.iv.produce(sentence)
            sleep(1)
            self.tabletService.hideImage()
        except Exception as ex:
            print(ex)


class Appraisal:
    """Class for computation of the appraisal variables according to the Russell appraisal model.
    5 Ekman primary emotions has been considered for this evaluation: Anger, Sadness, Fear, Happiness and Disgust.
    According to configurations of the appraisal values (called appraisal patterns), an emotion rises with a
    specific intensity.
    """

    def __init__(self):
        """Constructor method."""
        try:
            self.__dataset = read_csv('../resources/data/russell_ekman_emotions.csv')
            self.__dataset = self.__dataset.set_index('Emotion')
            self.__emotions = list(self.__dataset.index.values)
            self.__data = self.__dataset.loc[self.__emotions]
            self.__emotion = self.__intensity = self.__valence = self.__arousal = None
        except Exception as e:
            raise Exception("Exception __init__: {}".format(e), self.__class__.__name__)

    @property
    def emotion(self) -> str:
        """Get evaluated emotion"""
        return self.__emotion

    @property
    def intensity(self) -> str:
        """Get emotion's intensity"""
        return self.__intensity

    @property
    def valence(self) -> float:
        """Get appraisal variable valence"""
        return self.__valence

    @property
    def arousal(self) -> float:
        """Get appraisal variable arousal"""
        return self.__arousal

    def __get_thresholds(self, emotion: str) -> Tuple[float, float]:
        """
        Calculate the maximum threshold and the minimum threshold within which to limit the intensity of the emotion.
        :param emotion: selected emotion
        :type emotion: basestring
        :return: low and high threshold for the selected emotion
        :rtype: tuple
        :raise ValueError: if emotion parameter is not string or is not a recognizable emotion
        """
        if type(emotion) is not str:
            raise ValueError("Emotion label required as a string! {} received!".format(type(emotion)))
        elif emotion not in self.__emotions:
            raise ValueError("{} emotion not recognized!".format(emotion))

        emo_point = self.__data.loc[emotion].to_numpy()
        low_threshold = (norm(emo_point - array([0.0, 0.0]))) / 2
        high_threshold = low_threshold / 2

        return low_threshold, high_threshold

    def evaluate(self):
        """
        Evaluate input belief and raise emotion and its intensity with euclidean distance.
        :return: the emotion evaluated, and it's intensity
        :rtype: tuple
        :raise ValueError: input belief is not a valid belief (wrong appraisal pattern)
        """
        if not self.__valence or not self.__arousal:
            raise ValueError("Can't evaluate emotion! Need valence and arousal value to be computed!")
        min_dist = float_info.max

        for index, row in self.__data.iterrows():
            # Distance from belief and current emotion point
            curr = norm(row.to_numpy() - array([self.__valence, self.__arousal]))
            if curr < min_dist:
                min_dist = curr
                self.__emotion = index
                self.__intensity = min_dist

    def eval_valence(self, external_input: list):
        """Evaluate Valence variable based on external input"""
        self.__valence = -0.65

    def eval_arousal(self, internal_input: list):
        """Evaluate Arousal variable based on physical reaction"""
        self.__arousal = -0.23

    def plot_emotion(self):
        """Displays the emotions and belief plot in two dimensions on the screen.
        Draws an arrow between belief and emotion.
        :raise Exception: if there is no evaluated emotion
        """
        if not self.__valence or not self.__arousal:
            raise ValueError("Can't plot emotion! Need valence and arousal value to be computed!")

        belief = [self.__valence, self.__arousal]
        belief_df = DataFrame([belief], columns=self.__dataset.columns, index=['Emotion'])
        new_data = concat([self.__dataset, belief_df])
        self.__emotions.append('Emotion')
        if not self.__emotion:
            raise ValueError("Can't plot emotion! Evaluate one first!")

        colors = ['red', 'dodgerblue', 'blueviolet', 'gold', 'limegreen', 'black']

        plt.figure('Emotions and Belief', figsize=[8, 8])
        plt.xlim([-1.5, 1.5])
        plt.ylim([-1.5, 1.5])
        plt.xlabel('Valence')
        plt.ylabel('Arousal')
        plt.axhline(0, color='black')
        plt.axvline(0, color='black')

        circle = plt.Circle((0, 0), radius=1, edgecolor='black', fill=False, linestyle='--')
        for label, i in zip(self.__emotions, range(0, len(new_data))):
            x_data = new_data.loc[label]['Valence']
            y_data = new_data.loc[label]['Arousal']
            plt.scatter(x_data, y_data, marker='o', color=colors[i])
            plt.text(x_data + .03, y_data + .03, label, fontsize=9)

        if self.__emotion and belief is not None:
            low_threshold, high_threshold = self.__get_thresholds(self.__emotion)
            x_center = new_data.loc[self.__emotion]['Valence']
            y_center = new_data.loc[self.__emotion]['Arousal']
            x_belief = new_data.loc['Emotion']['Valence']
            y_belief = new_data.loc['Emotion']['Arousal']
            circle_low = plt.Circle((x_center, y_center), radius=low_threshold, edgecolor='forestgreen', fill=False)
            circle_high = plt.Circle((x_center, y_center), radius=high_threshold, edgecolor='red', fill=False)
            plt.legend([circle_high, circle_low], ['High Intensity', 'Medium Intensity'])
            arrow = ConnectionPatch((x_belief, y_belief),
                                    (x_center, y_center), 'data', 'data', arrowstyle="->", shrinkA=5, shrinkB=5,
                                    mutation_scale=20, fc="w")
            plt.gcf().gca().add_artist(arrow)
            plt.gca().add_patch(circle_low)
            plt.gca().add_patch(circle_high)
        plt.gca().add_patch(circle)
        plt.grid()
        plt.show()


