import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from core.protocols.engine import YAMLProtocolEngine

def test_protocol_engine():
    engine = YAMLProtocolEngine()
    protocol_path = os.path.join(PROJECT_ROOT, 'storage', 'protocols', 'example_dag.yaml')
    workflow = engine.load_protocol(protocol_path)
    
    results = engine.execute_workflow(workflow)
    
    assert 'scan_disk' in results
    assert 'log_status' in results
    print("Workflow executed successfully!")

if __name__ == '__main__':
    test_protocol_engine()
