# coding=utf-8
"""
    Handle Sensory Representation of Damasio's idea in Model's simulation.

    (C) 2022 Sophia Corvaia, University of Palermo, Palermo, Italy
    Released under GNU Public License (GPL)
    Contacts: sophia.corvaia@unipa.it
"""
from sys import float_info

from owlready2 import get_ontology, sync_reasoner_pellet, sync_reasoner_hermit
from pathlib import Path
from pandas import read_csv

from numpy import mean
from ast import literal_eval
from utils.Config import ConfigHandle

from model.Knowledge import Knowledge


class SensoryRepresentation:
    """Class handle base knowledge of an agent, giving a subjective representation of an input"""
    NORMAL_ACTIVATION = [0, 5]
    MAX_ACTIVATION = 15
    MIN_ACTIVATION = -15

    def __init__(self, onto: Knowledge, individual_file: str = None, hermit: bool = True) -> None:
        """Constructor method

        :param onto: Ontology base knowledge
        :type onto: Knowledge
        :param individual_file: Individual knowledge filename
        :type individual_file: str
        :param hermit: select Hermit or Pellet reasoner
        :type hermit: bool
        :raises TypeError: if file has not .owl extension
        :raises Exception
        """
        self._hermit = hermit
        self._world = None
        self._ind_world = None
        try:
            if individual_file is None:
                self._onto_ind = ConfigHandle().get_default_individual()
            else:
                self._onto_ind = individual_file
                file_extension = Path(individual_file).suffix
                if file_extension != '.owl':
                    raise TypeError("Required .owl file! Received {} instead!".format(file_extension))
            self._onto = onto
            self._ontology = onto.ontology
            self._ind_world = get_ontology(self._onto_ind).load(reload_if_newer=True)
            self._ontology.imported_ontologies.append(self._ind_world)
            # Embody data for emotion evaluation
            self._embody_data = read_csv('./S.U.S.A.N./resources/data/emBody_value.csv')
            self._embody_data.set_index('Emotions', inplace=True)
        except FileNotFoundError as not_found:
            raise FileNotFoundError("Exception __init__: {}. Missing CSV File: Cannot extract embody data. Run "
                                    "emo_body.py first!".format(not_found), self.__class__.__name__)
        except Exception as e:
            raise Exception("Exception __init__: {}".format(e), self.__class__.__name__)

    def synchronize(self, debug: int = 1) -> None:
        """Synchronize knowledge reasoner.

        :param debug: Level of debugging to check inconsistency in ontology
        :type debug: int
        """
        try:
            sync_reasoner_hermit(self._world) if self._hermit else sync_reasoner_pellet(self._world, debug=debug)
        except Exception as e:
            raise Exception("Exception synchronize: {}".format(e), self.__class__.__name__)

    def get_reactions(self, individual: object) -> list:
        """Retrieve all reactions associated to input instance.

        :param individual: Individual that generate reactions
        :type individual: object
        :return: A list of all reactions
        :rtype: list
        """
        return self._onto.infer_class(individual).hasReaction

    def get_actions(self, individual: object) -> list:
        """Retrieve all actions associated to input instance.

        :param individual: Individual that generate actions
        :type individual: object
        :return: A list of all actions
        :rtype: list
        """
        ancestors = list(individual.is_a[0].ancestors())
        if len(ancestors) == 2:  # Ancestors with 2 elements could be only Thing class and the class itself. No actions
            return []
        actions = individual.is_a[0].hasAction  # Action available for current individual
        if not actions:  # If there is no action for current individual
            return self.get_actions(individual.is_a[0])
        return actions

    def evaluate_reaction(self, reactions: list) -> dict:
        """Evaluate bodily medium reaction level produced by a list of reactions.

        :param reactions: List of all reactions produced by input
        :type reactions: list
        :return: Bodily reactions
        :rtype: dict
        """
        if type(reactions) is not list:
            raise TypeError("Type reactions parameter incorrect! Required list. "
                            "Received {} instead!".format(type(reactions)))

        body = self._onto.get_body_classes(name=True)
        body_reactions = {emp_list: [[], []] for emp_list in body}

        for reaction in reactions:
            body_part = reaction.is_a[0].hasBodyPart[0].name
            body_reactions[body_part][0].append(reaction.hasActivation.min_inclusive)
            body_reactions[body_part][1].append(reaction.hasActivation.max_inclusive)

        for body_part in body_reactions:
            if not body_reactions[body_part][0]:
                body_reactions[body_part] = self.NORMAL_ACTIVATION
            else:
                body_reactions[body_part][0] = round(mean(body_reactions[body_part][0]))
                body_reactions[body_part][1] = round(mean(body_reactions[body_part][1]))

        return body_reactions

    def sort_body_reactions(self, body_reactions: dict, ascending: bool = False) -> dict:
        """Sort body reactions by sum of its interval.

        :param body_reactions: list of intervals to be sorted
        :type body_reactions: dict
        :param ascending: if ascending sort is set
        :type ascending: bool
        :return: Sorted dict
        :rtype: dict
        """
        if not body_reactions:
            raise ValueError("Cannot sort a missing dictionary!")
        sort_list = [abs(sum(interval)) for interval in body_reactions.values()]
        sort_list.sort(reverse=not ascending)

        sorted_dict = {}
        dict_keys = list(body_reactions.keys())
        for value in sort_list:
            for key in dict_keys:
                if body_reactions[key] == self.NORMAL_ACTIVATION:  # Ignore body part with normal activation range
                    continue
                if abs(sum(body_reactions[key])) == value:
                    sorted_dict[key] = body_reactions[key]
                    dict_keys.remove(key)
        return sorted_dict

    def evaluate_emotion(self, reactions: dict) -> dict:
        """ Evaluate the closest emotion to the bodily reaction.

        :param reactions: Input's reaction
        :type reactions: dict
        :return: Closest emotion's label and value
        :rtype: dict
        """
        if type(reactions) is not dict:
            raise TypeError("Type reactions parameter incorrect! Required dict. "
                            "Received {} instead!".format(type(reactions)))
        emotion = None
        data_list = None
        intensity = None
        min_dist = float_info.max
        data = sum(list(reactions.values()), [])

        for label in self._embody_data.index:
            emo_data = self._embody_data.loc[label]
            emo_data = [literal_eval(col) for col in emo_data]
            emo_data = sum(emo_data, [])
            curr = 0
            for elem_data, elem_emo in zip(data, emo_data):
                curr += abs(elem_data - elem_emo)
            if curr < min_dist:
                min_dist = curr
                emotion = label
                data_list = emo_data
        intensity = self.evaluate_intensity(min_dist)

        return {'Selected': emotion, 'Data': data_list, 'Intensity': intensity}

    @staticmethod
    def evaluate_intensity(intensity: int) -> str:
        """
        Evaluate level of emotion intensity based on range of values
        :param intensity: Intensity to be evaluated
        :return: String label for intensity (Low, Medium, High)
        """
        far_emotion = 15 * 12  # TWELVE times the maximum activation level for emotion reaction in body
        level = 'Low'
        if intensity < far_emotion // 4:
            level = 'High'
        elif intensity < far_emotion // 2:
            level = 'Medium'
        return level

    def retrieve_reaction(self, body_part: str, activation: list) -> list:
        """Retrieve closer reaction that generate body part activation level

        :param body_part: Body part of the robot
        :type body_part: str
        :param activation: Interval activation computed for body part input
        :type activation: list
        :return: List of the closest reaction to activation level
        :rtype: list
        """
        body_class = self._onto.get_class_by_name(body_part)
        reactions = body_class.isBodyPartOf  # Get all reaction associated with body part
        closer_reaction = None
        min_dist = float_info.max

        for reaction in reactions:
            subclasses = reaction.subclasses()
            for subclass in subclasses:
                activation_list = self._onto.get_activation_as_list(subclass)
                curr = 0
                if activation_list:
                    for item_1, item_2 in zip(activation_list, activation):
                        curr += abs(item_1 - item_2)
                    if curr < min_dist:
                        min_dist = curr
                        closer_reaction = subclass
        return [closer_reaction]

    def retrieve_causes(self, inputs: list, reaction: list) -> list:
        """Retrieve causes that generate that reaction

        :param inputs: Inputs data to be analyzed
        :type inputs: list
        :param reaction: Reaction to be analyzed
        :type reaction: list
        :return: List of the closest causes to reaction
        """
        causes = []

        for individual in inputs:
            input_reactions = self.get_reactions(individual)
            if any(item in input_reactions for item in reaction):  # Find direct input cause
                causes.append(individual)

        if not causes:  # Didn't find any direct input link. Check input that generate a similar reaction
            activation = self._onto.get_activation_as_list(reaction[0])
            min_dist = float_info.max
            curr = 0
            for individual in inputs:
                for element in self.get_reactions(individual):
                    curr_activation = self._onto.get_activation_as_list(element)
                    for item_1, item_2 in zip(curr_activation, activation):
                        curr += abs(item_1 - item_2)
                    if curr < min_dist:
                        min_dist = curr
                        causes = [individual]
        return causes

    @staticmethod
    def get_parameters_not_ignored(ignore_parameters: list, r_causes: list) -> list:
        """Get causes to be not ignored in the process.

        :param ignore_parameters: List of ignored parameters
        :type ignore_parameters: list
        :param r_causes: Causes to be analyzed
        :type r_causes: list
        :return: List of object to be considered
        :rtype: list
        """
        if not ignore_parameters:
            return r_causes
        names_r_causes = list(set([cause.name for cause in r_causes]) - set(ignore_parameters))
        return [r_cause for r_cause in r_causes if r_cause.name in names_r_causes]

    @staticmethod
    def get_body_not_ignored(ignore_body: list, r_reactions: list) -> list:
        """Get body part to be not ignored in the process.

        :param ignore_body: List of ignored parameters
        :type ignore_body: list
        :param r_reactions: Reaction to be analyzed
        :type r_reactions: list
        :return: List of object to be considered
        :rtype: list
        """
        if not ignore_body:
            return r_reactions
        return list(filter(lambda x: x not in set(ignore_body), r_reactions))

    def change_body(self, activations: list, value: int) -> list:
        """Check and change activation parameter value from body part

        :param activations: List of activations to be checked
        :type activations: list
        :param value: Value to be added to activations
        :type value: int
        :return: Changed activations (eventually empty)
        """
        if type(activations) is not list:
            raise TypeError("Type activation parameter incorrect! Required list, received {} instead!"
                            .format(type(activations)))
        if type(value) is not int:
            raise TypeError("Type value parameter incorrect! Required int, received {} instead!"
                            .format(type(value)))

        min_value = activations[0]  # Min value of activation is on the first item of list
        max_value = activations[0]  # Max value of activation is on the second item of list

        if min_value + value < self.MIN_ACTIVATION or max_value + value > self.MAX_ACTIVATION:
            return []
        return [activation + value for activation in activations]
