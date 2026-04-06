from typing import Final

REGISTER_SIZE: Final[int] = 35
POLYNOMIAL_TAPS: Final[tuple[int, ...]] = (35, 2)

BITS_IN_BYTE: Final[int] = 8

CHUNK_SIZE: Final[int] = 4 * 1024 * 1024

FIRST_BYTES_COUNT: Final[int] = 32
LAST_BYTES_COUNT: Final[int] = 16
