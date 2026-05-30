# التعامل مع وضع محاكاة GCP (Simulation Mode)

في Nexum-Core، صُممت الموصلات السحابية (`GCP Connector`) بمرونة عالية لمنع توقف النظام عند غياب المكتبات أو فشل الاتصال.

## الأعراض
تظهر رسائل خطأ في `err.log` مثل:
`[GCP Connector] Google Cloud SDK libraries not fully installed. Falling back to simulated mode.`
`cannot import name 'dialogflowcx_v3' from 'google.cloud'`

## لماذا يحدث هذا؟
- النظام يحاول استيراد وحدات Dialogflow CX و Discovery Engine.
- إذا لم تكن مكتبات `google-cloud-dialogflow` مثبتة، يفشل الاستيراد.
- الكود مصمم بـ `try-except` صلبة تجعل النظام ينتقل تلقائياً لـ "وضع المحاكاة" لضمان استمرارية العمل (Resiliency).

## متى يجب التدخل؟
- **وضع المحاكاة يعمل (Nominal):** لا يلزم اتخاذ أي إجراء إذا كانت المهام تعمل بشكل طبيعي في وضع المحاكاة.
- **تفعيل الوظائف السحابية الكاملة:** إذا كنت بحاجة للارتباط الفعلي بـ Vertex AI/Dialogflow، قم بتثبيت المكتبة الناقصة:
  `pip install google-cloud-dialogflow`
- **التأكد من الاعتمادات:** تأكد دائماً من وجود مسار ملف JSON الخاص بـ `service_account` في البيئة المحددة في `NexumSecurityConfig`.
