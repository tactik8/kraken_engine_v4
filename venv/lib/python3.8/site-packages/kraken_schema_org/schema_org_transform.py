



def transform_class(properties):

    class_db = {}

    # Initialize db records
    for i in properties.keys():

        if properties[i].get('@type', None) == 'rdfs:Class':
            class_db[i] = properties[i]

    return class_db


def transform_class_normalized(properties):

    normalized_class_db = {}

    # Initialize db records
    for i in properties.keys():

        if properties[i].get('@type', None) == 'rdfs:Class':
            normalized_i = i.lower().replace('properties:', '')
            normalized_class_db[normalized_i] = i

    return normalized_class_db



def transform_properties(properties):

    properties_db = {}

    # Initialize db records
    for i in properties.keys():

        if properties[i].get('@type', None) == 'rdf:Property':
            properties_db[i] = properties[i]

    return properties_db

def transform_properties_normalized(properties):

    normalized_properties_db = {}

    # Initialize db records
    for i in properties.keys():

        if properties[i].get('@type', None) == 'rdf:Property':
            
            normalized_i = i.lower().replace('properties:', '')
            normalized_properties_db[normalized_i] = i

    return normalized_properties_db