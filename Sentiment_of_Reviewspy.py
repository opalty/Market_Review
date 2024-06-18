import pandas as pd
import requests
import json
import re

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
