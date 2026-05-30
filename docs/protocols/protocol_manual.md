# دليل بروتوكولات التشغيل السيادية لنظام NEXUM-CORE OS (v12.0.0+)
## المرجع الفني الشامل للمهندسين والوكلاء المستقلين

نظام **Nexum-Core** هو نظام تشغيل سيادي قائم على الوكلاء المستقلين (Sovereign Agentic OS). يعتمد النظام في عملياته الداخلية وتكامله الخارجي على شبكة من البروتوكولات المترابطة التي تضمن الحماية، الموثوقية، والتوافق الذاتي (Self-Healing). 

يقدم هذا الدليل تحليلاً فائق الدقة لكل بروتوكول من البروتوكولات الخمسة الأساسية في النظام، مقارنتها بمعايير الصناعة العالمية، طرق عملها البرمجي، وكيفية توظيفها بشكل احترافي.

---

### 1. بروتوكول مسارات العمل ومخططات التنفيذ (YAML DSL & YAMLProtocolEngine)
* **اسم الفئة البرمجية:** `YAMLProtocolEngine` و `ProtocolDSLEngine`
* **المسار في المشروع:** `core/protocols/engine.py` و `core/protocols/dsl/yaml_parser.py`

#### 💡 المفهوم المعياري في الصناعة (Industry Concept)
يعتمد هذا البروتوكول على مفهوم **مخططات التوجيه غير الحلقية (Directed Acyclic Graphs - DAGs)**، وهو نفس النموذج المستخدم في أدوات أتمتة البيانات الكبرى وهندسة البرمجيات مثل **Apache Airflow** و **LangGraph** و **Prefect**. يتيح هذا النموذج تقسيم المهام المعقدة إلى خطوات تتابعية أو متوازية، مع تتبع التبعيات (Dependencies) والمدخلات والمخرجات لكل خطوة بدقة متناهية.

#### ⚙️ آلية العمل البرمجية في Nexum-Core
1. **التحليل الفني (DSL Parsing):** يقوم `ProtocolDSLEngine` بتحليل ملفات التكوين بصيغة YAML والتحقق من احتوائها على العناصر الأساسية (`trigger`, `agents`, `retry`, `rollback`, `steps`).
2. **استبدال المتغيرات الديناميكي:** يمتلك محرك `YAMLProtocolEngine` نظاماً ذكياً لاستبدال المتغيرات بين الخطوات باستخدام النمط `{{variable_name}}` (Variable Substitution). على سبيل المثال، يمكن تمرير مخرجات `step_1` لتصبح مدخلات لـ `step_2` عبر المتغير `result_step_1`.
3. **التنفيذ السيادي المعزول:** يتم تمرير كل أمر تنفيذي عبر بوابة الحماية السيادية `SovereignExecutionGateway` لضمان عدم حقن الأوامر الخبيثة وحظر العمليات غير المصرح بها خارج نطاق النظام.

#### 🎯 الاستخدامات والتوظيف الاحترافي
* **أتمتة عمليات الصيانة الذاتية:** فحص الخادم، تشغيل النسخ الاحتياطية المشفرة، وترحيل السجلات.
* **إطلاق مسارات التطوير المستمر (CI/CD Pipelines):** بناء الأكواد وفحص الثغرات الأمنية وإجراء الاختبارات التلقائية قبل الدمج.
* **سيناريوهات التراجع عند الفشل (Rollback Policies):** تنفيذ بروتوكول إلغاء التغييرات واستعادة الحالة المستقرة تلقائياً في حال فشل أي خطوة حرجة.

#### 💻 مثال عملي للتوظيف (YAML Schema & Execution)
##### ملف التكوين (`storage/protocols/backup_and_audit.yaml`):
```yaml
protocol:
  trigger: scheduled
  schedule: "0 0 * * *"
  agents:
    - sentinel_agent
  retry: 3
  rollback: true
  steps:
    collect_logs:
      command: "tar -czf /tmp/logs_backup.tar.gz /home/madarmutaz/Nexum-Core/storage/logs/"
    encrypt_backup:
      command: "gpg --symmetric --batch --yes --passphrase-file /home/madarmutaz/.secret_key /tmp/logs_backup.tar.gz"
    verify_encryption:
      command: "ls /tmp/logs_backup.tar.gz.gpg"
```

