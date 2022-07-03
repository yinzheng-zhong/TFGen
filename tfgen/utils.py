def convert_attr_to_ec(attributes):
    attributes = map(lambda x: str(x), attributes)
    return '|'.join(attributes)
