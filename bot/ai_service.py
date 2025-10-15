from openai import OpenAI
from transcrib_voice import *

def ai_service(answer, text):
  """функция, которая оценивает корректность выполнения задания"""
  client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="<OPENROUTER_API_KEY>",
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
