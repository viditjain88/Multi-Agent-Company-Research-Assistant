from langchain_core.prompts import ChatPromptTemplate
from research_assistant.graph.state import AgentState
import json

class ValidatorAgent:
    def __init__(self, llm):
        self.llm = llm

    def run(self, state: AgentState):
        """
        Reviews research quality and completeness.
        """
        findings = state.get("research_findings")
        confidence = state.get("confidence_score", 0)
        
        # If confidence is already high from Research Agent, we might just agree.
        # But let's verify if the findings actually answer the user's implicit intent (general info).
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Validator Agent. Review the research findings.
            
            Findings: {findings}
            Current Confidence: {confidence}
            
            Is this information sufficient to provide a comprehensive summary? 
            Return JSON:
            - "validation_result": "sufficient" or "insufficient"
            - "feedback": If insufficient, what is missing? (Optional)
            """),
            ("user", "Validate research.")
        ])
        
        chain = prompt | self.llm
        
        try:
            response = chain.invoke({"findings": json.dumps(findings), "confidence": confidence})
            content = response.content.replace("```json", "").replace("```", "").strip()
            result = json.loads(content)
            
            return {
                "validation_result": result.get("validation_result", "insufficient")
            }
        except Exception:
            # Fallback based on confidence score provided by Research Agent
            return {
                "validation_result": "sufficient" if confidence >= 6 else "insufficient"
            }
