"""
input_validator.py
====================================
This module is used to validate identifiers from input file.
"""

from typing import List, Tuple


def validate_checksum(value: str, num_type: str) -> bool:
    """
        Check whether a given string is a valid NIP, or REGON number.

        :param value: The string to be checked.
        :param num_type: Declared identifier type.
        :return: True if checksum correct for indicated type, False otherwise.
    """
    if num_type == 'NIP':
        if len(value) != 10 or not value.isdigit():
            return False

        weights = [6, 5, 7, 2, 3, 4, 5, 6, 7]
        digits = [int(d) for d in value[:len(value)-1]]
        checksum = sum([w * d for w, d in zip(weights, digits)]) % 11

        if checksum == int(value[-1]):
            return True
        else:
            return False
    elif num_type == 'REGON':
        if len(value) not in [9, 14] or not value.isdigit():
            return False

        if len(value) == 9:
            weights = [8, 9, 2, 3, 4, 5, 6, 7]
            digits = [int(d) for d in value[:len(value)-1]]
            checksum = sum([w * d for w, d in zip(weights, digits)]) % 11

            if checksum == 10:
                checksum = 0

            if checksum == int(value[-1]):
                return True
        else:
            weights1 = [8, 9, 2, 3, 4, 5, 6, 7]
            weights2 = [2, 4, 8, 5, 0, 9, 7, 3, 6, 1, 2, 4, 8]
            digits = [int(d) for d in value[:len(value)-1]]

            checksum1 = sum([w * d for w, d in zip(weights1, digits[:8])]) % 11
            checksum2 = sum([w * d for w, d in zip(weights2, digits)]) % 11

            if checksum1 == 10:
                checksum1 = 0
            if checksum2 == 10:
                checksum2 = 0

            if checksum1 == int(value[8]) and checksum2 == int(value[-1]):
                return True
        return False
    else:
        if len(value) != 10:
            return False
        else:
            return True


class InputValidator:
    def __init__(self, filepath: str):
        """
            Initializes the InputValidator class.

            :param filepath: The path to the file from which the data will be loaded.
        """
        self.filepath = filepath
        self.data = []
        self.errors = []

    def validate_input(self) -> Tuple[List, List]:
        """
            Public method used to validate the data from the input file and return it as a list of tuples containing
            valid NIP or REGON numbers.

            :param: None.
            :return: List of tuples with valid NIP or REGON number and type, and list of tuples with rows
                     containing incorrect data.
        """
        with open(self.filepath, 'r') as f:
            lines = f.readlines()
            for line in lines:
                num, num_type = line.strip().split(',')
                if num_type in ['NIP', 'REGON', 'KRS']:
                    if validate_checksum(num, num_type):
                        self.data.append((num, num_type))
                    else:
                        self.errors.append((num, num_type, "Incorrect checksum for the specified number and its type"))
                else:
                    self.errors.append((num, num_type, "Incorrect identifier type declared"))

        return self.data, self.errors
