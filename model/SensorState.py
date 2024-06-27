# coding=utf-8
"""
    Handle Sensor State of Damasio's idea in Model's simulation.

    (C) 2022 Sophia Corvaia, University of Palermo, Palermo, Italy
    Released under GNU Public License (GPL)
    Contacts: sophia.corvaia@unipa.it
"""
from typing import Union

from rdflib import URIRef, Literal
from owlready2 import get_ontology, destroy_entity
from model.Knowledge import Knowledge
from utils.Config import ConfigHandle
from pathlib import Path


class SensorState:
    """Class handle sensor state of Damasio's model.
    It represents the sensory block of the agent when inputs are coded in data structures"""

    def __init__(self, onto: Knowledge, individual_file: str = None) -> None:
        """Constructor method.

        :param onto: Ontology base knowledge
        :type onto: Knowledge
        :param individual_file: Individual knowledge filename
        :type individual_file: str
        """
        self._onto_individuals = None
        try:
            if individual_file is None:
                self._onto_ind = ConfigHandle().get_default_individual()
                self.erase_ontology()
            else:
                self._onto_ind = individual_file
                file_extension = Path(individual_file).suffix
                if file_extension != '.owl':
                    raise TypeError("Required .owl file! Received {} instead!".format(file_extension))
            self._onto = onto
            self._ontology = onto.ontology
            self._graph = self._ontology.world.as_rdflib_graph()
            self._graph.bind('onto', self._onto.namespace)
            self._ind_namespace = self._onto_ind + "#"
        except Exception as e:
            raise Exception("Exception __init__: {}".format(e), self.__class__.__name__)

    def erase_ontology(self):
        """Erase old content of individual ontology."""
        if self._onto_individuals:  # Destroy old individuals
            for individual in list(self._onto_individuals.individuals()):
                destroy_entity(individual)
            self._onto_individuals.save(self._onto_ind)
            self._onto_individuals = None
        with open(self._onto_ind, 'w') as f:  # Clear individual file .owl
            f.write('')
            f.close()


    def create_instance(self, data: dict) -> list:
        """Create new generic instance and add it to individual ontology.

        :param data: Attribute of the instance
        :type data: dict
        :return: List of created individual
        :rtype: list
        """
        if type(data) is not dict:
            raise TypeError("Type data parameter incorrect! Required dict, received {} instead!"
                            .format(type(data)))

        try:
            self.erase_ontology()

            # Load base and individual ontology and merge them
            onto_individuals = get_ontology(self._onto_ind).load(reload=True)
            onto_individuals.imported_ontologies.append(self._ontology)
            individuals = []

            with onto_individuals:
                fields = data.keys()
                for field in fields:  # For each field in input data
                    # Look for type class input (if internal or external)
                    external_input = self._onto.get_class_by_name(field, parent='External_Input')
                    input_class = external_input if external_input else \
                        self._onto.get_class_by_name(field, parent='Internal_Input')

                    individual = input_class(name=field)

                    if input_class:
                        max_value = input_class.hasMaximum
                        min_value = input_class.hasMinimum
                        if max_value:
                            if data[field] > max_value:
                                data[field] = max_value

                        if min_value:
                            if data[field] < min_value:
                                data[field] = min_value

                        own_data_properties = self._onto.get_own_properties(input_class)

                        if own_data_properties:
                            individual = input_class(name=field)  # Class with specific property
                            # Create raw node associated with URI Reference of class' field object
                            field_node = URIRef(self._ind_namespace + field)
                            # Create raw node associated with URI Reference of class' property own_data_properties
                            for own_prop in own_data_properties:
                                data_property = URIRef(self._onto.namespace + own_prop)
                                if type(data[field]) == dict:  # Multiple properties to manage
                                    keys = data[field].keys()
                                    for key in keys:  # Check the keys of subdict
                                        if key in own_prop.lower():
                                            values = data[field][key]
                                            if type(values) == list:  # Multiple values for current key
                                                for value in values:
                                                    # Add property node to field node class as child
                                                    self._graph.add((field_node, data_property, Literal(value)))
                                            else:
                                                # Add property node to field node class as child
                                                self._graph.add((field_node, data_property, Literal(data[field][key])))
                                            break
                                else:  # Single property
                                    # Add property node to field node class as child
                                    self._graph.add((field_node, data_property, Literal(data[field])))
                        else:
                            input_class = self._onto.get_class_by_name(field)
                            if type(data[field]) == list:  # Multiple data values to manage
                                temp_individual = []
                                for value in data[field]:
                                    temp_individual.append(input_class(name=value))
                                individual = temp_individual
                            else:
                                individual = input_class(name=data[field])  # Generic Class
                    else:
                        raise ValueError('{} field name is not valid!!'.format(field))
                    if type(individual) == list:
                        individuals += individual
                    else:
                        individuals.append(individual)
            onto_individuals.save(self._onto_ind)
            self._onto_individuals = onto_individuals
            return individuals
        except Exception as e:
            raise Exception("Exception create_instance: {}".format(e), self.__class__.__name__)

    def infer_instance(self, instances: list) -> list:
        """Infer input instances in the ontology

        :param instances: Instances input in the ontology
        :type instances: list
        :return: List of classes with inferred instances
        :rtype: list
        """
        if type(instances) is not list:
            raise TypeError("Type instances parameter incorrect! Required list, received {} instead!"
                            .format(type(instances)))

        inferred = [self._onto.infer_class(instance) for instance in instances]
        return inferred

    def change_input(self, parameter: str, new_value: int or str, old_value: int or str) -> Union[int, str]:
        """Check and change input parameter value from data input dictionary

        :param parameter: Parameter's name to be checked
        :type parameter: str
        :param new_value: Value to be added to input
        :type new_value: int or str
        :param old_value: Value to be replaced in the input
        :type old_value: int or str
        :return: Changed input data
        :rtype: dict
        """
        if type(parameter) is not str:
            raise TypeError("Type parameter incorrect! Required str, received {} instead!"
                            .format(type(parameter)))
        if type(old_value) is not type(new_value):
            raise TypeError("Two types of value must be the same! Received {} and {} instead!"
                            .format(type(old_value), type(new_value)))

        external_input = self._onto.get_class_by_name(parameter, parent='External_Input')
        input_class = external_input if external_input else \
            self._onto.get_class_by_name(parameter, parent='Internal_Input')
        if type(old_value) == str:  # Changing value
            return new_value
        else:  # Update value
            max_value = input_class.hasMaximum
            min_value = input_class.hasMinimum
            temp_value = old_value + new_value
            if max_value:
                if temp_value > max_value:
                    return max_value
            if min_value:
                if temp_value < min_value:
                    return min_value
        return temp_value
