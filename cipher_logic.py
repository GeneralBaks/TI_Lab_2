from __future__ import annotations

import numpy as np
from numba import njit

from config import POLYNOMIAL_TAPS, REGISTER_SIZE

TAPS_ARRAY = np.array(POLYNOMIAL_TAPS, dtype=np.int32)


def clean_seed_text(seed_text: str) -> str:
    return "".join(ch for ch in seed_text if ch in "01")


def seed_text_to_register_state(seed_text: str) -> list[int]:
    cleaned = clean_seed_text(seed_text)
    if len(cleaned) != REGISTER_SIZE:
        raise ValueError(f"Нужно {REGISTER_SIZE} бит")
    return [int(cleaned, 2)]


@njit
def _numba_xor_core(input_bytes, state, taps, reg_size):
    size = len(input_bytes)
    res = np.empty(size, dtype=np.uint8)
    key = np.empty(size, dtype=np.uint8)

    mask = (1 << reg_size) - 1
    shift_taps = taps - 1
    out_shift = reg_size - 1

    current_state = state

    for i in range(size):
        byte_key = 0
        for _ in range(8):
            feedback = 0
            for t in shift_taps:
                feedback ^= (current_state >> t) & 1

            out_bit = (current_state >> out_shift) & 1
            byte_key = (byte_key << 1) | out_bit
            current_state = ((current_state << 1) | feedback) & mask

        key[i] = byte_key
        res[i] = input_bytes[i] ^ byte_key

    return res, key, current_state


def xor_chunk_with_lfsr(
    input_chunk: bytes, register_state: list[int]
) -> tuple[bytes, bytes]:
    input_array = np.frombuffer(input_chunk, dtype=np.uint8)

    res_arr, key_arr, new_state = _numba_xor_core(
        input_array, register_state[0], TAPS_ARRAY, REGISTER_SIZE
    )

    register_state[0] = new_state

    return res_arr.tobytes(), key_arr.tobytes()
