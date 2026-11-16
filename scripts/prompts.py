"""Prompt templates used by the ArtECulture release code."""

EMOTIONS = [
    "amusement", "awe", "contentment", "excitement", "anger",
    "disgust", "fear", "sadness", "something else",
]


EMOTION_LABELS = {
    "english": {emotion: emotion for emotion in EMOTIONS},
    "chinese": {
        "amusement": "好笑", "awe": "惊叹", "contentment": "满足",
        "excitement": "兴奋", "anger": "愤怒", "disgust": "嫌恶",
        "fear": "恐惧", "sadness": "伤感", "something else": "其它情感",
    },
    "arabic": {
        "amusement": "المتعة", "awe": "الذهول", "contentment": "الرضا",
        "excitement": "الحماس", "anger": "الغضب", "disgust": "الاشمئزاز",
        "fear": "الخوف", "sadness": "الحزن", "something else": "أخرى",
    },
}

ZERO_SHOT_PROMPTS = {
    "english": """You are interpreting emotions from an English-speaking cultural perspective. Look at this artwork and identify the single emotion it evokes, then briefly explain why.

Choose exactly one emotion from: amusement, awe, contentment, excitement, anger, disgust, fear, sadness, something else.

Return exactly:
Emotion: <emotion>
Explanation: <brief explanation>""",
    "chinese": """请从中文文化视角理解情感。观察这件艺术作品，判断它唤起的一种主要情感，并简要说明原因。

请仅从以下情感中选择一项：好笑、惊叹、满意/满足、兴奋、愤怒、嫌恶、恐惧、伤感、其它情感。

请严格按以下格式回答：
情感：<情感>
解释：<简短解释>""",
    "arabic": """فسّر المشاعر من منظور ثقافي ناطق بالعربية. انظر إلى هذا العمل الفني وحدد شعورًا واحدًا يثيره، ثم اشرح السبب بإيجاز.

اختر شعورًا واحدًا فقط من: المتعة، الذهول، الرضا، الحماس، الغضب، الاشمئزاز، الخوف، الحزن، أخرى.

أجب بالصيغة التالية فقط:
الشعور: <الشعور>
التفسير: <تفسير موجز>""",
}

RATIONALE_GENERATION_PROMPTS = {
    "english": """For the visual concept {concept}, use the following emotion distribution from English-speaking viewers: {emotion_distribution}. Identify the dominant emotion and provide concise cultural rationales explaining why this concept is associated with that emotion in this culture.

Return JSON only:
{{"dominant_emotion": "<emotion>", "rationales": ["<rationale>"]}}""",
    "chinese": """对于视觉概念“{concept}”，请依据中文文化群体的以下情感分布：{emotion_distribution}。确定占主导地位的情感，并给出简洁的文化解释，说明该概念为何在这一文化中与该情感相关。

请仅返回 JSON：
{{"dominant_emotion": "<情感>", "rationales": ["<解释>"]}}""",
    "arabic": """بالنسبة إلى المفهوم البصري «{concept}»، استخدم توزيع المشاعر الآتي لدى الناطقين بالعربية: {emotion_distribution}. حدّد الشعور الغالب وقدّم تفسيرات ثقافية موجزة توضّح سبب ارتباط هذا المفهوم بذلك الشعور في هذه الثقافة.

أعد JSON فقط:
{{"dominant_emotion": "<الشعور>", "rationales": ["<التفسير>"]}}""",
}

REVERSE_VALIDATION_PROMPTS = {
    "english": """Infer the single underlying emotion explained by the following rationale set:

{rationales}

Choose exactly one label from: amusement, awe, contentment, excitement, anger, disgust, fear, sadness, something else.
Return the label only.""",
    "chinese": """请根据以下解释推断其对应的一种主要情感：

{rationales}

请仅从以下标签中选择一项：好笑、惊叹、满意/满足、兴奋、愤怒、嫌恶、恐惧、伤感、其它情感。
只返回情感标签。""",
    "arabic": """استنتج شعورًا واحدًا تشرحه مجموعة التفسيرات الآتية:

{rationales}

اختر تسمية واحدة فقط من: المتعة، الذهول، الرضا، الحماس، الغضب، الاشمئزاز، الخوف، الحزن، أخرى.
أعد تسمية الشعور فقط.""",
}

