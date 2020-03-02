from typing import List, Union

from numpy import array_equal

# Utility function to convert an ascii character to binary.
def ascii_to_binary(char: str) -> List[int]:
    binary_char = bin(int.from_bytes(char.encode(), 'big')).replace('b', '')

    return list(map(lambda x: int(x), binary_char))

# Utility function to convert from binary to ascii
def binary_to_ascii(binary: List[int]) -> str:
    character_string = int(''.join(list(map(lambda x: str(x), binary))), 2)
    return character_string.to_bytes((character_string.bit_length() + 7) // 8, 'big').decode()

# Utility function to check if list is not comprised of 0 and 1
def check_binary(data: Union[List[int], List[int]]) -> bool:
    return array_equal(data, data.astype(bool))