##### تشغيل البروتوكول برمجياً:
```python
import sys
sys.path.insert(0, '/home/madarmutaz/Nexum-Core')
from core.protocols.engine import YAMLProtocolEngine

engine = YAMLProtocolEngine()
# تحميل وتشغيل البروتوكول
protocol_data = engine.load_protocol('/home/madarmutaz/Nexum-Core/storage/protocols/backup_and_audit.yaml')
results = engine.execute_workflow(protocol_data)
print("نتائج تنفيذ البروتوكول:", results)
```

---

### 2. بروتوكول التواصل الفيدرالي للبوتات المساعدة (Inter-Bot Protocol)
* **اسم الفئة البرمجية:** `InterBotProtocol` و `BotManifest`
* **المسار في المشروع:** `core/inter_bot_protocol.py`

#### 💡 المفهوم المعياري في الصناعة (Industry Concept)
يمثل هذا البروتوكول بنية **أوركسترا الخدمات المصغرة (Microservices Orchestration)** وإدارة العمليات المعزولة (Daemon / Process Management) الشبيهة بـ **Kubernetes Control Plane** ولكن على مستوى العمليات المحلية (Local OS Processes). يستخدم بروتوكول التواصل مع البوتات واجهات البرمجة **HTTP REST APIs** لتبادل الأوامر والتحقق من نبضات القلب (Heartbeat) والمطابقة المعمارية.

#### ⚙️ آلية العمل البرمجية في Nexum-Core
1. **السجل المركزي للخدمات (Service Registry):** يسجل كل بوت مساعد قدراته، والمسار الفيزيائي لملفاته، ومنفذ الاتصال (Port)، والتوكين الأمني في ملف `registry.json`.
2. **إدارة دورة حياة العمليات (Process Lifecycle):** يقوم بروتوكول `InterBotProtocol` ببدء العمليات كجلسات منفصلة في الخلفية باستخدام `subprocess.Popen` بمعزل عن العملية الرئيسية لنظام نيكسوم، ويتتبع حالتها عبر معرف العملية الرقمي (PID).
3. **التواصل الآمن عبر المنافذ:** يتم إرسال الأوامر للبوتات الفرعية عبر بروتوكول HTTP POST مشفر وموجه للمسار `/nexum/command` بحمولة مهيكلة تحتوي على الأوامر والبيانات وتوقيع المصدر.

#### 🎯 الاستخدامات والتوظيف الاحترافي
* **توزيع الأحمال البرمجية:** إسناد المهام الثقيلة (مثل تلخيص قنوات التليجرام أو معالجة الصور) إلى بوت مساعد مخصص (مثل `telegram-summarizer-bot`) لتجنب عرقلة استجابة النظام الرئيسي.
* **البناء الديناميكي للبوتات (Dynamic Code Generation):** توليد قوالب برمجية لبوتات فرعية جديدة وتجهيزها للاستماع التلقائي بمجرد تزايد الحاجة لقدرات جديدة.

#### 💻 مثال عملي للتوظيف (Register & Dispatch)
##### تسجيل وتشغيل بوت فرعي جديد:
```python
import sys
sys.path.insert(0, '/home/madarmutaz/Nexum-Core')
from core.inter_bot_protocol import InterBotProtocol

ibp = InterBotProtocol()

# تعريف الهيكل المعماري للبوت الفرعي (Manifest)
bot_manifest = {
    "name": "data_cleaner_bot",
    "path": "/home/madarmutaz/Nexum-Core/bots/data_cleaner.py",
    "port": 8085,
    "telegram_token": "765432109:ABCdefGhI...",
    "capabilities": ["database_cleanup", "log_pruning"],
    "status": "stopped"
}

# 1. تسجيل البوت في النظام
ibp.register_bot(bot_manifest)

# 2. بدء التشغيل في الخلفية
launch_result = ibp.start_bot("data_cleaner_bot")
print("حالة تشغيل البوت:", launch_result)

# 3. إرسال أمر تشغيلي للبوت المساعد
response = ibp.send_command("data_cleaner_bot", "prune_old_records", {"days_threshold": 30})
print("استجابة البوت الفرعي للطلب:", response)
```

---

### 3. بروتوكول تداول ونقاش مجلس الحكماء (CouncilDebateProtocol)
* **اسم الفئة البرمجية:** `CouncilDebateProtocol`
* **المسار في المشروع:** `council/debate_protocol.py`

