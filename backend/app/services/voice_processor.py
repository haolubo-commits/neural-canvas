"""
Voice Ingestion & Semantic Intent Parser for NeuralCanvas.
Handles streaming audio VAD (Voice Activity Detection), RMS energy calculation,
and speech-to-action intent classification.
"""

from typing import Dict, Any, List, Optional, Tuple
import re
import math
import struct
from app.core.config import settings
from app.models.canvas import NodeType, ActionType


class VoiceProcessor:
    def __init__(self, energy_threshold: float = settings.VAD_ENERGY_THRESHOLD):
        self.energy_threshold = energy_threshold

    @staticmethod
    def calculate_rms_energy(pcm_bytes: bytes) -> float:
        """
        Computes Root Mean Square (RMS) energy for 16-bit linear PCM mono audio.
        Normalized to 0.0 - 1.0 range.
        """
        if not pcm_bytes:
            return 0.0

        # Unpack signed 16-bit integers (h = 2 bytes)
        num_samples = len(pcm_bytes) // 2
        if num_samples == 0:
            return 0.0

        try:
            samples = struct.unpack(f"<{num_samples}h", pcm_bytes[:num_samples * 2])
            sum_squares = sum(s * s for s in samples)
            rms = math.sqrt(sum_squares / num_samples)
            # Normalize against max 16-bit amplitude (32768)
            return round(min(1.0, rms / 32768.0), 4)
        except Exception:
            return 0.0

    def detect_voice_activity(self, pcm_bytes: bytes) -> Tuple[bool, float]:
        """
        Determines whether the provided PCM audio chunk contains active speech.
        Returns (is_active_speech, rms_energy).
        """
        energy = self.calculate_rms_energy(pcm_bytes)
        is_speech = energy >= self.energy_threshold
        return is_speech, energy

    def parse_speech_intent(self, text: str) -> Dict[str, Any]:
        """
        Parses transcribed natural speech into structured agentic actions.
        Identifies creation, wiring, transformations, and tool executions.
        """
        clean_text = text.strip()
        lower_text = clean_text.lower()

        # 1. CREATE NODE
        # Examples:
        # "create a filter node named churn_filter"
        # "add prompt node for customer feedback"
        # "new tool node"
        create_match = re.search(
            r"(?:create|add|new|insert|spawn)\s+(?:a\s+|an\s+)?(prompt|tool|data_source|filter|transform|visualization|output)\s+node(?:\s+(?:named|called|labeled)\s+([a-zA-Z0-9_\-\s]+))?",
            lower_text,
        )
        if create_match:
            raw_type = create_match.group(1).lower()
            node_type = self._map_node_type(raw_type)
            label = create_match.group(2).strip() if create_match.group(2) else f"{raw_type.capitalize()} Node"

            # Check if coordinates mentioned, e.g. "at 200, 300"
            pos_match = re.search(r"at\s+(\d+)\s*,\s*(\d+)", lower_text)
            pos_x = float(pos_match.group(1)) if pos_match else 220.0
            pos_y = float(pos_match.group(2)) if pos_match else 180.0

            return {
                "action_type": ActionType.CREATE_NODE,
                "confidence": 0.96,
                "parameters": {
                    "node_type": node_type.value,
                    "label": label,
                    "position_x": pos_x,
                    "position_y": pos_y,
                    "data": {"created_via": "voice_intent", "original_speech": clean_text},
                },
                "summary": f"Create {node_type.value} node '{label}'",
            }

        # 2. CONNECT NODES (Wire / Edge)
        # Examples:
        # "connect node A to node B"
        # "wire churn_filter to slack_alert"
        # "link prompt to tool"
        connect_match = re.search(
            r"(?:connect|wire|link|pipe)\s+(?:node\s+)?([a-zA-Z0-9_\-]+)\s+(?:to|into|with)\s+(?:node\s+)?([a-zA-Z0-9_\-]+)",
            lower_text,
        )
        if connect_match:
            source = connect_match.group(1).strip()
            target = connect_match.group(2).strip()
            return {
                "action_type": ActionType.CONNECT_NODES,
                "confidence": 0.94,
                "parameters": {
                    "source": source,
                    "target": target,
                    "edge_type": "data_stream",
                },
                "summary": f"Connect '{source}' -> '{target}'",
            }

        # 3. DELETE NODE
        # Examples: "delete node churn_filter", "remove node 123"
        delete_match = re.search(
            r"(?:delete|remove|destroy|drop)\s+(?:node\s+)?([a-zA-Z0-9_\-]+)",
            lower_text,
        )
        if delete_match:
            target_node = delete_match.group(1).strip()
            return {
                "action_type": ActionType.DELETE_NODE,
                "confidence": 0.92,
                "parameters": {"node_target": target_node},
                "summary": f"Delete node '{target_node}'",
            }

        # 4. EXECUTE TOOL
        # Examples: "execute tool rag_search", "run web_crawler"
        tool_match = re.search(
            r"(?:execute|run|invoke|trigger)\s+(?:tool\s+)?([a-zA-Z0-9_\-]+)",
            lower_text,
        )
        if tool_match:
            tool_name = tool_match.group(1).strip()
            return {
                "action_type": ActionType.EXECUTE_TOOL,
                "confidence": 0.90,
                "parameters": {"tool_name": tool_name},
                "summary": f"Execute tool '{tool_name}'",
            }

        # 5. VOICE ASSISTANT QUERY (Default Intent)
        return {
            "action_type": ActionType.VOICE_SYNTHESIS,
            "confidence": 0.85,
            "parameters": {
                "query": clean_text,
                "context": "multimodal_dialogue",
            },
            "summary": f"Voice dialogue: '{clean_text[:60]}...'",
        }

    @staticmethod
    def _map_node_type(type_str: str) -> NodeType:
        mapping = {
            "prompt": NodeType.PROMPT,
            "tool": NodeType.TOOL,
            "data_source": NodeType.DATA_SOURCE,
            "filter": NodeType.FILTER,
            "transform": NodeType.TRANSFORM,
            "visualization": NodeType.VISUALIZATION,
            "output": NodeType.OUTPUT,
        }
        return mapping.get(type_str, NodeType.PROMPT)
