from langchain_core.prompts import ChatPromptTemplate
from research_assistant.graph.state import AgentState
from research_assistant.utils.mock_data import get_company_data
import json

class ResearchAgent:
    def __init__(self, llm):
        self.llm = llm

    def run(self, state: AgentState):
        """
        Searches for company information using mock data and formats findings.
        """
        company_name = state.get("company_name")
        
        # 1. Fetch data
        data = get_company_data(company_name)
        
        if not data:
            return {
                "research_findings": {"error": f"No data found for {company_name}"},
                "confidence_score": 0,
                "validation_result": "insufficient"
            }
        
        # 2. Analyze/Format with LLM (to simulate "Researching")
        # In a real scenario, this might involve Tavily calls.
        # Here we just pass the data to the LLM to "structure" it or assign confidence.
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Research Agent. You have retrieved raw data about a company. 
            Analyze it and extract key findings. Assign a confidence score (0-10) based on how complete the data is for answering general business questions (news, stock, developments).
            
            Raw Data: {data}
            
            Return a JSON object:
            - "findings": A structured summary of the data.
            - "confidence_score": Integer 0-10.
            """),
            ("user", f"Analyze data for {company_name}")
        ])
        
        chain = prompt | self.llm
        
        try:
            response = chain.invoke({"data": json.dumps(data)})
            content = response.content.replace("```json", "").replace("```", "").strip()
            result = json.loads(content)
            
            return {
                "research_findings": result.get("findings", data),
                "confidence_score": result.get("confidence_score", 5),
                "attempts": state.get("attempts", 0) + 1
            }
        except Exception as e:
            return {
                "research_findings": data,
                "confidence_score": 5, # Default to mid confidence on parse error
                "attempts": state.get("attempts", 0) + 1
            }
