import pandas as pd
import requests
import json

# 리뷰 데이터 로드
df = pd.read_csv('reviews.csv', encoding='utf-8-sig')

review_texts = df['Review'].tolist()

# 파파고 번역 API 설정
papago_client_id = "vsffe7umav".strip()
papago_client_secret = "cCmMOJvVluQYkO1tpoGqIq3iNHrYqK9aq0JGwgXO".strip()

# 사용자로부터 번역할 언어 코드 입력 받기
target_language = input("Enter the target language code (e.g., en for English, ja for Japanese es for Spanish): ").strip()

# 번역을 위한 함수
def translate_text(text, target_language):
    url = "https://naveropenapi.apigw.ntruss.com/nmt/v1/translation"
    headers = {
        "X-NCP-APIGW-API-KEY-ID": papago_client_id,
        "X-NCP-APIGW-API-KEY": papago_client_secret,
        "Content-Type": "application/json"
    }
    data = {
        "source": "ko",
        "target": target_language,
        "text": text
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        result = response.json()
        return result['message']['result']['translatedText']
    else:
        print(f"Error translating text '{text}': {response.text}")
        return None

# 리뷰 번역 수행
translated_reviews = []
for review in review_texts:
    translated_text = translate_text(review, target_language)
    if translated_text:
        translated_reviews.append(translated_text)
    else:
        translated_reviews.append('Translation failed')

# 번역된 리뷰 출력
translated_df = pd.DataFrame({
    'Original Review': review_texts,
    'Translated Review': translated_reviews
})

print("\nTranslated Reviews:")
print(translated_df)
