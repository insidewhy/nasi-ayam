"""Agentic reasoning loop for document retrieval and response generation."""

from typing import Annotated, Any, cast

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

from nasi_ayam.generation.conversation import ConversationManager
from nasi_ayam.logging import get_logger
from nasi_ayam.progress import ProgressCallback
from nasi_ayam.retrieval.search import DocumentSearch, SearchResult

logger = get_logger("agent")

MAX_ITERATIONS = 3

SYSTEM_PROMPT = """You are a helpful knowledge retrieval assistant. Your role is to answer questions by searching through a document database.

IMPORTANT: You MUST always search first before responding. Never ask for clarification - just search with your best interpretation of the query.

When answering questions:
1. ALWAYS use the search_documents tool first - do not respond without searching
2. If the results aren't sufficient, use refine_search with different keywords
3. Always cite your sources by mentioning the document source and relevant context
4. If you cannot find relevant information after {max_iterations} search attempts, acknowledge this honestly

You have access to documents from two sources:
- "local": Documents from the local filesystem
- "github": Documents from a GitHub repository

Document types include: md (markdown), txt (text), pdf (PDF documents converted to markdown)

Be concise but thorough. Include relevant quotes when helpful."""


class RetrievalAgent:
    """Agent that uses tools to search documents and generate responses."""

    def __init__(
        self,
        database_url: str,
        anthropic_api_key: str,
        relevant_document_result_count: int,
        initial_retrieval_count: int,
        max_context_characters: int,
        reranker_model: str,
    ) -> None:
        self._database_url = database_url
        self._anthropic_api_key = anthropic_api_key
        self._top_k = relevant_document_result_count
        self._search = DocumentSearch(
            database_url, reranker_model, initial_retrieval_count
        )
        self._conversation = ConversationManager(
            database_url, anthropic_api_key, max_context_characters
        )
        self._iteration_count = 0
        self._last_results: list[SearchResult] = []
        self._progress_callback: ProgressCallback | None = None

    def set_progress_callback(self, callback: ProgressCallback | None) -> None:
        self._progress_callback = callback
        self._search.set_progress_callback(callback)

    def _report_progress(self, stage: str, is_starting: bool) -> None:
        if self._progress_callback:
            self._progress_callback(stage, is_starting)

    def _create_tools(self) -> list[Any]:
        """Create the tools for the agent."""
        search = self._search
        top_k = self._top_k
        agent = self

        @tool
        def search_documents(
            query: Annotated[str, "The search query to find relevant documents"],
            source: Annotated[
                str | None, "Optional filter: 'local' or 'github'"
            ] = None,
            doc_type: Annotated[
                str | None, "Optional filter: 'md', 'txt', or 'pdf'"
            ] = None,
        ) -> str:
            """Search for documents matching the query with optional filters."""
            results = search.search(query, top_k, source, doc_type)
            agent._last_results = results

            if not results:
                return "No documents found matching the query."

            output_parts = []
            for i, result in enumerate(results, 1):
                contexts = ""
                if result.semantic_contexts:
                    context_paths = [
                        c.get("heading_path", "") for c in result.semantic_contexts
                    ]
                    contexts = f" (Context: {', '.join(filter(None, context_paths))})"

                output_parts.append(
                    f"{i}. [{result.source}/{result.doc_type}]{contexts}\n"
                    f"   Score: {result.score:.3f}\n"
                    f"   Content: {result.content[:500]}{'...' if len(result.content) > 500 else ''}"
                )

            return "\n\n".join(output_parts)

        @tool
        def refine_search(
            new_keywords: Annotated[str, "New or expanded keywords to search with"],
        ) -> str:
            """Search again with different or expanded keywords."""
            return cast(str, search_documents.invoke({"query": new_keywords}))

        return [search_documents, refine_search]

    def _create_agent(self) -> Any:
        """Create the ReAct agent."""
        llm = ChatAnthropic(
            model="claude-sonnet-4-5-20250929",  # type: ignore[call-arg]
            api_key=self._anthropic_api_key,  # type: ignore[arg-type]
        )

        tools = self._create_tools()
        system_message = SYSTEM_PROMPT.format(max_iterations=MAX_ITERATIONS)

        return create_react_agent(llm, tools, prompt=system_message)

    def process_query(self, query: str) -> str:
        """Process a user query and generate a response.

        Args:
            query: The user's question.

        Returns:
            The agent's response with citations.
        """
        logger.info(f"Processing query: {query[:100]}...")

        self._last_results = []
        self._conversation.add_message("user", query)
        self._conversation.maybe_compact()

        agent = self._create_agent()

        history = self._conversation.get_langchain_messages()
        messages = history[:-1] + [HumanMessage(content=query)]

        config = {"recursion_limit": MAX_ITERATIONS * 2 + 5}

        try:
            result = agent.invoke({"messages": messages}, config=config)
            response_message = result["messages"][-1]

            if isinstance(response_message, AIMessage):
                response = str(response_message.content)
            else:
                response = str(response_message)

        except Exception as e:
            logger.error(f"Agent error: {e}")
            response = f"I encountered an error while processing your query: {str(e)}"

        self._report_progress("Answered", False)
        self._conversation.add_message("assistant", response)

        logger.info(f"Generated response ({len(response)} chars)")
        return response

    def get_last_results(self) -> list[SearchResult]:
        """Get the last search results for displaying sources."""
        return self._last_results
