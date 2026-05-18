from core.agent_registry import agent_registry
from core.protocol_compiler import protocol_compiler
from core.sandbox import sandbox
from core.llm_factory import llm

class TaskOrchestrator:
    """
    Agent Task Orchestrator (NEXUM PRIME META-AGENT)
    يدير فريق الوكلاء، يوزع المهام وفقاً لبروتوكول العمل المُجمَّع (Compiled Protocol)،
    ويشرف على حلقة الـ Reflection والتصحيح الذاتي.
    """

    def execute_goal(self, goal: str):
        print(f"[ORCHESTRATOR] Received Global Objective: {goal}")
        
        # 1. Compile Protocol
        protocol = protocol_compiler.compile_workflow(goal)
        print(f"[ORCHESTRATOR] Compiled Protocol: {protocol['protocol_id']}")
        
        results = {}
        # 2. Traverse Graph
        for step in protocol['execution_graph']:
            agent_id = step['agent']
            action = step['action']
            print(f"[ORCHESTRATOR] Delegating step {step['step_id']} to {agent_id} for action {action}")
            
            # التحقق من قدرات الوكيل
            agent = agent_registry.get_agent(agent_id)
            if not agent:
                print(f"[ORCHESTRATOR] ERROR: Agent {agent_id} not globally registered!")
                break
                
            if action not in agent.get('capabilities', []):
                print(f"[ORCHESTRATOR] ERROR: Agent {agent_id} lacks capability {action}!")
                break
            
            # 3. Simulate Execution via LLM routing
            # In a real LangGraph setup, this invokes the specific LLM prompt for this agent.
            prompt = f"Executing {action} for goal: {goal}. Respond with execution strategy."
            res = llm.ask_specialist(f"[{agent['name']}] {prompt}") 
            results[step['step_id']] = {"status": "done", "agent": agent_id, "output": res}
            
            print(f"[ORCHESTRATOR] Step {step['step_id']} completed.")
            
        return {"objective": goal, "protocol": protocol, "results": results}

orchestrator = TaskOrchestrator()
