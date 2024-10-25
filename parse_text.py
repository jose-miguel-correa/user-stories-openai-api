
class textProcess:
    def __init__(self) -> None:
        pass

    def parse_input(self, text):
        # Remove formatting asterisks
        text = text.replace("**", "").replace("-", "").strip()

        # Splits the text into segments
        lines = text.split('\n')
        
        # Initialize variables for "Característica" and "Contexto"
        caracteristica = ""
        contexto = ""
        
        # Capture scenarios in a dictionary
        scenarios = {}
        
        current_scenario = ""
        current_actions = ""
        in_actions = False
        
        for line in lines:
            stripped_line = line.strip()
            
            if stripped_line.startswith("Característica"):
                caracteristica = stripped_line.split(": ", 1)[1].strip()
            
            elif stripped_line.startswith("Contexto"):
                contexto = stripped_line.split(": ", 1)[1].strip()
            
            elif stripped_line.startswith("Escenario"):
                if current_scenario and current_actions:
                    scenarios[current_scenario] = current_actions.strip()
                
                current_scenario = stripped_line.split(": ", 1)[1].strip()
                current_scenario = f"Escenario {len(scenarios) + 1}: {current_scenario}"
                current_actions = ""
                in_actions = True
            
            elif in_actions:
                current_actions += stripped_line + "\n"
        
        if current_scenario and current_actions:
            scenarios[current_scenario] = current_actions.strip()
        
        return caracteristica, contexto, scenarios

    def generate_subtask_payloads(self, scenarios, task_key):
        subtask_payloads = []
        for scenario_desc, actions in scenarios.items():
            subtask_payloads.append({
                "fields": {
                    "project": {
                        "key": "US2"  # Replace with actual project key as needed
                    },
                    "parent": {
                        "key": task_key  # The main task key
                    },
                    "summary": scenario_desc,
                    "description": actions,
                    "issuetype": {
                        "name": "Subtask"  # Subtask type
                    }
                }
            })
        return subtask_payloads
