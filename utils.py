def get_speed(message_fields):
    """ get_speed
    return the speed as float in km/h from a message.as_dict()['fields'] object

    Args:
        message_fields: a message.as_dict()['fields'] object (with name 'record')

    Returns:
        the speed as float in km/h, or 0. if not found
    """
    for message_field in message_fields:
        if message_field['name'] == 'speed':
            return 3.6 * message_field['value']
    return 0.


get_speed.__name__ = "Speed [km/h]"


def get_heart_rate(message_fields):
    """ get_heart_rate
    return the heart rate as float from a message.as_dict()['fields'] object

    Args:
        message_fields: a message.as_dict()['fields'] object (with name 'record')

    Returns:
        heart rate in bpm or 50. if not found
    """
    for message_field in message_fields:
        if message_field['name'] == 'heart_rate':
            return message_field['value']
    return 50.


get_heart_rate.__name__ = "heart rate [bpm]"


def get_pace(message_fields):
    for message_field in message_fields:
        if message_field['name'] == 'speed':
            try:
                return 60. / (3.6 * message_field['value'])
            except ZeroDivisionError:
                return 0.
    return 0.


get_pace.__name__ = "pace [min/km]"
