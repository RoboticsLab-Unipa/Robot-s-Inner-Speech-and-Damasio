# coding=utf-8
"""
    Module handling actions performed by robot.

    (C) 2022 Sophia Corvaia, University of Palermo, Palermo, Italy
    Released under GNU Public License (GPL)
    Contacts: sophia.corvaia@unipa.it
"""
from owlready2 import Thing
from random import randint, choice

from model.Knowledge import Knowledge


class Action:
    """Class handle action's performed by robot"""

    def __init__(self, onto: Knowledge):
        """Constructor method.

        :param onto: Ontology base knowledge
        :type onto: Knowledge
        """
        self.onto = onto

        with self.onto.ontology:  # Define actions method for every action class in ontology

            class VolumeDown(Thing):
                @classmethod
                def do_action(cls, parent, name):
                    return 'Volume', - randint(10, 30)

            class VolumeUp(Thing):
                @classmethod
                def do_action(cls, parent, name):
                    return 'Volume', randint(10, 30)

            class Breath(Thing):
                @classmethod
                def do_action(cls, parent, name):
                    return 'Chest', - randint(5, 10)

            class Close(Thing):
                @classmethod
                def do_action(cls, parent, name):
                    return 'Head', - randint(5, 10)

            class Release(Thing):
                @classmethod
                def do_action(cls, parent, name):
                    return 'Hands', - randint(5, 10)

            class RhythmUp(Thing):
                @classmethod
                def do_action(cls, parent, name):
                    return 'Rhythm', randint(20, 50)

            class RhythmDown(Thing):
                @classmethod
                def do_action(cls, parent, name):
                    return 'Rhythm', - randint(20, 50)

            class ChangePitch(Thing):
                @classmethod
                def do_action(cls, parent, name):
                    if name:
                        class_list = list(parent.onto.get_pitch_classes(name=True))
                        class_list.remove(name)
                        return 'Pitch', choice(class_list)
                    return 'Pitch', choice(parent.onto.get_pitch_classes(name=True))

            class ChangeInstrument(Thing):
                @classmethod
                def do_action(cls, parent, name):
                    if name:
                        class_list = list(parent.onto.get_instrument_classes(name=True))
                        class_list.remove(name)
                        return 'Instrument', choice(class_list)
                    return 'Instrument', choice(parent.onto.get_instrument_classes(name=True))

    def do_action(self, individual: object, name: str = None):
        """Retrieve action from a class of the ontology.

        :param individual: class to be analyzed
        :type individual: object
        :param name: Parameter name used to ignore class itself in the action selection
        :type name: str
        """
        return individual.do_action(self, name)
