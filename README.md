# LangGraph Multi-Agent Research Assistant

This project is a multi-agent research assistant built using **LangGraph**, **LangChain**, **Ollama**, and **Streamlit**. It demonstrates a production-ready, modular architecture for a research assistant system with robust state management, conditional routing, feedback loops, and human-in-the-loop interactions.

## Deliverables Checklist

✅ **1. Working LangGraph with 4 Agents**
   - **Clarity Agent** (`research_assistant/agents/clarity.py`): Analyzes query clarity and company identification
   - **Research Agent** (`research_assistant/agents/research.py`): Fetches and processes company data
   - **Validator Agent** (`research_assistant/agents/validator.py`): Reviews research quality
   - **Synthesis Agent** (`research_assistant/agents/synthesis.py`): Generates final summaries

✅ **2. State Schema Definition with All Required Fields**
   - Location: `research_assistant/graph/state.py`
   - Inherits from `MessagesState` for conversation history
   - Fields: `query`, `clarity_status`, `company_name`, `research_findings`, `confidence_score`, `validation_result`, `attempts`, `summary`

✅ **3. Three Conditional Routing Functions**
   - Location: `research_assistant/graph/workflow.py`
   - **`route_clarity()`**: Routes to Research (clear) or END (needs clarification)
   - **`route_research()`**: Always routes to Validator
   - **`route_validator()`**: Routes to Synthesis (sufficient) or back to Research (insufficient & attempts < 3)

✅ **4. Feedback Loop: Validator → Research with Attempt Counter**
   - Validator can reject insufficient research and loop back to Research
   - Attempt counter increments on each Research Agent execution
   - Maximum 3 attempts before forcing Synthesis

✅ **5. Interrupt Mechanism for Unclear Queries**
   - When Clarity Agent determines a query is unclear, the workflow ends
   - Streamlit app detects this and prompts the user for clarification
   - User provides clarification, and the next invocation resumes the process
   - Full conversation history is preserved and passed to the next invocation

✅ **6. Multi-turn Conversation Handling with Memory**
   - LangGraph's `MemorySaver` maintains conversation state across turns
   - Full message history is passed to all agents for context awareness
   - Clarity Agent uses both LLM and code fallback to infer company from previous messages
   - Example: After "Tell me about Apple", asking "What about the stock?" correctly infers Apple

✅ **7. At Least 2 Example Conversation Turns**
   - See "Example Conversation Flows" section below

✅ **8. Software Engineering Best Practices**
   - **Modular Agent Design**: Each agent is a separate class with a `run()` method
   - **Separation of Concerns**: State, workflow, agents, and utilities are in distinct modules
   - **Type Hints**: All functions use proper type annotations
   - **Documentation**: Docstrings and inline comments throughout
   - **Error Handling**: Try/catch blocks with meaningful fallbacks
   - **Configuration Management**: Centralized LLM factory (`llm_factory.py`)
   - **Clean Code**: Follows PEP 8 style guidelines

✅ **9. Instructions on How to Run**
   - See "Installation & Running" section below

✅ **10. Assumptions Documented**
   - See "Assumptions" section below

## Installation & Running

### Prerequisites
- **Python 3.9+**
- **Ollama** (with `gemma:latest` model)

### Setup Steps

