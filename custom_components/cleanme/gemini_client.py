"""Gemini 3 Pro Preview API client for CleanMe."""
from __future__ import annotations

import base64
import json
import logging
import time
from typing import Any, Dict

import aiohttp

from .const import GEMINI_MODEL, GEMINI_API_BASE

_LOGGER = logging.getLogger(__name__)


class GeminiClientError(Exception):
    """Raised when the Gemini API client fails."""


class GeminiClient:
    """Client for Gemini 3 Pro Preview API with Deep Think mode."""

    def __init__(self, api_key: str) -> None:
        """Initialize Gemini client."""
        self._api_key = api_key

    async def analyze_image(
        self,
        session: aiohttp.ClientSession,
        image_bytes: bytes,
        room_name: str,
        personality: str,
        pickiness: int,
    ) -> Dict[str, Any]:
        """
        Analyze room image using Gemini 3 Pro Preview.
        
        Returns dict with:
        - tidy: bool
        - tasks: list of task strings
        - comment: str
        - severity: str (low/medium/high)
        """
        start_time = time.time()
        
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        
        prompt = self._build_prompt(room_name, personality, pickiness)
        
        url = f"{GEMINI_API_BASE}/models/{GEMINI_MODEL}:generateContent"
        
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self._api_key,
        }
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": image_b64,
                            }
                        },
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.4,
                "topK": 32,
                "topP": 1,
                "maxOutputTokens": 2048,
            },
            # Deep Think mode with thinking_level parameter
            "thinking_level": 2,  # 0=no thinking, 1=light, 2=deep
        }
        
        try:
            async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=90)) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise GeminiClientError(f"Gemini API HTTP {resp.status}: {text}")
                
                data = await resp.json()
        except aiohttp.ClientError as err:
            raise GeminiClientError(f"Network error calling Gemini API: {err}") from err
        except Exception as err:
            raise GeminiClientError(f"Unexpected error calling Gemini API: {err}") from err
        
        response_time = time.time() - start_time
        
        # Parse Gemini response
        try:
            candidates = data.get("candidates", [])
            if not candidates:
                raise ValueError("No candidates in response")
            
            first = candidates[0]
            parts = first.get("content", {}).get("parts", [])
            
            text_block = None
            for part in parts:
                if "text" in part:
                    text_block = part["text"]
                    break
            
            if not text_block:
                raise ValueError("No text content in response")
            
            # Extract JSON from response (handle markdown code blocks)
            text_block = text_block.strip()
            if text_block.startswith("```json"):
                text_block = text_block[7:]
            if text_block.startswith("```"):
                text_block = text_block[3:]
            if text_block.endswith("```"):
                text_block = text_block[:-3]
            
            parsed = json.loads(text_block.strip())
            
        except Exception as err:
            _LOGGER.error("Failed to parse Gemini response: %s", data)
            raise GeminiClientError(f"Malformed Gemini response: {err}") from err
        
        # Validate and normalize response
        result = self._validate_response(parsed)
        result["api_response_time"] = response_time
        result["image_size"] = len(image_bytes)
        
        return result

    def _build_prompt(self, room_name: str, personality: str, pickiness: int) -> str:
        """Build the analysis prompt with personality and pickiness instructions."""
        personality_instructions = self._get_personality_instructions(personality)
        pickiness_instructions = self._get_pickiness_instructions(pickiness)
        
        return f"""You are analyzing a room for tidiness using image analysis.

Room type: {room_name}
Analysis mode: {personality}
Pickiness level: {pickiness}/5

{personality_instructions}

{pickiness_instructions}

Look at this image carefully and determine:
1. Is the room tidy and organized?
2. What specific tasks need doing (if any)?
3. A brief, {personality}-toned comment

Respond ONLY with valid JSON in this exact format:
{{
  "tidy": true/false,
  "tasks": ["task 1", "task 2"],
  "comment": "your observation",
  "severity": "low/medium/high"
}}

Focus on: clutter, dishes, trash, surfaces needing cleaning, items out of place.
Be practical and realistic.
Do not include any markdown formatting, just raw JSON."""

    def _get_personality_instructions(self, personality: str) -> str:
        """Get personality-specific instructions."""
        instructions = {
            "chill": "Be relaxed and supportive. Only flag obvious messes. Use a friendly, encouraging tone.",
            "thorough": "Be detailed and helpful. Use normal tidiness standards. Provide clear, actionable guidance.",
            "strict": "Be critical and demanding. Flag every imperfection. Use a firm, no-nonsense tone.",
            "sarcastic": "Be funny and snarky. Make cleanup entertaining. Use witty observations and playful criticism.",
            "professional": "Be formal and clinical. Use business language. Provide objective, matter-of-fact assessments.",
        }
        return instructions.get(personality, instructions["thorough"])

    def _get_pickiness_instructions(self, pickiness: int) -> str:
        """Get pickiness level instructions."""
        instructions = {
            1: "Level 1 Pickiness: Only report major messes, health hazards, or obvious clutter that significantly impacts the space.",
            2: "Level 2 Pickiness: Report significant items but ignore minor things. Focus on visible problems that should be addressed soon.",
            3: "Level 3 Pickiness: Report normal everyday tidiness issues. Use standard home cleanliness expectations.",
            4: "Level 4 Pickiness: Be thorough and report most issues. Notice things that might be overlooked in a casual inspection.",
            5: "Level 5 Pickiness: Be extremely thorough. Report any imperfections, dust, items slightly out of place, or anything less than perfect.",
        }
        return instructions.get(pickiness, instructions[3])

    @staticmethod
    def _validate_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize the API response."""
        if not isinstance(data, dict):
            raise GeminiClientError("Response must be a JSON object")
        
        # Validate tidy field
        tidy = data.get("tidy")
        if not isinstance(tidy, bool):
            raise GeminiClientError(f"Invalid 'tidy' field: {tidy}")
        
        # Validate tasks field
        tasks = data.get("tasks", [])
        if not isinstance(tasks, list):
            raise GeminiClientError("'tasks' must be a list")
        
        # Clean and validate tasks
        cleaned_tasks = []
        for task in tasks:
            if isinstance(task, str) and task.strip():
                cleaned_tasks.append(task.strip())
        
        # Validate comment
        comment = data.get("comment", "")
        if not isinstance(comment, str):
            comment = str(comment)
        
        # Validate severity
        severity = data.get("severity", "medium")
        if severity not in ("low", "medium", "high"):
            severity = "medium"
        
        return {
            "tidy": tidy,
            "tasks": cleaned_tasks,
            "comment": comment.strip(),
            "severity": severity,
        }

    async def validate_api_key(self, session: aiohttp.ClientSession) -> bool:
        """Validate that the API key works."""
        url = f"{GEMINI_API_BASE}/models/{GEMINI_MODEL}"
        
        headers = {
            "x-goog-api-key": self._api_key,
        }
        
        try:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                return resp.status == 200
        except Exception:
            return False
