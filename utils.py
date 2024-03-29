def get_power_right_left(message_fields):
    power = 0.
    lrencoded = None
    for message_field in message_fields:
        if message_field['name'] == 'power':
            power = message_field['value']
        if message_field['name'] == 'left_right_balance':
            lrencoded = message_field['value']
    if lrencoded == 'right':
        lrencoded = 0x80
    if lrencoded is None:
        return (None, None)

    if lrencoded & 0x80:
        factor_right = (lrencoded & 0x7f)/100.
    else:
        factor_right = 1 - (lrencoded & 0x7f)/100.
    factor_left = 1 - factor_right
    return (factor_right * power, factor_left * power)


def get_speed(message_fields):
    """ get_speed
    return the speed as float in km/h from a message.as_dict()['fields'] object

    Args:
        message_fields: a message.as_dict()['fields'] object (with name 'record')

    Returns:
        the speed as float in km/h, or 0. if not found
    """
    for message_field in message_fields:
        try:
            if message_field['name'] == 'speed':
                return 3.6 * message_field['value']
        except TypeError:
            # NoneType from message_field['value']
            pass
    for message_field in message_fields:
        if message_field['name'] == 'enhanced_speed':
            try:
                return 3.6 * message_field['value']
            except TypeError:
                # NoneType or something???
                pass
    return 0.


get_speed.__name__ = "Speed [km/h]"


def get_power(message_fields):
    """ get_power
    return the power as float in Watts from a message.as_dict()['fields'] object

    Args:
        message_fields: a message.as_dict()['fields'] object (with name 'record')

    Returns:
        the power as float in watts, or 0. if not found
    """
    for message_field in message_fields:
        if message_field['name'] == 'power':
            return message_field['value']
    return 0.


get_power.__name__ = "Power [Watts]"


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


def get_cadence(message_fields):
    """ get_cadence
    return the cadence as float in 1/min from a message.as_dict()['fields'] object

    Args:
        message_fields: a message.as_dict()['fields'] object (with name 'record')

    Returns:
        the cadence as float in 1/min, or 0 if not found
    """
    for message_field in message_fields:
        if message_field['name'] == 'cadence':
            return message_field['value']
    return 0.


get_cadence.__name__ = "Cadence [1/min]"
