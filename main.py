import yt_dlp as youtube_dl
import os
import requests
import sys
from Terminal_Effects import tcolors, clear_terminal

PASSWORDS_URL = "https://pwlist.netlify.app/pass.txt"  # Parola listesinin bulunduğu URL

# Kullanıcıdan parolayı doğrulayan fonksiyon
def get_password_list():
    try:
        response = requests.get(PASSWORDS_URL, timeout=10)  # HTTPS bağlantısı
        response.raise_for_status()  # Hata durumlarını kontrol et
        return set(response.text.splitlines())  # Satır satır parolaları sete çevir (optimizasyon)
    except requests.exceptions.RequestException as e:
        print(f"{tcolors.red}Parola listesi alınamadı: {e}{tcolors.clear}")
        sys.exit(1)

def verify_password():
    print(f"{tcolors.cyan}Lütfen programı kullanmak için parolanızı girin.{tcolors.clear}")
    password_list = get_password_list()
    while True:
        user_password = input(f"{tcolors.yellow}Parola: {tcolors.clear}")
        if user_password in password_list:
            print(f"{tcolors.green}Parola doğru! Programa devam ediliyor...{tcolors.clear}")
            break
        else:
            print(f"{tcolors.red}Parola yanlış, tekrar deneyin.{tcolors.clear}")

# Kullanıcıya başlangıç mesajları ve seçenekler gösteriliyor
start_info = [
    f"{tcolors.cyan}Youtube Downloader{tcolors.clear}", 
    f"{tcolors.gray}Written in Python 3.10.7 - 12/1/2023",
    "By SakuK" + tcolors.clear,
]

options = [
    "Choose what format do you want to download",
    "---",
    f"{tcolors.yellow}1){tcolors.clear} Audio only in mp3",
    f"{tcolors.yellow}2){tcolors.clear} Audio only in webm",
    f"{tcolors.yellow}3){tcolors.clear} Video & Audio in mp4",
    f"{tcolors.yellow}4){tcolors.clear} Video & Audio in webm",
]

playlist_options = [
    "Do you want to download a playlist?",
    "y/n"
]

def my_hook(d):
    if d['status'] == 'finished':
        print('\nDone downloading, now converting ...')

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
        Exception("Invalid choice")

def main():
    print(clear_terminal.clear())
    verify_password()  # Parola doğrulama
    print("\n".join(start_info))
    print("---")
    print("\n".join(options))
    print()
    user_choice = input("Input your choice (numerically): ")

    try:
        process_choice(user_choice)
    except Exception as e:
        print(e)
        input("Press enter to quit")
        return

    print("\n".join(playlist_options))
    playlist_choice = input()

    if playlist_choice == "y":
        ydl_opts["noplaylist"] = False
    elif playlist_choice == "n":
        ydl_opts["noplaylist"] = True
    else:
        input("Press enter to try again")
        main()
        return

    link = input("Input the link to the video: ")
    print(clear_terminal.clear())
    if ydl_opts["noplaylist"] == True:
        print(f"{tcolors.gray}Downloading video info...{tcolors.clear}")
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=False)
        print(clear_terminal.clear())
        print(f"Title: {tcolors.yellow}{info['title']}{tcolors.clear}")
        print(f"Upload date: {tcolors.yellow}{info['upload_date']}{tcolors.clear}")
        print(f"Uploader: {tcolors.yellow}{info['uploader']}{tcolors.clear}")
        print(f"View count: {tcolors.yellow}{info['view_count']}{tcolors.clear}")
        print(f"Format: {tcolors.yellow}{info['format']}{tcolors.clear}")
        print(f"Duration: {tcolors.yellow}{info['duration']}{tcolors.clear}")

        print("Is this the correct video? (y/n)")
        correct_video = input()
    else:
        print(f"{tcolors.gray}Downloading playlist info...{tcolors.clear}")
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=False)
        print(clear_terminal.clear())
        print(f"Title: {tcolors.yellow}{info['title']}{tcolors.clear}")
        print(f"Description: {tcolors.yellow}{info['description']}{tcolors.clear}")
        print(f"Uploader: {tcolors.yellow}{info['uploader']}{tcolors.clear}")
        print(f"Amount of videos: {tcolors.yellow}{info['playlist_count']}{tcolors.clear}")

        print("Is this the correct playlist? (y/n)")
        correct_video = input()

    try:
        if correct_video == "y" and ydl_opts["noplaylist"] == True:
            print("Downloading video to desktop...")
            download_video(ydl_opts, link)
            end_info(info["title"])
        if correct_video == "y" and ydl_opts["noplaylist"] == False:
            print("Downloading playlist to desktop...")
            download_video(ydl_opts, link)
            end_info(info["title"])
        else:
            print("Press enter to try again")
            input()
            main()
            return
    except Exception as e:
        print(f"Error occurred: {tcolors.red}{str(e)}{tcolors.clear}")

def download_video(ydl_opts, link):
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])

def end_info(filename):
    print(clear_terminal.clear())
    print("Done downloading video")
    if (ydl_opts["noplaylist"] == True):
        print(f"File {tcolors.yellow}{filename}{tcolors.clear} was downloaded to your desktop")
    else:
        print(f"Playlist {tcolors.yellow}{filename}{tcolors.clear} was downloaded to your desktop")
    input("Press enter to quit")
    return

main()
