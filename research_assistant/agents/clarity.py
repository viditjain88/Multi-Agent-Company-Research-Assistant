from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage
from research_assistant.graph.state import AgentState
import json

class ClarityAgent:
    def __init__(self, llm):
        self.llm = llm

    def run(self, state: AgentState):
        """
        Analyzes the user's query to determine if it's clear and specific.
        """
        messages = state["messages"]
        last_message = messages[-1]
        query = last_message.content

        # Improved prompt: explicitly instruct LLM to look at previous user messages for company name
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
You are a Clarity Agent. Your job is to check if the user's query is clear and mentions a specific company name, OR if the company is clear from the conversation context.

If the current user message does NOT mention a company, look at previous user messages in the conversation history and use the most recent company mentioned as context. Only return 'needs_clarification' if you cannot infer a company from any previous user message.

Return a JSON object with the following fields:
- "clarity_status": "clear" or "needs_clarification"
- "company_name": The name of the company if found or inferred from context, or null if not found.
- "reason": A brief explanation.

Examples:
User: "Tell me about Apple"
Output: {"clarity_status": "clear", "company_name": "Apple", "reason": "Company explicitly named."}

User: "How is the stock doing?" (With no prior context)
Output: {"clarity_status": "needs_clarification", "company_name": null, "reason": "No company specified."}

User: "Analyze Tesla's recent news" -> AI: "Sure..." -> User: "What about the stock?"
Output: {"clarity_status": "clear", "company_name": "Tesla", "reason": "Inferred from previous turn."}
"""),
            MessagesPlaceholder(variable_name="messages"),
        ])

        chain = prompt | self.llm
        from research_assistant.utils.mock_data import mock_research
        # 1. Check latest user message for a known company
        found_company = None
        for cname in mock_research.keys():
            if cname.lower() in query.lower():
                found_company = cname
                break
        if found_company:
            return {
                "clarity_status": "clear",
                "company_name": found_company,
                "query": query
            }
        # 2. Otherwise, try LLM
        try:
            response = chain.invoke({"messages": messages})
            content = response.content
            content = content.replace("```json", "").replace("```", "").strip()
            result = json.loads(content)
            clarity_status = result.get("clarity_status", "needs_clarification")
            company_name = result.get("company_name")
            # 3. Fallback: If LLM fails, search previous user messages for a company
            if clarity_status == "needs_clarification" or not company_name:
                for msg in reversed(messages[:-1]):
                    if hasattr(msg, "content") and isinstance(msg, HumanMessage):
                        for cname in mock_research.keys():
                            if cname.lower() in msg.content.lower():
                                company_name = cname
                                clarity_status = "clear"
                                break
                        if clarity_status == "clear":
                            break
            return {
                "clarity_status": clarity_status,
                "company_name": company_name,
                "query": query
            }
        except Exception as e:
            # Fallback: try to infer from previous user messages
            company_name = None
            for msg in reversed(messages[:-1]):
                if hasattr(msg, "content") and isinstance(msg, HumanMessage):
                    for cname in mock_research.keys():
                        if cname.lower() in msg.content.lower():
                            company_name = cname
                            break
                    if company_name:
                        break
            return {
                "clarity_status": "clear" if company_name else "needs_clarification",
                "company_name": company_name,
                "query": query
            }
