from __future__ import annotations

import os
import tempfile

from cipher_logic import seed_text_to_register_state, xor_chunk_with_lfsr
from config import CHUNK_SIZE, FIRST_BYTES_COUNT, LAST_BYTES_COUNT


class _ByteCollector:
    def __init__(self) -> None:
        self._first = bytearray()
        self._last = bytearray()
        self.total: int = 0

    def feed(self, chunk: bytes) -> None:
        self.total += len(chunk)

        needed = FIRST_BYTES_COUNT - len(self._first)
        if needed > 0:
            self._first.extend(chunk[:needed])

        combined = bytes(self._last) + chunk
        self._last = bytearray(combined[-LAST_BYTES_COUNT:])

    def format_as_binary_text(self) -> str:
        if self.total == 0:
            return "(пусто)"

        if self.total <= FIRST_BYTES_COUNT + LAST_BYTES_COUNT:
            all_bytes = self._reconstruct_all_bytes()
            return " ".join(f"{b:08b}" for b in all_bytes)

        first_str = " ".join(f"{b:08b}" for b in self._first)
        last_str = " ".join(f"{b:08b}" for b in self._last)
        return f"{first_str} ... {last_str}"

    def _reconstruct_all_bytes(self) -> bytes:
        if self.total <= FIRST_BYTES_COUNT:
            return bytes(self._first[: self.total])

        overlap = FIRST_BYTES_COUNT + LAST_BYTES_COUNT - self.total
        tail = bytes(self._last[max(0, overlap) :])
        return bytes(self._first) + tail


def read_file_binary_text(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise FileNotFoundError(file_path)

    collector = _ByteCollector()

    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            collector.feed(chunk)

    return collector.format_as_binary_text()


def process_file_stream(
    source_file_path: str,
    initial_seed_text: str,
) -> tuple[str, str, str, str]:
    register_state = seed_text_to_register_state(initial_seed_text)

    source_collector = _ByteCollector()
    key_collector = _ByteCollector()
    result_collector = _ByteCollector()

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".bin")

    try:
        with open(source_file_path, "rb") as source_file:
            while True:
                input_chunk = source_file.read(CHUNK_SIZE)
                if not input_chunk:
                    break

                result_chunk, key_chunk = xor_chunk_with_lfsr(
                    input_chunk, register_state
                )

                temp_file.write(result_chunk)

                source_collector.feed(input_chunk)
                key_collector.feed(key_chunk)
                result_collector.feed(result_chunk)
    finally:
        temp_file.close()

    if source_collector.total == 0:
        empty = "(пусто)"
        return temp_file.name, empty, empty, empty

    return (
        temp_file.name,
        source_collector.format_as_binary_text(),
        key_collector.format_as_binary_text(),
        result_collector.format_as_binary_text(),
    )


def save_temporary_result(temp_file_path: str, destination_file_path: str) -> None:
    with open(temp_file_path, "rb") as src, open(destination_file_path, "wb") as dst:
        while True:
            chunk = src.read(CHUNK_SIZE)
            if not chunk:
                break
            dst.write(chunk)
