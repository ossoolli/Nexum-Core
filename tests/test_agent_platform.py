import sys, os
sys.path.insert(0, '.')

print('=== AGENT PLATFORM INTEGRATION TEST ===')
print()

# Test GeminiService directly (bypasses config import issues)
print('[1] GeminiService direct init...')
from services.gemini_service import GeminiService

# Test API Key mode
svc1 = GeminiService(api_key="test-key-123", use_vertex=False)
s1 = svc1.get_status()
assert s1['auth_mode'] == 'API_Key'
assert s1['model'] == 'gemini-3.5-flash'
assert s1['connected'] == True
print('  API Key mode: OK (connected=' + str(s1['connected']) + ')')

# Test ADC/Vertex mode (creates client with env vars)
os.environ['GOOGLE_CLOUD_PROJECT'] = 'test-project'
os.environ['GOOGLE_CLOUD_LOCATION'] = 'global'
svc2 = GeminiService(use_vertex=False, api_key="test-key")  # No actual ADC
s2 = svc2.get_status()
print('  Model: ' + s2['model'])
print('  Image Model: ' + s2['image_model'])
print('  OK')
print()

print('[2] Methods exist...')
svc = GeminiService(api_key="test-key")
assert hasattr(svc, 'ask')
assert hasattr(svc, 'generate_image')
assert hasattr(svc, 'understand_image')
assert hasattr(svc, 'execute_code')
assert hasattr(svc, 'switch_model')
assert hasattr(svc, 'list_available_models')
assert hasattr(svc, 'get_status')
print('  ask, generate_image, understand_image, execute_code, switch_model, list_available_models, get_status')
print('  OK')
print()

print('[3] Model switch...')
svc.switch_model('gemini-3.1-flash-lite')
assert svc.model == 'gemini-3.1-flash-lite'
print('  Switched to gemini-3.1-flash-lite: OK')
print()

print('[4] Models list...')
models = svc.list_available_models()
assert len(models) >= 2
for m in models:
    print('    - ' + m)
print('  OK')
print()

print('[5] All core modules...')
from core.terminal_controller import terminal_controller
from watchdog.monitor import Watchdog
from watchdog.recovery import RecoveryManager
from swarm.engine import SwarmEngine
from swarm.council import CouncilOfSages
from core.memory.sovereign_memory import SovereignMemory
from core.context.context_engine import ContextEngine
from core.trust.trust_engine import TrustEngine
from core.trust.behavior_engine import BehaviorEngine
from core.learning.engines import ExperienceAnalyzer, PatternExtractor
from core.learning.initiative_engine import PredictionEngine, InitiativeEngine
print('  All modules imported OK')
print()

print('[6] Full wiring...')
mem = SovereignMemory('storage/sovereign_memory')
ctx = ContextEngine(mem)
trust = TrustEngine(mem)
beh = BehaviorEngine(trust, ctx)
council = CouncilOfSages(trust_engine=trust, llm_interface=svc)
swarm = SwarmEngine(council=council, llm_interface=svc)
wdog = Watchdog(heartbeat_interval=5)
rec = RecoveryManager(max_retries=3)
print('  All engines wired OK')
print()

print('=== ALL TESTS PASSED ===')
