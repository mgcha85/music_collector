import time
import sqlite3
import os
import requests
from bs4 import BeautifulSoup
import os

# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By



def download_mp3(url, title, path):
    headers = {
        'Referer': 'https://www.chosic.com/free-music/motivational/',
        'Sec-Ch-Ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Microsoft Edge";v="116"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.54'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:  # 상태 코드가 200일 때만 파일을 다운로드합니다.
        with open(os.path.join(path, f"{title}.mp3"), 'wb') as file:
            file.write(response.content)
        return True
    return False


def download_music_from_chosic(tag, download_path):
    if os.path.exists(download_path) is False:
        os.makedirs(download_path)

    headers = {
        'Referer': 'https://www.chosic.com/free-music/all/',
        'Sec-Ch-Ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Microsoft Edge";v="116"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.54'
    }

    url = f"https://www.chosic.com/free-music/{tag}/"

    # SQLite3 데이터베이스 연결 및 테이블 생성
    conn = sqlite3.connect('music_info.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS music (
        title TEXT,
        composer TEXT,
        duration TEXT,
        tag TEXT,
        url TEXT
    )
    ''')

    page = 1
    while url:  # 다음 페이지 URL이 존재하면 계속 반복
        print("page {}".format(page))
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        # 음악 정보 추출
        tracks = []
        track_elements = soup.find_all('div', class_='track-title-wrap')
        for track in track_elements:
            title = track.find('div', class_='trackF-title-inside').a.text
            title = title.replace('/', '_').replace('\\', '_').replace('|', '').replace('?', '')
            composer = track.find('div', class_='artist-track').a.text
            duration = soup.find('div', class_='time-full').text
            track_url = track.find('div', class_='trackF-title-inside').a['href']
            
            # 데이터베이스에 해당 정보가 이미 존재하는지 확인
            cursor.execute("SELECT * FROM music WHERE title=? AND composer=? AND duration=?", (title, composer, duration))
            existing_entry = cursor.fetchone()

            # 해당 정보가 데이터베이스에 존재하면 건너뛰기
            if existing_entry:
                continue

            tracks.append({
                'title': title,
                'composer': composer,
                'duration': duration,
                'url': track_url
            })

        # 각 음악의 URL을 방문하여 mp3 파일 다운로드
        for track in tracks:
            headers = {
                'Referer': 'https://www.chosic.com/free-music/motivational/',
                'Sec-Ch-Ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Microsoft Edge";v="116"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.54'
            }
            track_response = requests.get(track['url'], headers=headers)
            track_soup = BeautifulSoup(track_response.content, 'html.parser')
            download_button = track_soup.find('button', class_='download')
            if download_button:
                mp3_url = download_button['data-url']
                title = track['title'].replace('/', '_').replace('\\', '_').replace('|', '').replace('?', '')
                success = download_mp3(mp3_url, title, download_path)
                if success:  # 다운로드에 성공했을 때만 데이터베이스에 정보를 저장합니다.
                    cursor.execute("INSERT INTO music (title, composer, duration, tag, url) VALUES (?, ?, ?, ?, ?)", (track['title'], track['composer'], track['duration'], tag, mp3_url))
                    conn.commit()
        
        # 다음 페이지로 이동하는 링크 찾기
        next_page_link = soup.find('a', class_='next page-numbers')
        if next_page_link:
            url = next_page_link['href']
        else:
            url = None  # 다음 페이지 링크가 없으면 종료
        page += 1

    conn.close()


# def download_music_from_chosic(tag, download_path):
#     if os.path.exists(download_path) is False:
#         os.makedirs(download_path)

#     # 크롬드라이버 위치 지정
#     service = Service(executable_path='chromedriver-win64/chromedriver.exe')
#     options = webdriver.ChromeOptions()
#     prefs = {'download.default_directory': download_path}
#     options.add_experimental_option('prefs', prefs)
#     browser = webdriver.Chrome(service=service, options=options)

#     url = f"https://www.chosic.com/free-music/{tag}/"
#     browser.get(url)

#     # SQLite3 데이터베이스 연결 및 테이블 생성
#     conn = sqlite3.connect('music_info.db')
#     cursor = conn.cursor()
#     # cursor.execute('''
#     # CREATE TABLE IF NOT EXISTS music (
#     #     title TEXT,
#     #     composer TEXT,
#     #     tag TEXT,
#     #     url TEXT
#     # )
#     # ''')
#     # conn.commit()

#     while True:
#         # 현재 페이지에서 다운로드 링크 찾기
#         track_elements = browser.find_elements(By.XPATH, '//div[@class="track-title-wrap"]')
#         download_buttons = browser.find_elements(By.XPATH, '//a[contains(@class, "download-button track-download")]')
#         durations = browser.find_elements(By.XPATH, '//div[@class="time-full"]')
                
#         # 다운로드 링크를 통해 음악 다운로드 (현재는 링크만 출력)
#         for i, button in enumerate(download_buttons):
#             try:
#                 # TODO: 제목, 작곡가 등의 정보를 수집하는 코드를 추가해야 합니다.
#                 title = track_elements[i].find_element(By.XPATH, './/div[@class="trackF-title-inside"]/a').text
#                 composer = track_elements[i].find_element(By.XPATH, './/div[@class="artist-track"]/a').text
#                 duration = durations[i].text
#                 url = button.get_attribute('href')

#                 button.click()
#                 time.sleep(2)

#                 # 새 페이지에서 실제 다운로드 버튼 클릭
#                 real_download_button = browser.find_element(By.XPATH, '//button[contains(@class, "download")]')
#                 real_download_button.click()
#                 time.sleep(3)  # 다운로드 대기

#                 cursor.execute("INSERT INTO music (title, composer, tag, url) VALUES (?, ?, ?, ?)", (title, composer, tag, url))
#                 conn.commit()

#                  # 원래 페이지로 돌아가기
#                 browser.back()
#                 time.sleep(2)

#             except:
#                 print("버튼 클릭 오류 발생")

#         # 다음 페이지로 이동하는 링크 찾기
#         next_page_links = browser.find_elements(By.XPATH, '//a[contains(@class, "next page-numbers")]')
        
#         # 다음 페이지 링크가 없으면 종료
#         if not next_page_links:
#             break

#         # 다음 페이지로 이동
#         next_page_link = next_page_links[0].get_attribute('href')
#         browser.get(next_page_link)
#         time.sleep(2)  # 페이지 로드 대기

#     browser.quit()



for tag in ['Bach',
            'Beethoven',
            'Mozart',
            'Tropical',
            'House',
            'lullaby',
            'Lounge']:
    download_music_from_chosic(tag, os.path.join("D:/music", tag))
