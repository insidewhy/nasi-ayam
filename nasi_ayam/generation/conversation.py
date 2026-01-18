"""Conversation management with compaction support."""

from dataclasses import dataclass
from uuid import UUID

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from nasi_ayam.database import (
    get_cursor,
    get_message_count,
    get_messages,
    insert_message,
    mark_messages_compacted,
)
from nasi_ayam.logging import get_logger

logger = get_logger("conversation")

COMPACTION_SYSTEM_PROMPT = """Summarize the following conversation history into a concise context summary.
Focus on key information, decisions made, and relevant context that would be useful for continuing the conversation.
Preserve important details like file names, technical decisions, and user preferences.
Keep the summary focused and actionable."""


@dataclass
class Message:
    """A conversation message."""

    id: UUID
    role: str
    content: str
    is_compacted: bool


class ConversationManager:
    """Manages conversation history with automatic compaction."""

    def __init__(
        self,
        database_url: str,
        anthropic_api_key: str,
        max_context_characters: int,
    ) -> None:
        self._database_url = database_url
        self._anthropic_api_key = anthropic_api_key
        self._max_context_characters = max_context_characters

    def add_message(self, role: str, content: str) -> UUID:
        """Add a new message to the conversation history."""
        with get_cursor(self._database_url) as cur:
            message_id = insert_message(cur, role, content)
        logger.debug(f"Added {role} message: {content[:50]}...")
        return message_id

    def get_history(self) -> list[Message]:
        """Get the full conversation history."""
        with get_cursor(self._database_url) as cur:
            rows = get_messages(cur)

        return [
            Message(
                id=row["id"],
                role=row["role"],
                content=row["content"],
                is_compacted=row["is_compacted"],
            )
            for row in rows
        ]

    def get_langchain_messages(self) -> list[HumanMessage | AIMessage]:
        """Get conversation history as LangChain message objects."""
        history = self.get_history()
        messages: list[HumanMessage | AIMessage] = []

        for msg in history:
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                messages.append(AIMessage(content=msg.content))

        return messages

    def should_compact(self) -> bool:
        """Check if compaction is needed."""
        with get_cursor(self._database_url) as cur:
            total_chars = get_message_count(cur)
        return total_chars > self._max_context_characters

    def compact(self) -> None:
        """Compact older messages into a summary.

        Keeps the last 4-6 exchanges intact and summarizes the rest.
        """
        history = self.get_history()

        if len(history) <= 8:
            logger.debug("Not enough messages to compact")
            return

        messages_to_compact = history[:-8]
        if not messages_to_compact:
            return

        to_summarize = [m for m in messages_to_compact if not m.is_compacted]

        if not to_summarize:
            logger.debug("No new messages to compact")
            return

        logger.info(f"Compacting {len(to_summarize)} messages")

        conversation_text = "\n".join(
            f"{m.role.upper()}: {m.content}" for m in to_summarize
        )

        llm = ChatAnthropic(
            model="claude-sonnet-4-5-20250929",  # type: ignore[call-arg]
            api_key=self._anthropic_api_key,  # type: ignore[arg-type]
        )

        summary_messages = [
            SystemMessage(content=COMPACTION_SYSTEM_PROMPT),
            HumanMessage(content=conversation_text),
        ]

        response = llm.invoke(summary_messages)
        summary = response.content

        with get_cursor(self._database_url) as cur:
            insert_message(
                cur,
                "system",
                f"[Previous conversation summary]\n{summary}",
                is_compacted=True,
            )
            mark_messages_compacted(cur, [m.id for m in to_summarize])

        logger.info(f"Compacted messages into summary ({len(str(summary))} chars)")

    def maybe_compact(self) -> None:
        """Compact if needed."""
        if self.should_compact():
            self.compact()
