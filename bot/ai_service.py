from openai import OpenAI
from transcrib_voice import *

def ai_service(answer, test):
  """функция, которая оценивает корректность выполнения задания"""
  client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="<OPENROUTER_API_KEY>",
  )

  completion = client.chat.completions.create(
    model="deepseek/deepseek-r1-0528-qwen3-8b:free",
    messages=[
      {"role": "system", "content": f"Ты — помощник по языковой практике. Оцени ответ пользователя.{test}"},
      {"role": "user", "content":f"{answer}" },
    ]
  )
  a = completion.choices[0].message.content
  print(a)
  return a

ai_service(text,test)

def ai_service_exercise():
  """функция, которая придумывает задания"""
  client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
  )

  completion = client.chat.completions.create(
    model="deepseek/deepseek-r1-0528-qwen3-8b:free",
    messages=[
      {"role": "system", "content": f"5 вопросов по одной из тем: внешность, жилье, семья, профессиональная деятельность, учеба, свободное время, хобби, праздники. Вопросы должны быть открытытми, для уровня знания языка А1, А2, В1"},
      {"role": "user", "content":"Придумай задание, напиши только 5 вопросов без дополнительных комментариев. Пиши вопросы только на одну тему" },
     ]
  )
  b = completion.choices[0].message.content
  print(b)
  return b

c = ai_service_exercise()
tts_gtts_mp3_bytes(c)
