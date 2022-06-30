import pandas as pd
import tfgen.utils as utils


def get_observable_ec(attributes):
    """
    This function finds all observable event classes from an offline dataset.
    :param attributes:
    :return:
    """
    # check if attributes is a dataframe
    if isinstance(attributes, pd.DataFrame):
        attributes = list(attributes.astype(str).values)
    else:
        attributes = list(attributes)

    event_classes = set([utils.convert_attr_to_ec(attribute) for attribute in attributes])
    return list(event_classes)
