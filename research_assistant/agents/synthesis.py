from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from research_assistant.graph.state import AgentState
import json

class SynthesisAgent:
    def __init__(self, llm):
        self.llm = llm

    def run(self, state: AgentState):
        """
        Creates a coherent summary.
        """
        findings = state.get("research_findings")
        company_name = state.get("company_name")
        query = state.get("query")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Synthesis Agent. specific. Create a professional, coherent summary of the research findings for {company_name}.
            Address the user's original query if possible, or provide a general overview if the query was broad.
            
            Findings: {findings}
            """),
            ("user", "{query}")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({"findings": json.dumps(findings), "company_name": company_name, "query": query})
        
        return {
            "messages": [AIMessage(content=response.content)],
            "summary": response.content
        }