#### 💡 المفهوم المعياري في الصناعة (Industry Concept)
يندرج هذا البروتوكول تحت تصنيف **مصفوفات التوافق متعددة الوكلاء (Multi-Agent Consensus & Debate Architectures)** وأبحاث الذكاء الاصطناعي المتقدمة مثل **Society of Mind** و **Self-Collaboration for Error Reduction**. يحل هذا النموذج مشكلة "الهلوسة" الفردية للنماذج اللغوية الكبيرة عبر إنشاء دورات نقاش واعتراض برمجية محكمة، مماثلة لأنظمة التصويت والأغلبية الحاكمة في معمارية الموزعات الأمنية (e.g., Byzantine Fault Tolerance).

#### ⚙️ آلية العمل البرمجية في Nexum-Core
1. **التصويت المبدئي الإجباري:** يطرح النظام المهمة البرمجية الحساسة على 3 حكماء (نماذج ذكاء اصطناعي مختلفة مثل Gemini و Claude وغيرها). إذا صوت الجميع بالموافقة (Unanimous 3/3)، تمر المهمة فوراً بتقدير توافق `AAA Unanimous`.
2. **جولة دحض الاعتراض (Dissent Evaluation):** في حال وجود معترض واحد (2 موافق ضد 1 معترض)، يبدأ بروتوكول النقاش الذاتي. يتم جلب حجة المعترض التفصيلية وصياغتها برمجياً كـ `Reconsideration Prompt` وإرسالها للموافقين لإعادة تقييم موافقتهم.
3. **جولة المحاكمة النهائية (Sages Convincing):** في حال تمسك الموافقين برأيهم ودفاعهم عنه، يتم تجميع حججهم الفنية وإعادتها للمعترض في محاولة لإقناعه بالموافقة المشروطة بضمانات أمنية (Conditional Safeguards). إذا اقتنع المعترض أو حافظ الموافقون على الأغلبية (2/3)، تصدر رخصة التنفيذ بتقدير توافق `A Consensus`؛ وإلا يتم إلغاء المهمة وحظرها تماماً كإجراء حمائي فائق.

#### 🎯 الاستخدامات والتوظيف الاحترافي
* **بوابات العبور الأمنية للكود الفعلي (Gatekeeping):** عدم السماح بتطبيق أي تعديل برمجي أو أمر طرفي حساس (مثل حذف ملف أو تغيير إعداد سحابي) إلا بترخيص رقمي صادر من مجلس الحكماء ومصدق عبر بروتوكول النقاش والتوافق.
* **فحص الثغرات الحرجة في الوقت الفعلي:** تدقيق كفاءة السكربتات والتصدي لمحاولات الاختراق وحقن التعليمات البرمجية.

#### 💻 مثال عملي للتوظيف (Simulated Debate Execution)
```python
# محاكاة لدورة نقاش مجلس الحكماء عند اتخاذ قرار مصيري
import asyncio
import logging
from council.debate_protocol import CouncilDebateProtocol

# إعداد السجلات لمشاهدة تفاصيل النقاش
logging.basicConfig(level=logging.INFO)

class MockConsensusEngine:
    async def _ask_sage_by_id(self, sage_id: str, prompt: str) -> str:
        if sage_id == "sage_1":
            return "APPROVED: I reviewed the code and the dependencies. It's fully safe and complies with HMAC protocols."
        return "APPROVED: Agree with Sage 1. Standard library used, zero network exposure."

    def _extract_vote(self, response: str) -> bool:
        return "APPROVED" in response

    async def _merge_deliberation(self, task: str, reasoning: dict) -> str:
        return "Compiled Consensus: Safe script deployment authorized."

# تشغيل نقاش محاكى
async def run_simulation():
    engine_mock = MockConsensusEngine()
    debate_protocol = CouncilDebateProtocol(engine_mock)
    
    task_description = "Deploy PM2 self-healing auto-restart script"
    initial_reasoning = {
        "sage_1": "Objection! Standard script could cause infinite restart loops if node crash isn't caught.",
        "sage_2": "APPROVED: Crucial for self-healing, improves system uptime.",
        "sage_3": "APPROVED: High-priority requirement from sovereign logs."
    }
    initial_votes = {
        "sage_1": False, # معترض
        "sage_2": True,  # موافق
        "sage_3": True   # موافق
    }
    
    token = await debate_protocol.debate(task_description, initial_reasoning, initial_votes)
    print("Consensus Approved Status:", token.approved)
    print("Consensus Quality Grade:", token.consensus_grade)
    print("Merged Action Output:", token.merged_output)

# لتشغيل المحاكاة:
# asyncio.run(run_simulation())
```

