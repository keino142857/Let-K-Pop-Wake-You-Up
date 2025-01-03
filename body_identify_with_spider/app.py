from flask import Flask, render_template, redirect, url_for, request, jsonify
import threading
import time
import os
import subprocess
from information import speak_weather_info, speak_book_info, play_countdown
from weather import fetch_weather
from book import fetch_book
import webbrowser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

# 共享變數來控制鬧鐘音效的播放
alarm_playing = False
alarm_thread = None
person_detected = False
motion_detected_flag = False

vlc_path = "/usr/bin/vlc"  # VLC 安裝的路徑
def play_with_vlc():
    """使用 VLC 播放 .m4a 音效檔案"""
    alarm_sound_path = os.path.join(BASE_DIR, 'static', 'music', 'alarm.m4a')  # 音效檔案路徑

    try:
        # 使用 subprocess 執行 VLC 播放
        subprocess.Popen([vlc_path, alarm_sound_path, '--intf', 'dummy'])  # 使用 dummy 介面不顯示 VLC 視窗
        print("音效正在播放...")
    except Exception as e:
        print(f"無法啟動 VLC 播放音效: {e}")

def stop_vlc_alarm():
    """停止 VLC 播放音效"""
    # VLC 播放器停止功能可以進一步研究，通常 VLC 沒有簡單的 stop 命令，可能需要控制 VLC 進程
    print("停止 VLC 播放音效 (這需要進一步控制 VLC 進程)")

@app.route('/motion_detected', methods=['POST'])
def handle_motion_detected():
    global person_detected
    person_detected = True
    return jsonify({"status": "success"})

# 當手機發送 HTTP 請求時觸發
@app.route('/alarm', methods=['POST'])
def alarm():
    global alarm_playing, alarm_thread
    print("收到鬧鐘通知！")

    # 播放鬧鐘直到偵測到使用者
    if not alarm_playing:
        alarm_thread = threading.Thread(target=play_with_vlc)
        alarm_thread.start()
    
    webbrowser.open('http://192.168.1.151:5000/')
    
    # 偵測是否有人
    while not motion_detected_flag:
        print("沒有人在鏡頭前，繼續播放警報音！")
        time.sleep(1)  # 每秒檢查一次

    # 偵測到有人後停止鬧鐘並播放倒數 5 秒
    print("偵測到有人！停止鬧鐘並開始倒數。")
    alarm_playing = False  # 停止鬧鐘音效
    if alarm_thread.is_alive():
        alarm_thread.join()

    return redirect(url_for('challenge'))
    
@app.route('/')
def index():
    # 顯示初始頁面
    return render_template('index.html')

@app.route('/challenge')
def challenge():
   
    return render_template('challenge.html')

if __name__ == "__main__":
    # 語音播放
    speak_weather_info(fetch_weather())
    speak_book_info(fetch_book())
    
    try:
        app.run(host="0.0.0.0", port=5001, debug=True, use_reloader=False)
    except Exception as e:
        print(f"Error: {e}")
