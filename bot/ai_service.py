from openai import OpenAI
from transcrib_voice import *

def ai_service(answer, text):
  """функция, которая оценивает корректность выполнения задания"""
  client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
  )

  completion = client.chat.completions.create(
    model="deepseek/deepseek-r1-0528-qwen3-8b:free",
    messages=[
      {"role": "system", "content": f"Ты — помощник по языковой практике по английскому языку. Оцени ответ пользователя.{text}"},
      {"role": "user", "content":f"{answer}" },
    ]
  )
  a = completion.choices[0].message.content
  print(a)
  return a

ai_service(text,text)

def ai_service_exercise():
  """функция, которая придумывает задания"""
  client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
  )

  completion = client.chat.completions.create(
    model="deepseek/deepseek-r1-0528-qwen3-8b:free",
    messages=[
      {"role": "system", "content": f"5 вопросов на английском языке по одной из тем: внешность, жилье, семья, профессиональная деятельность, учеба, свободное время, хобби, праздники. Вопросы должны быть открытытми, для уровня знания языка А1, А2, В1"},
      {"role": "user", "content":"Придумай задание, напиши только 5 вопросов без дополнительных комментариев. Пиши вопросы только на одну тему" },
     ]
  )
  b = completion.choices[0].message.content
  print(b)
  return b

c = ai_service_exercise()
tts_gtts_mp3_bytes(c)

def ai_service_faq(question):
  """функция, которая отправляем вопрос оператору"""
  # Формируем структурированный список FAQ
  faq_list = {
    "Как начать практиковать язык с ботом?": "Просто напишите команду /practice в диалоге с ботом. После этого бот предложит первые задания для практики.",
    "На каких языках можно практиковаться?": "В настоящее время бот поддерживает английский язык. В будущем планируется расширение списка доступных языков.",
    "Как настроить сложность заданий?": "Бот предлагает задания для уровня А1, А2, В1.",
    "Как узнать, правильно ли я выполняю задания?": "Бот автоматически проверяет ваши ответы и предоставляет обратную связь.",
    "Могу ли я пользоваться ботом в любое время?": "Да, бот доступен 24/7 без ограничений по времени. Вы можете практиковать язык когда угодно и где угодно, главное — иметь доступ к интернету. Количество заданий и время использования не ограничены."
  }

  # Формируем текст FAQ для отправки в модель
  faq_text = "\n".join([f"{q}: {a}" for q, a in faq_list.items()])

  client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
  )

  completion = client.chat.completions.create(
    model="deepseek/deepseek-r1-0528-qwen3-8b:free",
    messages=[
      {"role": "system", "content": f"Это список вопросов и ответов FAQ:\n{faq_text}\n\nТвоя задача: проверь, есть ли вопрос пользователя в этом списке FAQ. Если вопрос есть в списке — верни текст соответствующего ответа. Если вопроса нет в списке — верни число 0." "},
      {"role": "user", "content":f"{question}" }
    ]
  )
  response = completion.choices[0].message.content.strip()
  # Проверяем, является ли ответ числом 0
    if response == "0":
      return 0
    else:
    return response