---

### 4. بروتوكول مترجم مسارات العمل (ProtocolCompiler)
* **اسم الفئة البرمجية:** `ProtocolCompiler`
* **المسار في المشروع:** `core/protocol_compiler.py`

#### 💡 المفهوم المعياري في الصناعة (Industry Concept)
يعمل مترجم البروتوكولات بآلية **البرمجة التعريفية (Declarative Programming)** والترجمة الهيكلية (Abstract Syntax Trees - AST translation). يشبه في آلية عمله مترجمات الأكواد الحديثة وأدوات تحويل المخططات الفنية إلى هياكل تحتية (IaC Compiler) مثل **Terraform Compiler** و **LLVM Frontend compiler**، حيث يقوم باستلام أهداف عامة غير مهيكلة ويترجمها إلى تسلسل مهام وعلاقات رياضية منطقية قابلة للفهم من قبل محركات التشغيل.

#### ⚙️ آلية العمل البرمجية في Nexum-Core
1. **استخلاص الأهداف (Semantic Extraction):** يستلم المترجم النص البشري للهدف (Task Objective) ويحلل السياق اللغوي والدلالي لمعرفة الأصول المستهدفة (مثل ملفات، مستودع GitHub، قواعد بيانات، خوادم سحابية).
2. **التحليل الشبكي للتبعيات:** بناءً على طبيعة المهمة، يقوم بتجهيز "عقد" (Nodes) العمليات والوكلاء المسؤولين (مثلاً: `architect_agent` لتصميم المعمارية، متبوعاً بـ `frontend_agent` للبناء، ثم `infra_agent` للنشر).
3. **إنشاء مخطط التحكيم (Orchestration Graph):** يربط المترجم العقد ببعضها بعلاقات اعتمادية صريحة (`depends_on`) لضمان عدم بدء تشغيل أي خطوة قبل اكتمال وتدقيق مدخلاتها السابقة، ويصدر كائن البروتوكول المجمع بحالة `compiled`.

#### 🎯 الاستخدامات والتوظيف الاحترافي
* **بناء البرمجيات من الصفر عبر الأوامر النصية:** تحويل طلبات المستخدم في التليجرام (مثل "أنشئ لي تطبيق متجر سحابي كامل") إلى سلسلة مهام دقيقة توزع على الوكلاء المختصين بالتصميم والكود والنشر التلقائي.
* **إعادة التكوين الذاتي للنظام (Self-Adaptation):** إعادة ترتيب أولويات عمليات الترقيع الأمني بناءً على قنوات الاتصال والتهديدات المستكشفة.

#### 💻 مثال عملي للتوظيف (Task Graph Compilation)
```python
import sys
sys.path.insert(0, '/home/madarmutaz/Nexum-Core')
from core.protocol_compiler import protocol_compiler

# استدعاء المترجم لتحويل هدف معقد إلى مسار عمل مجمع (DAG)
objective = "Build and deploy a React dashboard on GCP and configure GitHub Actions."
compiled_graph = protocol_compiler.compile_workflow(objective)

print(f"اسم البروتوكول المولد: {compiled_graph['protocol_id']}")
print(f"الهدف الرئيسي: {compiled_graph['objective']}")
print(f"حالة البروتوكول: {compiled_graph['status']}")
print("مخطط العلاقات والخطوات المولدة:")
for step in compiled_graph["execution_graph"]:
    print(f" - خطوة {step['step_id']}: يقوم الوكيل ({step['agent']}) بـ ({step['action']}) [يعتمد على خطوات سابقة: {step.get('depends_on', 'لا يوجد')}]")
```

---

### 5. بروتوكول عقود الوكلاء والربط بالأحداث (AgentContract & ProtocolBridge)
* **اسم الفئة البرمجية:** `AgentEvent`, `AgentContractValidator`, `ProtocolBridgeAgent`
* **المسار في المشروع:** `protocols/agent_contract.py` و `agents/protocol_bridge.py`
* **ملف البروتو المعياري:** `protocols/agent_contract.proto`

