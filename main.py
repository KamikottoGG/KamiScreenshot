import datetime
import threading
import winreg
import keyword

import keyboard
import requests
from PIL import ImageGrab
import os
import sys
import win32con
import win32gui
import win32api
import win32process
import win32event
import win32gui_struct
import winreg as reg

from plyer import notification
from win32com.client import Dispatch

python_script_path = os.path.abspath(sys.argv[0])

icon_path = 'configs/icon.ico'

def get_api_key():
    with open("configs/api_key.txt", "r") as f:
        return f.read()

api_key = get_api_key()
def create_background_window():
    wc = win32gui.WNDCLASS()
    wc.hInstance = hInstance = win32api.GetModuleHandle(None)
    wc.lpszClassName = "KamiScreenshots"
    wc.lpfnWndProc = wnd_proc  # Обработчик сообщений окна

    class_atom = win32gui.RegisterClass(wc)

    hwnd = win32gui.CreateWindow(
        class_atom,
        "KamiScreenshots",
        win32con.WS_ICONIC,
        0, 0, 0, 0,
        0, 0, hInstance, None
    )

    icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
    icon_handle = win32gui.LoadImage(0, icon_path, win32con.IMAGE_ICON, 0, 0, icon_flags)

    nid = (hwnd, 0, win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP, win32con.WM_USER + 20, icon_handle,
           "KamiScreenshots")
    win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, nid)
    return hwnd

def wnd_proc(hwnd, msg, wparam, lparam):
    if msg == win32con.WM_USER + 20:  # Событие от иконки в трее
        if lparam == win32con.WM_RBUTTONUP:  # Нажатие правой кнопки мыши
            show_menu(hwnd)
        elif lparam == win32con.WM_LBUTTONUP:  # Нажатие левой кнопки мыши
            show_main_menu()
    elif msg == win32con.WM_CONTEXTMENU:  # Событие вызова контекстного меню
        show_menu(hwnd)
    elif msg == win32con.WM_CLOSE:  # Закрытие окна
        win32gui.DestroyWindow(hwnd)
    elif msg == win32con.WM_DESTROY:  # Уничтожение окна
        win32gui.PostQuitMessage(0)
    return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)


def show_menu(hwnd):
    menu = win32gui.CreatePopupMenu()
    win32gui.AppendMenu(menu, win32con.MF_STRING, 1, "Выход")

    pos = win32gui.GetCursorPos()
    win32gui.TrackPopupMenu(menu, win32con.TPM_LEFTALIGN, pos[0], pos[1], 0, hwnd, None)
    win32gui.PostMessage(hwnd, win32con.WM_NULL, 0, 0)



def show_main_menu():
    sys.exit(0)
    pass

def wait_for_exit():
    try:
        win32event.WaitForSingleObject(win32process.GetCurrentProcess(), win32event.INFINITE)
    except KeyboardInterrupt:
        pass

def unregister_from_startup():
    try:
        key = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "KamiScreenshots"
        reg_path = f"{key}\\{app_name}"
        reg.DeleteKey(winreg.HKEY_CURRENT_USER, reg_path)
    except Exception as e:
        print(f"Ошибка удаления из автозапуска: {e}")

def on_f2_press(e):
    if e.name == 'f2':
        threading.Thread(target= screenshot_and_notify()).start()


def screenshot_and_notify():
    with open(f"logs/{datetime.datetime.now().date()}.txt", "a+", encoding="utf-8") as f:
        try:
            screenshot = ImageGrab.grab()
            screenshot.save('configs/screenshot.png')

            url = "https://api.e-z.host/files"
            headers = {"key": api_key, "randomdamain": str(True),
                       "amongusUrl": str(False)}

            with open("configs/screenshot.png", "rb") as file:
                files = {"file": ("configs/screenshot.png", file, "image/png")}
                response = requests.post(url, headers=headers, files=files)
            f.write(f"[{datetime.datetime.now().time()}] [LINK: {response.json()['imageUrl']}] [DEL LINK: {response.json()['deletionUrl']}]\n")


            notification.notify(
                title='Успех!',
                message='Успешная загрузка скриншота!',
                app_name='KamiScreenshots',
                timeout=10,
            )

        except Exception as e:
            f.write(f"[ERROR] {e}\n")
            notification.notify(
                title='Ошибка!',
                message='Случилась ошибка при загрузке скриншота!',
                app_name='KamiScreenshots',
                timeout=10,
            )

keyboard.on_press_key('F2', on_f2_press)



def register_in_startup():
    try:
        key = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "KamiScreenshots"
        reg_path = f"{key}\\{app_name}"
        reg.SetValue(winreg.HKEY_CURRENT_USER, reg_path, winreg.REG_SZ, python_script_path)
    except Exception as e:
        print(f"Error: {e}")

register_in_startup()

hwnd = create_background_window()

wait_for_exit()


unregister_from_startup()
win32gui.DestroyWindow(hwnd)