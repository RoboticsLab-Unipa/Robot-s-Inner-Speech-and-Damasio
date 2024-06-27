# coding=utf-8
"""
    Module handling base knowledge information.

    (C) 2022 Sophia Corvaia, University of Palermo, Palermo, Italy
    Released under GNU Public License (GPL)
    Contacts: sophia.corvaia@unipa.it
"""
from typing import Union, Optional
from owlready2 import get_ontology
from pathlib import Path
from rdflib import Graph
from utils.Config import ConfigHandle
from random import choice


class Knowledge:
    """Class for manage base ontology"""

    def __init__(self, onto_file: str = None, language: str = 'en') -> None:
        """Constructor method.

        :param onto_file: filename of base knowledge
        :type onto_file: str
        """
        self._ontology = None
        try:
            if onto_file is None:
                self._owl_file = ConfigHandle().get_default_knowledge()
            else:
                file_extension = Path(onto_file).suffix
                if file_extension != '.owl':
                    raise TypeError("Required .owl file! Received {} instead!".format(file_extension))
                self._owl_file = onto_file
            self._ontology = get_ontology(self._owl_file).load(reload_if_newer=True)
            self._graph = Graph().parse(self._owl_file)
            self._namespace = self._ontology.get_base_iri()
            self._language = language
        except Exception as e:
            raise Exception("Exception __init__: {}".format(e), self.__class__.__name__)

    @property
    def ontology(self):
        """Get base ontology"""
        return self._ontology

    @property
    def namespace(self):
        """Get ontology's namespace"""
        return self._namespace

    def get_class_by_name(self, name: str, parent: str = None) -> Optional[object]:
        """Get class object by name

        :param name: Class name
        :type name: str
        :param parent: Parent's class to be search
        :type parent: str
        :return: Class object
        :rtype: object
        """
        onto_classes = list(self._ontology.classes())
        if parent:
            subclasses = None
            for onto_class in onto_classes:
                if onto_class.name == parent:
                    subclasses = onto_class.descendants()
                    break
            for subclass in subclasses:
                if subclass.name == name:
                    return subclass
        else:
            for onto_class in onto_classes:
                if onto_class.name == name:
                    return onto_class
        return None

    def get_property_by_name(self, name: str) -> Optional[object]:
        """Get property object by name

        :param name: Class name
        :type name: str
        :return: Class object
        :rtype: object
        """
        onto_properties = list(self._ontology.properties())
        for onto_property in onto_properties:
            if onto_property.name == name:
                return onto_property
        return None

    @staticmethod
    def get_activation_as_list(thing: object) -> Optional[list]:
        """Get activation level associated with an object thing in the ontology as list

        :param thing: Class in ontology
        :type thing: object
        :return: Activation level
        :rtype: list
        """
        activation = thing.hasActivation
        if not activation:
            return None
        return [activation.min_inclusive, activation.max_inclusive]

    def get_comment(self, thing: object) -> str:
        """Get annotation comment in a class object

        :param thing: Class in ontology
        :type thing: object
        :return: Class' annotation comment
        :rtype: str
        """
        if self._language == 'it':
            return choice(thing.comment.it) if len(thing.comment.it) > 0 else ''
        return choice(thing.comment) if len(thing.comment) > 0 else ''

    def get_label(self, thing: object) -> str:
        """Get annotation label in a class object

        :param thing: Class in ontology
        :type thing: object
        :return: Class' annotation label
        :rtype: str
        """
        if self._language == 'it':
            return choice(thing.label.it) if len(thing.label.it) > 0 else ''
        return choice(thing.label) if len(thing.label) > 0 else ''

    def get_inner_act(self, act: str) -> str:
        """Get sentence associated with Inner Act.

        :param act: Name class of Inner Act
        :type act: str
        :return: Sentence
        :rtype: str
        """
        inner_acts = self._ontology.InnerAct.subclasses()
        for inner_act in inner_acts:
            if inner_act.name == act:
                return self.get_comment(self.get_class_by_name(act))

    def get_input_classes(self, name: bool = False) -> list:
        """Get all the input classes, both external and internal, in base ontology.

        :param name: If the returned list must contain also classes' names
        :type name: bool
        :return: List of subclasses
        :rtype: list
        """
        if name:
            return [subclass.name for subclass in self._ontology.External_Input.descendants()
                    | self._ontology.Internal_Input.descendants()]
        return list(self._ontology.Input.descendants() | self._ontology.Internal_Input.descendants())

    def get_volume_classes(self) -> list:
        """Get all the volume classes in base ontology"""
        return list(self._ontology.Volume.subclasses())

    def get_rhythm_classes(self) -> list:
        """Get all the rhythm classes in base ontology"""
        return list(self._ontology.Rhythm.subclasses())

    def get_instrument_classes(self, name: bool = False) -> list:
        """Get all the instrument classes in base ontology.

        :param name: If the returned list must contain also classes' names
        :type name: bool
        :return: List of subclasses
        :rtype: list
        """
        if name:
            return [subclass.name for subclass in self._ontology.Instrument.subclasses()]
        return list(self._ontology.Intrument.subclasses())

    def get_pitch_classes(self, name: bool = False) -> list:
        """Get all the pitch classes in base ontology.

        :param name: If the returned list must contain also classes' names
        :type name: bool
        :return: List of subclasses
        :rtype: list
        """
        if name:
            return [subclass.name for subclass in self._ontology.Pitch.subclasses()]
        return list(self._ontology.Pitch.subclasses())

    def get_body_classes(self, name: bool = False) -> list:
        """Get all the body classes in base ontology.

        :param name: If the returned list must contain also classes' names
        :type name: bool
        :return: List of subclasses
        :rtype: list
        """
        if name:
            return [subclass.name for subclass in self._ontology.Body.subclasses()]
        return list(self._ontology.Body.subclasses())

    @staticmethod
    def infer_class(individual: object) -> Union[list, object]:
        """ Infer type class of an individual from base ontology.

        :param individual: Individual to be analyzed
        :type individual: object
        """
        if not individual.hasOwnProperty:
            return individual.is_a[0]
        return individual

    def get_own_properties(self, individual: object) -> list:
        """Retrieve all properties associated to input instance.

        :param individual: Individual that generate actions
        :type individual: object
        :return: A list of all properties
        :rtype: list
        """
        ancestors = list(individual.is_a[0].ancestors())
        if len(ancestors) == 1:  # Ancestors with 1 element could be only Thing class. No prop
            return []
        properties = individual.hasOwnProperty  # Properties for current individual
        if not properties:  # If there is no properties for current individual
            return self.get_own_properties(individual.is_a[0])
        return properties

    def validate(self, name: str, value: Union[list, int, str]) -> bool:
        """Validates the correctness of an individual with respect to ontology.

        :param name: Individual's name to be validated
        :type name: str
        :param value: Individual's input value
        :type value: list, int, str
        :return: Validator result
        :rtype: bool
        """
        pass
        input_class = self.get_class_by_name(name)
        ind_prop = {}
        for prop in list(input_class.get_class_properties()):
            ind_prop[prop.name] = []
            for value in prop[input_class]:
                ind_prop[prop.name].append(value.name)

        return True

