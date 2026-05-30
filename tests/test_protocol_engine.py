import sys
import os
sys.path.append('/home/madarmutaz/Nexum-Core')

from core.protocols.engine import YAMLProtocolEngine

def test_protocol_engine():
    engine = YAMLProtocolEngine()
    protocol_path = '/home/madarmutaz/Nexum-Core/storage/protocols/example_dag.yaml'
    workflow = engine.load_protocol(protocol_path)
    
    results = engine.execute_workflow(workflow)
    
    assert 'scan_disk' in results
    assert 'log_status' in results
    print("Workflow executed successfully!")

if __name__ == '__main__':
    test_protocol_engine()
