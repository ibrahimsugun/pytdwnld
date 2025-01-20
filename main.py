import yt_dlp as youtube_dl
import os
import requests
import sys
import hashlib
from Terminal_Effects import tcolors, clear_terminal

PASSWORDS_URL = "https://pwlist.netlify.app/pass.txt"  # Hashlenmiş parolaların bulunduğu URL

# Parola listesini indiren ve döndüren fonksiyon
def get_password_list():
    try:
        response = requests.get(PASSWORDS_URL, timeout=10)  # HTTPS bağlantısı
        response.raise_for_status()  # Hata durumlarını kontrol et
        return set(response.text.splitlines())  # Satır satır hash'leri sete çevir (optimizasyon)
    except requests.exceptions.RequestException as e:
        print(f"{tcolors.red}Parola listesi alınamadı: {e}{tcolors.clear}")
        sys.exit(1)

# Parola hashleme fonksiyonu
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# Parola doğrulama fonksiyonu
def verify_password():
    print(f"{tcolors.cyan}Lütfen programı kullanmak için parolanızı girin.{tcolors.clear}")
    password_list = get_password_list()

    while True:
        user_password = input(f"{tcolors.yellow}Parola: {tcolors.clear}")
        hashed_password = hash_password(user_password)  # Kullanıcı parolasını hashle

        if hashed_password in password_list:  # Hash'leri karşılaştır
            print(f"{tcolors.green}Parola doğru! Programa devam ediliyor...{tcolors.clear}")
            break
        else:
            print(f"{tcolors.red}Parola yanlış, tekrar deneyin.{tcolors.clear}")

# Kullanıcıya başlangıç mesajları ve seçenekler gösteriliyor
start_info = [
    f"{tcolors.cyan}Youtube Downloader{tcolors.clear}", 
    f"{tcolors.gray}Python ile yazılmıştır.",
    "" + tcolors.clear,
]

options = [
    "İndirme formatını seçin:",
    "---",
    f"{tcolors.yellow}1){tcolors.clear} Sadece ses (mp3 formatında)",
    f"{tcolors.yellow}2){tcolors.clear} Sadece ses (webm formatında)",
    f"{tcolors.yellow}3){tcolors.clear} Video ve ses (mp4 formatında)",
    f"{tcolors.yellow}4){tcolors.clear} Video ve ses (webm formatında)",
]

def my_hook(d):
    if d['status'] == 'finished':
        print('\nİndirme tamamlandı, şimdi dönüştürülüyor...')

# Kullanıcının masaüstü yolunu buluyor
desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')

# youtube-dl seçenekleri
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': desktop + '/%(title)s.%(ext)s',
    'noplaylist': True,
    'progress_hooks': [my_hook],
}

def process_choice(choice):
    if choice == "1":
        ydl_opts["format"] = "bestaudio/best"
        ydl_opts["postprocessors"] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
        return
    if choice == "2":
        ydl_opts["format"] = "bestaudio/best"
        return
    if choice == "3":
        ydl_opts["format"] = "bestvideo+bestaudio/best"
        ydl_opts["postprocessors"] = [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }]
        return
    if choice == "4":
        ydl_opts["format"] = "bestvideo+bestaudio/bestvideo/best"
        return
    else:
        raise ValueError("Geçersiz seçim")

def get_user_choice():
    while True:
        user_choice = input("Seçiminizi girin (numaralı): ")
        if user_choice.isdigit() and user_choice in ["1", "2", "3", "4"]:
            return user_choice
        else:
            print(f"{tcolors.red}Geçersiz giriş! Lütfen yalnızca 1, 2, 3 veya 4 rakamlarını girin.{tcolors.clear}")

def main():
    print(clear_terminal.clear())
    verify_password()  # Parola doğrulama
    print("\n".join(start_info))
    print("---")
    print("\n".join(options))
    print()
    user_choice = get_user_choice()

    try:
        process_choice(user_choice)
    except Exception as e:
        print(e)
        input("Çıkmak için Enter tuşuna basın")
        return

    link = input("Video bağlantısını girin: ")
    print(clear_terminal.clear())
    print(f"{tcolors.gray}Video bilgisi indiriliyor...{tcolors.clear}")
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(link, download=False)
    print(clear_terminal.clear())
    print(f"Başlık: {tcolors.yellow}{info['title']}{tcolors.clear}")
    print(f"Yüklenme tarihi: {tcolors.yellow}{info['upload_date']}{tcolors.clear}")
    print(f"Yükleyici: {tcolors.yellow}{info['uploader']}{tcolors.clear}")
    print(f"İzlenme sayısı: {tcolors.yellow}{info['view_count']}{tcolors.clear}")
    print(f"Format: {tcolors.yellow}{info['format']}{tcolors.clear}")
    print(f"Süre: {tcolors.yellow}{info['duration']}{tcolors.clear}")

    print("Bu doğru video mu? (e/h)")
    correct_video = input()

    try:
        if correct_video == "e":
            print("Video masaüstüne indiriliyor...")
            download_video(ydl_opts, link)
            end_info(info["title"])
        else:
            print("Tekrar denemek için Enter tuşuna basın")
            input()
            main()
            return
    except Exception as e:
        print(f"Bir hata oluştu: {tcolors.red}{str(e)}{tcolors.clear}")

def download_video(ydl_opts, link):
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])

def end_info(filename):
    print(clear_terminal.clear())
    print("İndirme tamamlandı")
    print(f"Dosya {tcolors.yellow}{filename}{tcolors.clear} masaüstüne indirildi")
    print("Çıkmak için Enter tuşuna basın")
    input()
    return

main()
