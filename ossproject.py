import csv
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests
import json
import re

# 크롬 드라이버 설정
chrome_options = Options()

# 웹 드라이버 서비스 설정
service = Service(ChromeDriverManager().install())

# 웹 드라이버 시작
driver = webdriver.Chrome(service=service, options=chrome_options)

# 네이버 지도 페이지로 이동
driver.get("https://m.place.naver.com/place/13304144/review/visitor?entry=plt")

# 페이지가 로드될 때까지 대기
wait = WebDriverWait(driver, 10)

# '더보기' 버튼을 반복적으로 클릭하여 모든 리뷰 로드
while True:
    try:
        more_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'fvwqf')))
        driver.execute_script("arguments[0].click();", more_button)
        time.sleep(1)  # 페이지 로드 시간 대기
    except Exception:
        break

# 모든 리뷰 요소 추출
reviews = driver.find_elements(By.CLASS_NAME, 'zPfVt')
review_list = [review.text for review in reviews]

# 크롬 드라이버 종료
driver.quit()

# 리뷰 데이터를 CSV 파일로 저장
csv_file = 'reviews.csv'
with open(csv_file, 'w', encoding='utf-8-sig', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Review'])  # CSV 파일의 첫 번째 행은 열 제목
    for review in review_list:
        writer.writerow([review])

print(f"Total {len(review_list)} reviews have been saved to {csv_file}")






# 리뷰 데이터 로드 및 전처리
df = pd.read_csv('reviews.csv', encoding='utf-8-sig')

def preprocess_text(text):
    text = re.sub('[^가-힣 ]', '', str(text))
    text = re.sub('\s+', ' ', text).strip()
    return text

df['Review'] = df['Review'].apply(preprocess_text)
df = df[df['Review'] != '']

review_texts = df['Review'].tolist()

# 네이버 클라우드 감정 분석 API 설정
client_id = "hnxg2izuff".strip()
client_secret = "NctXoUBArSam4j2ttIdcIQlaPX2vw0MnLmZiNAdZ".strip()
url = "https://naveropenapi.apigw.ntruss.com/sentiment-analysis/v1/analyze"
headers = {
    "X-NCP-APIGW-API-KEY-ID": client_id,
    "X-NCP-APIGW-API-KEY": client_secret,
    "Content-Type": "application/json"
}

# 감정 분석을 위한 함수
def analyze_sentiment(text):
    data = {
        "content": text
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        result = response.json()
        sentiment = result['document']['sentiment']
        confidence = result['document']['confidence']
        return sentiment, confidence
    else:
        print(f"Error analyzing sentiment for '{text}': {response.text}")
        return None, None

# 감정 분석 수행 및 결과 저장
sentiments = []
negative_confidence = []
positive_confidence = []
neutral_confidence = []

for text in review_texts:
    sentiment, confidence = analyze_sentiment(text)
    if sentiment:
        sentiments.append(sentiment)
        negative_confidence.append(confidence['negative'])
        positive_confidence.append(confidence['positive'])
        neutral_confidence.append(confidence['neutral'])
    else:
        sentiments.append('Unknown')
        negative_confidence.append(0.0)
        positive_confidence.append(0.0)
        neutral_confidence.append(0.0)

# 결과 데이터프레임 생성
result_df = pd.DataFrame({
    'Review': review_texts,
    'Sentiment': sentiments,
    'Negative Confidence': negative_confidence,
    'Positive Confidence': positive_confidence,
    'Neutral Confidence': neutral_confidence
})

# 긍정/부정 리뷰 출력
negative_reviews = result_df[result_df['Sentiment'] == 'negative']
print("\nNegative Reviews:")
print(negative_reviews[['Review', 'Sentiment']])

positive_reviews = result_df[result_df['Sentiment'] == 'positive']
print("\nPositive Reviews:")
print(positive_reviews[['Review', 'Sentiment']])





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