RETRIEVAL_PROMPTS = {
    "english": """Interpret the artwork from an English-speaking cultural perspective. Relevant culture-specific knowledge retrieved for visible concepts is provided below:

{retrieved_tuples}

Using the artwork and this knowledge, identify the single emotion the artwork evokes and briefly explain why. If no knowledge is provided, rely on the artwork alone.

Choose exactly one emotion from: amusement, awe, contentment, excitement, anger, disgust, fear, sadness, something else.
Return exactly:
Emotion: <emotion>
Explanation: <brief explanation>""",
    "chinese": """请从中文文化视角理解这件艺术作品。以下是针对画面中可见概念检索到的相关文化知识：

{retrieved_tuples}

请结合艺术作品和这些知识，判断作品唤起的一种主要情感，并简要说明原因。如果没有提供知识，请仅依据作品判断。

请仅从以下情感中选择一项：好笑、惊叹、满意/满足、兴奋、愤怒、嫌恶、恐惧、伤感、其它情感。
请严格按以下格式回答：
情感：<情感>
解释：<简短解释>""",
    "arabic": """فسّر هذا العمل الفني من منظور ثقافي ناطق بالعربية. فيما يلي معرفة ثقافية ذات صلة استُرجعت للمفاهيم الظاهرة في الصورة:

{retrieved_tuples}

استنادًا إلى العمل الفني وهذه المعرفة، حدّد شعورًا واحدًا يثيره العمل واشرح السبب بإيجاز. إذا لم تُقدَّم معرفة، فاعتمد على العمل الفني وحده.

اختر شعورًا واحدًا فقط من: المتعة، الذهول، الرضا، الحماس، الغضب، الاشمئزاز، الخوف، الحزن، أخرى.
أجب بالصيغة التالية فقط:
الشعور: <الشعور>
التفسير: <تفسير موجز>""",
}

EMOTION_ALIGNMENT_PROMPTS = {
    "english": """Evaluate only emotion alignment: how well the explanation supports the model-predicted emotion for the English-speaking culture, using the artwork as visual evidence.

Predicted emotion: {predicted_emotion}
Explanation: {explanation}

Score on a 1-5 scale:
1 = The explanation contradicts or does not support the predicted emotion.
2 = The connection to the predicted emotion is weak or largely implausible.
3 = The explanation provides partial or generic support for the predicted emotion.
4 = The explanation clearly supports the predicted emotion with relevant evidence.
5 = The explanation strongly and coherently supports the predicted emotion with specific, culturally appropriate visual reasoning.

Return JSON only:
{{"emotion_alignment": <integer from 1 to 5>}}""",
    "chinese": """仅评估情感一致性：结合艺术作品中的视觉证据，判断解释在多大程度上支持模型针对中文文化群体预测的情感。

预测情感：{predicted_emotion}
解释：{explanation}

请按 1 至 5 分评分：
1 = 解释与预测情感矛盾或完全不支持该情感。
2 = 解释与预测情感的联系很弱或大多不可信。
3 = 解释对预测情感提供了部分支持，但较为笼统。
4 = 解释以相关证据清楚地支持预测情感。
5 = 解释通过具体、符合文化语境的视觉推理，有力且连贯地支持预测情感。

请仅返回 JSON：
{{"emotion_alignment": <1 至 5 的整数>}}""",
    "arabic": """قيّم محاذاة الشعور فقط: إلى أي مدى يدعم التفسير الشعور الذي تنبأ به النموذج للثقافة الناطقة بالعربية، بالاستناد إلى الأدلة البصرية في العمل الفني.

الشعور المتنبأ به: {predicted_emotion}
التفسير: {explanation}

قيّم من 1 إلى 5:
1 = يناقض التفسير الشعور المتنبأ به أو لا يدعمه.
2 = الصلة بالشعور المتنبأ به ضعيفة أو غير معقولة إلى حد كبير.
3 = يقدم التفسير دعمًا جزئيًا أو عامًا للشعور المتنبأ به.
4 = يدعم التفسير الشعور المتنبأ به بوضوح وبأدلة ذات صلة.
5 = يدعم التفسير الشعور المتنبأ به بقوة واتساق من خلال استدلال بصري محدد وملائم ثقافيًا.

أعد JSON فقط:
{{"emotion_alignment": <عدد صحيح من 1 إلى 5>}}""",
}

SFT_INSTRUCTIONS = {
    "english": "From an English-speaking cultural perspective, identify the single emotion evoked by this artwork and briefly explain why.",
    "chinese": "请从中文文化视角判断这件艺术作品唤起的一种主要情感，并简要说明原因。",
    "arabic": "من منظور ثقافي ناطق بالعربية، حدّد شعورًا واحدًا يثيره هذا العمل الفني واشرح السبب بإيجاز.",
}
