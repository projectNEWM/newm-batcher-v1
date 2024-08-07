import cbor2


def to_bytes(hex_string: str) -> bytes:
    """ Convert the string to bytes and prepend with 'h' to indicate hexadecimal format.
    The bytes representation will be returned else a ValueError is raised.

    Args:
        s (str): The hexadecimal string used in byte conversion

    Returns:
        bytes: A bytestring in proper cbor format.
    """
    try:
        return bytes.fromhex(hex_string)
    except ValueError:
        raise ValueError(
            "non-hexadecimal number found in fromhex() arg at position 1")


def tag(tag_number: int, data: any):
    """Create a custom CBOR tag with any type of data.

    Args:
        tag_number (int): The constructor number plus 121
        data (any): Any valid cbor data

    Returns:
        CBORTag: A CBORTag
    """
    return cbor2.CBORTag(tag_number, data)


def dumps_with_indefinite_array(tag_number: int, data: list) -> bytes:
    """Create a indefinite array for a custom data type that does not have
    nested data types.

    Args:
        tag_number (int): The constructor number plus 121
        data (list): The fields list from the datum

    Returns:
        bytes: The cbor bytes of the custom data type
    """
    indefinite_array_start = b'\x9f'
    indefinite_array_end = b'\xff'

    # Start with the CBOR tag
    encoded_data = cbor2.dumps(cbor2.CBORTag(tag_number, None))[:-1]  # Remove the last byte (break byte)

    # Append the indefinite array start
    encoded_data += indefinite_array_start

    for item in data:
        encoded_data += cbor2.dumps(item)

    # Append the indefinite array end
    encoded_data += indefinite_array_end

    return encoded_data


def convert_datum(datum: dict) -> bytes:
    """Convert any datum used in the contracts into valid cbor. This should
    work with sale, queue, vault, oracle, and data datums.

    Args:
        datum (dict): The datum in json format.

    Returns:
        bytes: The cbor bytes of the datum type.
    """
    indefinite_array_start = b'\x9f'
    indefinite_array_end = b'\xff'

    # Start with the CBOR tag
    encoded_data = cbor2.dumps(cbor2.CBORTag(121 + datum["constructor"], None))[:-1]
    # Append the indefinite array start
    encoded_data += indefinite_array_start

    # lets go through the fields and type convert it
    top_level_fields = datum['fields']
    for field in top_level_fields:

        # custom types
        if "constructor" in field:
            encoded_data += cbor2.dumps(cbor2.CBORTag(121 + field["constructor"], None))[:-1]
            encoded_data += indefinite_array_start

            for value in field['fields']:
                # bytes object
                if 'bytes' in value:
                    encoded_data += cbor2.dumps(to_bytes(value['bytes']))

                # ints object
                if 'int' in value:
                    encoded_data += cbor2.dumps(value['int'])

                # map object
                if 'map' in value:
                    obj = {}
                    for entry in value['map']:
                        obj[entry['k']['int']] = entry['v']['int']
                    encoded_data += cbor2.dumps(obj)

                # list object
                if 'list' in value:
                    encoded_data += indefinite_array_start
                    for entry in value['list']:
                        if 'bytes' in entry:
                            encoded_data += cbor2.dumps(to_bytes(entry['bytes']))
                        if 'int' in entry:
                            encoded_data += cbor2.dumps(entry['int'])
                    encoded_data += indefinite_array_end

                # new custom type
                if 'constructor' in value:
                    nested_fields = []
                    for nested_value in value['fields']:
                        if 'bytes' in nested_value:
                            nested_fields.append(to_bytes(nested_value['bytes']))
                        if 'int' in nested_value:
                            nested_fields.append(nested_value['int'])
                    encoded_data += dumps_with_indefinite_array(121 + value["constructor"], nested_fields)

            # Append the indefinite array end
            encoded_data += indefinite_array_end

        if 'bytes' in field:
            encoded_data += cbor2.dumps(to_bytes(field['bytes']))

        if 'int' in field:
            encoded_data += cbor2.dumps(field['int'])

        if 'map' in field:
            obj = {}
            for entry in field['map']:
                obj[entry['k']['int']] = entry['v']['int']
            encoded_data += cbor2.dumps(obj)

        if 'list' in field:
            encoded_data += indefinite_array_start
            for entry in field['list']:
                if 'bytes' in entry:
                    encoded_data += cbor2.dumps(to_bytes(value['bytes']))
                if 'int' in value:
                    encoded_data += cbor2.dumps(value['int'])
            encoded_data += indefinite_array_end

    # Append the indefinite array end
    encoded_data += indefinite_array_end

    return encoded_data
