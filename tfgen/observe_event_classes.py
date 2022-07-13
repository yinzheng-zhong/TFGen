import pandas as pd
import tfgen.utils as utils


def _convert_type(attributes):
    # check if attributes is a dataframe
    if isinstance(attributes, pd.DataFrame):
        attributes = list(attributes.astype(str).values)
    else:
        attributes = list(attributes)

    return attributes


def get_observable_ec(attributes):
    """
    This function finds all observable event classes from an offline dataset.
    :param attributes:
    :return:
    """
    attributes = _convert_type(attributes)

    num_attributes = len(attributes[0])
    eot_string = utils.convert_attr_to_ec(['EOT'] * num_attributes)

    event_classes = set([utils.convert_attr_to_ec(attribute) for attribute in attributes]) - {eot_string}
    return sorted(list(event_classes))


def get_observable_ec_top_n(attributes, n=10):
    """
    This function finds all observable event classes from an offline dataset.
    :param attributes:
    :param n: number of top occurring event classes to return.
    :return:
    """
    attributes = _convert_type(attributes)

    num_attributes = len(attributes[0])
    eot_string = utils.convert_attr_to_ec(['EOT'] * num_attributes)

    event_classes = [utils.convert_attr_to_ec(attribute) for attribute in attributes]
    keys = sorted(set(event_classes) - {eot_string})

    counts = {key: event_classes.count(key) for key in keys}

    top_ec = sorted(counts, key=counts.get, reverse=True)[:n]

    return top_ec