1. **Install Ollama**:
   - Download from [ollama.com](https://ollama.com/)
   - Run `ollama pull gemma:latest`
   - Start Ollama server: `ollama serve`

2. **Install Python Dependencies**:
   ```bash
   pip install -r research_assistant/requirements.txt
   ```

3. **Run the Application**:
   ```bash
   streamlit run app.py --server.port 8501
   ```

4. **Access the UI**:
   - Open http://localhost:8501 in your browser
   - Start asking about companies!

## Example Conversation Flows

### Turn 1: Direct Company Query
```
User: "Tell me about Apple"

Flow:
1. Clarity Agent: ✓ Detects "Apple" explicitly → clarity_status = "clear", company_name = "Apple"
2. Research Agent: Fetches mock data for Apple
3. Validator Agent: Evaluates research → validation_result = "sufficient"
4. Synthesis Agent: Generates summary

Response: "Apple Inc. has recently launched Vision Pro, expanding services revenue. 
The stock is trading at $195, up 45% YTD. Key developments include AI integration 
across the product line."
```

### Turn 2: Follow-up Question (Context Inference)
```
User: "What is the latest news about their competitors?"

Flow:
1. Clarity Agent: ✗ No explicit company name, but fallback searches conversation history
   → Finds "Apple" from previous turn → clarity_status = "clear", company_name = "Apple"
2. Research Agent: Fetches Apple data again (same mock data)
3. Validator Agent: Validates research
4. Synthesis Agent: Generates updated summary focused on news

Response: (Continues context from Apple, providing latest news)
```

### Scenario 3: Clarification Request
```
User: "What's the latest news?"

Flow:
1. Clarity Agent: No company mentioned, no previous context 
   → clarity_status = "needs_clarification", company_name = null
2. Workflow ends, Streamlit app detects this

Response: "I'm not sure which company you're referring to. Could you please specify the company name?"

User: "Apple"

Flow: Continues as Turn 1 above
```

## Architecture Overview

```
┌──────────────────────────────────────────────────┐
│           Streamlit UI (app.py)                   │
│  - Chat interface with message history            │
│  - Session management (thread_id)                 │
│  - State debugging view                           │
└─────────────────┬──────────────────────────────────┘
                  │
                  ↓
┌──────────────────────────────────────────────────┐
│         LangGraph Workflow (workflow.py)          │
│  ┌──────────────────────────────────────────┐    │
│  │ Clarity Agent → Research → Validator     │    │
│  │                              ↓           │    │
│  │                           (sufficient?)  │    │
│  │                              ↓           │    │
│  │                         Synthesis → END  │    │
│  │                    ↑         ↓           │    │
│  │                    └─ (loop on insufficient) │
│  └──────────────────────────────────────────┘    │
│  - State: AgentState with all fields             │
│  - Memory: MemorySaver for multi-turn            │
│  - Routing: 3 conditional functions              │
└──────────────────────────────────────────────────┘
```

## Assumptions

1. **Local-Only Deployment**: This system is designed for local use with mock data; no external APIs or web search is performed.
2. **Mock Data Only**: Only "Apple" and "Tesla" companies are supported. Real-time financial data or news APIs are not integrated.
3. **LLM Reliability**: The gemma:latest model may not always infer context perfectly; code-level fallbacks are implemented for robustness.
4. **Conversation State**: The system assumes a single user session per thread_id. Multi-user scenarios would require thread management at the application level.
5. **Streamlit as Demo**: The Streamlit UI is intended for demonstration and evaluation, not production deployment.
6. **Recursion Limit**: The graph has a recursion limit of 50 to prevent infinite loops while allowing sufficient re-attempts.

## Testing

Unit tests verify the workflow logic without requiring a real LLM:
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)
.venv/bin/python research_assistant/tests/test_workflow.py
.venv/bin/python research_assistant/tests/test_context.py
```

**Test Coverage**:
- `test_workflow_clear_query`: Verifies full flow with explicit company
- `test_workflow_unclear_query`: Verifies interrupt mechanism
- `test_workflow_low_confidence_loop`: Verifies Validator → Research feedback loop
- `test_follow_up_question`: Verifies multi-turn context awareness

## Beyond Expected Deliverable

### 1. **Context Inference with Code Fallback**
   - ClarityAgent uses both LLM and code-level heuristics to infer company names
   - Automatically searches mock_data keys to match company names in user queries
   - Falls back to previous conversation messages to infer context for follow-up questions
   - Example: "What about the stock?" correctly infers the company from prior context

### 2. **Dual-Layer Clarity Detection**
   - **LLM Layer**: Uses gemma:latest to understand natural language queries
   - **Code Layer**: Direct string matching and fallback logic for reliability
   - Ensures that queries like "Tell me about Apple" are always recognized, even if the LLM fails

### 3. **Streamlit Interactive UI**
   - Modern chat interface with message history
   - Sidebar showing active agent status
   - Expandable "View Agent State" debug panel
   - Session management with persistent conversation history
   - Clear Chat button for reset functionality

### 4. **Production-Ready Error Handling**
   - Try/catch blocks around LLM invocations with graceful fallbacks
   - JSON parsing error recovery in all agents
   - Validation result defaults to "sufficient" after 3 attempts to prevent infinite loops

### 5. **Comprehensive State Management**
   - Full conversation history in `messages` field
   - Structured fields for clarity status, company name, research findings, confidence, and validation
   - Attempt counter to track feedback loop iterations
   - Enables advanced features like multi-turn context awareness

### 6. **Mock Data with Smart Matching**
   - Case-insensitive company name matching
   - Partial string matching (e.g., "Apple" matches "Apple Inc.")
   - Enables natural language queries without requiring exact company names

### 7. **Modular and Extensible Architecture**
   - Each agent is a standalone class with a `run(state)` method
   - Easy to extend with new agents or data sources
   - LLM factory pattern allows switching between different language models
   - State-based design supports adding new fields without changing agent logic

### 8. **Multi-turn Conversation with Context Memory**
   - LangGraph's MemorySaver maintains state across invocations
   - Full message history is passed to every agent for context awareness
   - Enables coherent follow-up questions like "What about the CEO?" or "Tell me more about their earnings"
   - Each turn builds on the previous context without losing information

---

**Built with**: LangGraph | LangChain | Ollama | Streamlit | Python 3.13

**For questions or improvements, see the inline code documentation or the project README.**


