from core.learning.self_correction import AssistedDebuggingLoop
from core.sandbox import SandboxRuntime

with open('tests/test_terminal_controller.py', 'r') as f:
    script_content = f.read()

loop = AssistedDebuggingLoop()
report = loop.execute_debugging_flow('HERMES_AGENT', script_content, 'tests/test_terminal_controller.py')
print(report['report'])