#### 💡 المفهوم المعياري في الصناعة (Industry Concept)
يمثل هذا البروتوكول تطبيقاً صارماً لـ **بنية النظم المعتمدة على الأحداث (Event-Driven Architecture - EDA)** وحيازة مخططات البيانات الصارمة (Schema-Driven Communication) باستخدام **Google Protocol Buffers (Protobuf)** وعقود أحداث السحابة المعيارية **CloudEvents Specification**. يضمن هذا التوافق نقل البيانات الثنائية بأعلى سرعة وبأقل حجم من استهلاك الذاكرة وحزم الشبكة عبر تفعيل قنوات النشر والاشتراك (Pub/Sub) المستقرة مثل **Redis** و **Apache Kafka**.

#### ⚙️ آلية العمل البرمجية في Nexum-Core
1. **عقد الحدث الموحد (AgentEvent Contract):** يتم تغليف كل حدث محلي أو إشارة اتصال داخل كائن `AgentEvent` الذي يحافظ على هيكل آمن يحتوي على (`event_id`, `sender`, `timestamp`, `topic`, `payload`).
2. **التشفير والترميز الثنائي الفائق:** يتم ترميز وتعبئة الحمولة المعقدة كأكواد ثنائية آمنة (Binary-safe base64 encoding) لضمان عدم تلف الملفات التنفيذية أو نصوص البرمجة أثناء عبور قنوات النشر والمستقبلات.
3. **جسر التكامل الخارجي (ProtocolBridge):** يقوم `ProtocolBridgeAgent` بربط نظام نيكسوم بشبكة Redis المحلية أو السحابية، ويوفر ميثود `publish_event` لنشر الأحداث، وميثود `call_webhook` لإرسال إشارات الاستدعاء المرتدة (Callbacks) بنمط غير متزامن فائق الكفاءة.
4. **التدقيق الصارم للمطابقة (Contract Validation):** يتحقق موديول `AgentContractValidator` من صحة البيانات الواردة ومطابقتها التامة للميتا داتا الإجبارية قبل السماح بمرورها للذاكرة أو محرك التنفيذ، مما يمنع حقن البيانات المشوهة.

#### 🎯 الاستخدامات والتوظيف الاحترافي
* **نظام التنبيهات الفوري العابر للقنوات (Cross-Channel Notification):** نشر إشارات فورية عند تعثر أي تطبيق في PM2 لتقوم البوتات الفرعية بالتقاط الإشارة وترجمتها فوراً وإرسال إشعار لقناة السجلات السيادية.
* **بناء الأنظمة الموزعة (Distributed Agents Networks):** تمكين عدة وكلاء مستضافين على خوادم مختلفة من التعاون الفوري وتبادل المخرجات عبر قنوات Redis المشتركة بشكل منسق وآمن تماماً.

#### 💻 مثال عملي للتوظيف (Publishing Contract Event)
```python
import sys
import asyncio
sys.path.insert(0, '/home/madarmutaz/Nexum-Core')
from agents.protocol_bridge import protocol_bridge

# نشر حدث سيادي عند اكتمال عملية الترميم التلقائي بنجاح
system_payload = {
    "status": "restored",
    "service": "telegram-summarizer-bot",
    "pm2_id": 4,
    "healing_action": "Memory flush and process cold-restart",
    "timestamp": "2026-05-30T10:00:00Z"
}

# نشر الحدث عبر جسر البروتوكولات على قناة "sentinel_events"
result = protocol_bridge.publish_event(
    channel="sentinel_events",
    payload=system_payload
)

print(result)

# استدعاء Webhook خارجي لإعلام واجهة تحكم بعيدة
async def notify_external_dashboard():
    webhook_url = "https://external-console.ossoolli.com/api/v1/event_receiver"
    response = await protocol_bridge.call_webhook(webhook_url, {"event": "self_healing_success", "payload": system_payload})
    print(response)

# لتشغيل الاستدعاء غير المتزامن:
# asyncio.run(notify_external_dashboard())
```

---

## 🔱 الاندماج والدوام في الذاكرة السيادية
لضمان قيام نظام **Nexum-Core** ووكلاؤه و**Hermes** باستحضار واستخدام هذه البروتوكولات باحترافية وبدون أي أخطاء، تم:
1. **أرشفة وحفظ هذا المرجع** بشكل دائم في الذاكرة السيادية المشتركة لتكون مرجعاً دائماً لمحركات الاسترجاع المعرفي (FTS5 Recall Engines).
2. **برمجة السلوك التلقائي:** يتم استيراد العقود واستخدام المصادقات الثنائية وقواعد التصويت في مجلس الحكماء تلقائياً في كل مرة يطلب فيها المطور معتز تنفيذ مهام برمجية أو عملياتية جديدة.
