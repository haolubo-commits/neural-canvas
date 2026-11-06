"""
Unit tests for VoiceProcessor.
Tests RMS energy calculation, VAD activity detection, and speech-to-intent parsing.
"""

import math
import struct
import pytest
from app.services.voice_processor import VoiceProcessor
from app.models.canvas import ActionType, NodeType


@pytest.fixture
def voice_processor():
    return VoiceProcessor(energy_threshold=0.015)


def make_pcm_frame(amplitude: int, freq: float = 440.0, num_samples: int = 320) -> bytes:
    """Creates signed 16-bit PCM bytes."""
    samples = [
        int(amplitude * math.sin(2.0 * math.pi * freq * (i / 16000.0)))
        for i in range(num_samples)
    ]
    return struct.pack(f"<{len(samples)}h", *samples)


def test_rms_energy_silence(voice_processor):
    silence_pcm = bytes(320 * 2)  # All zeros
    energy = voice_processor.calculate_rms_energy(silence_pcm)
    assert energy == 0.0


def test_rms_energy_active_audio(voice_processor):
    speech_pcm = make_pcm_frame(amplitude=16000)
    energy = voice_processor.calculate_rms_energy(speech_pcm)
    assert energy > 0.30
    assert energy <= 1.0


def test_vad_detection_speech_vs_silence(voice_processor):
    speech_pcm = make_pcm_frame(amplitude=12000)
    is_speech, energy = voice_processor.detect_voice_activity(speech_pcm)
    assert is_speech is True
    assert energy >= voice_processor.energy_threshold

    silence_pcm = bytes(320 * 2)
    is_speech, energy = voice_processor.detect_voice_activity(silence_pcm)
    assert is_speech is False
    assert energy < voice_processor.energy_threshold


def test_intent_parsing_create_node(voice_processor):
    text = "Create a filter node named churn_filter at 350, 220"
    intent = voice_processor.parse_speech_intent(text)

    assert intent["action_type"] == ActionType.CREATE_NODE
    assert intent["confidence"] >= 0.90
    assert intent["parameters"]["node_type"] == NodeType.FILTER.value
    assert intent["parameters"]["label"] == "churn_filter"
    assert intent["parameters"]["position_x"] == 350.0
    assert intent["parameters"]["position_y"] == 220.0


def test_intent_parsing_connect_nodes(voice_processor):
    text = "Connect node prompt_input to node slack_bot"
    intent = voice_processor.parse_speech_intent(text)

    assert intent["action_type"] == ActionType.CONNECT_NODES
    assert intent["confidence"] >= 0.90
    assert intent["parameters"]["source"] == "prompt_input"
    assert intent["parameters"]["target"] == "slack_bot"


def test_intent_parsing_delete_node(voice_processor):
    text = "Delete node old_data_sink"
    intent = voice_processor.parse_speech_intent(text)

    assert intent["action_type"] == ActionType.DELETE_NODE
    assert intent["parameters"]["node_target"] == "old_data_sink"


def test_intent_parsing_execute_tool(voice_processor):
    text = "Execute tool vector_retrieval_agent"
    intent = voice_processor.parse_speech_intent(text)

    assert intent["action_type"] == ActionType.EXECUTE_TOOL
    assert intent["parameters"]["tool_name"] == "vector_retrieval_agent"


def test_intent_parsing_voice_synthesis_fallback(voice_processor):
    text = "What is the predicted churn rate for next quarter?"
    intent = voice_processor.parse_speech_intent(text)

    assert intent["action_type"] == ActionType.VOICE_SYNTHESIS
    assert intent["parameters"]["query"] == text
