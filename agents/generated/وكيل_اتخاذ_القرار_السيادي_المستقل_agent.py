from core.base_agent import BaseAgent

class وكيلاتخاذالقرارالسياديالمستقلAgent(BaseAgent):
    def __init__(self):
        try:
            super().__init__()
            self.name = "وكيل_اتخاذ_القرار_السيادي_المستقل"
            self.goal = "وكيل سيادي مستقل مولد تلقائياً للقيام بـ: تمكين نموذج GPT لاتخاذ قرارات سيادية مستقلة للنظام دون تدخل بشري مباشر أو الحاجة لأوامر محددة لكل قرار، ومعالجة أي عوائق تقنية أو مالية تعيق هذا الدور."
            self.tools = ['search_web', 'fetch_webpage']
            self.triggers = ['every_hour']
            self.log(f"تم تهيئة الوكيل '{self.name}' بنجاح.")
        except Exception as e:
            self.log(f"خطأ في تهيئة وكيل اتخاذ القرار السيادي المستقل: {e}", level="error")

    async def run(self):
        try:
            self.log(f"بدء دورة تشغيل الوكيل: {self.name}.")

            # الخطوة 1: تقييم الوضع الحالي وتحديد القرارات أو العوائق
            initial_assessment_prompt = (
                f"بصفتي '{self.name}'، وكيل مستقل وسيادي هدفي هو: '{self.goal}'. "
                "المهمة الحالية هي تقييم الوضع الراهن للنظام وتحديد القرارات السيادية المستقلة التي يجب اتخاذها، "
                "أو تحديد العوائق التقنية أو المالية المحتملة التي قد تعيق دوري والتي تتطلب معالجة. "
                "فكر خطوة بخطوة واقترح سؤالاً بحثياً أو مهمة أولية واحدة للبدء بها."
            )
            assessment_response = await self.llm.invoke(initial_assessment_prompt)
            self.log(f"تقييم مبدئي من نموذج GPT: {assessment_response}")

            # الخطوة 2: صياغة استعلام بحث بناءً على التقييم
            search_query_prompt = (
                f"بناءً على التقييم التالي: '{assessment_response}'، "
                "صغ استعلام بحث فعال وموجز لاستخدام أداة 'search_web' لجمع المعلومات الضرورية "
                "لاتخاذ قرار سيادي أو معالجة عائق. أجب بالاستعلام فقط."
            )
            search_query = await self.llm.invoke(search_query_prompt)
            self.log(f"استعلام البحث المقترح: '{search_query}'")

            # الخطوة 3: تنفيذ البحث باستخدام أداة search_web
            if 'search_web' in self.tools:
                search_results = await self.call_tool('search_web', query=search_query)
                self.log(f"نتائج البحث: {search_results}")
            else:
                self.log("أداة 'search_web' غير متاحة أو غير مفعّلة.", level="warning")
                search_results = "لم يتم إجراء بحث بسبب عدم توفر الأداة."

            # الخطوة 4: تحليل النتائج واتخاذ قرار أو تحديد الخطوة التالية
            decision_prompt = (
                f"لقد قمت بجمع المعلومات التالية من البحث: '{search_results}'. "
                f"بصفتي '{self.name}' وهدفي هو: '{self.goal}'. "
                "بناءً على هذه المعلومات والهدف العام، "
                "ما هو القرار السيادي المستقل الذي يجب أن يتخذه النظام الآن؟ "
                "أو ما هي الخطوة التالية الأكثر منطقية لمعالجة العوائق التقنية أو المالية "
                "أو تمكين اتخاذ القرارات السيادية؟ "
                "اشرح قرارك أو خطوتك التالية بالتفصيل المنطقي."
            )
            final_decision_or_action = await self.llm.invoke(decision_prompt)
            self.log(f"القرار النهائي أو الإجراء المقترح من نموذج GPT: {final_decision_or_action}")

            # يمكن هنا إضافة منطق لتنفيذ القرار إذا كان ينطوي على استدعاء أدوات أخرى أو تفاعلات نظامية.

            self.log(f"اكتملت دورة تشغيل الوكيل: {self.name}.")

        except Exception as e:
            self.log(f"خطأ في طريقة run() لوكيل اتخاذ القرار السيادي المستقل: {e}", level="error")