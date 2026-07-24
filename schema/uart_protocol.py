from __future__ import annotations

from dataclasses import dataclass


FRAME_SYNC = b"\xAA\x55"


@dataclass(frozen=True)
class Frame:
    msg_type: int
    payload: bytes


def crc8_maxim(data: bytes) -> int:
    crc = 0x00
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = ((crc >> 1) ^ 0x8C) if (crc & 0x01) else (crc >> 1)
    return crc & 0xFF


def encode_frame(msg_type: int, payload: bytes = b"") -> bytes:
    length = len(payload)
    header = bytes([msg_type & 0xFF, length & 0xFF]) + payload
    return FRAME_SYNC + header + bytes([crc8_maxim(header)])


def decode_frame(raw: bytes) -> Frame:
    if len(raw) < 5 or raw[:2] != FRAME_SYNC:
        raise ValueError("invalid frame sync")
    msg_type = raw[2]
    length = raw[3]
    payload = raw[4:-1]
    if len(payload) != length:
        raise ValueError("invalid frame length")
    expected_crc = raw[-1]
    actual_crc = crc8_maxim(raw[2:-1])
    if expected_crc != actual_crc:
        raise ValueError("invalid frame crc")
    return Frame(msg_type=msg_type, payload=payload)
