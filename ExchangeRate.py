import requests

# 저장된 음식의 평균 가격 (예: 3000원)
average_price = 3000

# 환율 정보 가져오기 함수
#Exchangerate_API 사용
def get_exchange_rate(base_currency, target_currency):
    url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
    response = requests.get(url)
    data = response.json()
    return data['rates'].get(target_currency)

# 사용자로부터 변환할 나라 입력 받기
target_currency = input("어느 나라의 화폐로 변경할 것인지 입력하세요 (예: USD, EUR, JPY): ").upper()

# 원화를 선택한 화폐로 변환
exchange_rate = get_exchange_rate('KRW', target_currency)
if exchange_rate:
    converted_price = average_price * exchange_rate
    print(f"미리 설정된 평균 떡볶이 가격 ({target_currency}): {converted_price:.2f} {target_currency}")
else:
    print("환율 정보를 가져오는 데 실패했습니다.")
