LangGraph Chatbot with Saved Chats & Tools

A robust, stateful conversational AI built using LangGraph, LangChain, OpenAI, and tool integration — with full session persistence.

Highlights:

Context-aware dialog: Maintains conversation history across user sessions using LangGraph and SQLite check-pointing backed by SqliteSaver, ensuring context continuity.

Multi-turn interaction flows: Architected with LangGraph’s StateGraph, enabling dynamic multi-node conversation pathways based on user input.

Tool integration: Supports on-demand tool execution (e.g., calculator, real-time DuckDuckGo search, and stock price fetch via Alpha Vantage), enhancing the chatbot’s capabilities beyond plain text responses.

Streamlit interface: Clean, intuitive chat UI with sidebar controls to start new chats, browse previous threads, and load full conversation history.

Persistent memory: Each conversation thread is stored in the chatbot.db SQLite file, allowing users to revisit and continue past chats effortlessly.

Adaptable & portable: Designed for easy deployment on platforms like Streamlit Cloud or Hugging Face Spaces, with options to swap out the backend (e.g., SQLite → external DB) as needed.
