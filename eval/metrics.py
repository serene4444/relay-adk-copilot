"""ADK plugin that records, for every request: which agents ran, and the
latency and token usage of every Gemini call (including nested specialist calls)."""
import time

from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.plugins.base_plugin import BasePlugin


class MetricsPlugin(BasePlugin):
    def __init__(self) -> None:
        super().__init__(name="fieldkit_metrics")
        self.reset()

    def reset(self) -> None:
        self.agents_run: list[str] = []
        self.model_calls: list[dict] = []
        self._started: dict[str, list[float]] = {}

    async def before_agent_callback(self, *, agent: BaseAgent, callback_context: CallbackContext):
        self.agents_run.append(agent.name)
        return None

    async def before_model_callback(self, *, callback_context: CallbackContext, llm_request: LlmRequest):
        self._started.setdefault(callback_context.agent_name, []).append(time.perf_counter())
        return None

    async def after_model_callback(self, *, callback_context: CallbackContext, llm_response: LlmResponse):
        starts = self._started.get(callback_context.agent_name) or [time.perf_counter()]
        seconds = time.perf_counter() - starts.pop()
        usage = llm_response.usage_metadata
        self.model_calls.append({
            "agent": callback_context.agent_name,
            "seconds": seconds,
            "input_tokens": (usage.prompt_token_count or 0) if usage else 0,
            # Thinking tokens are billed as output, so count them too.
            "output_tokens": ((usage.candidates_token_count or 0)
                              + (usage.thoughts_token_count or 0)) if usage else 0,
        })
        return None

