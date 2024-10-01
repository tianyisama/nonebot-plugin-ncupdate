# 真有系统不带tk库
try:
    import tkinter as tk
    import tkinter.font as tkFont
    from tkinter import messagebox
except ImportError:
    tk = None
    tkFont =None
import asyncio
import threading


def run_tkinter_dialog(loop, future):
    def on_restart():
        loop.call_soon_threadsafe(future.set_result, "restart")
        root.destroy()

    def on_cancel():
        loop.call_soon_threadsafe(future.set_result, "cancel")
        root.destroy()

    root = tk.Tk()
    root.title("重启 Napcat")
    root.attributes('-topmost', True)
    # 设置字体
    label_font = tkFont.Font(family="Helvetica", size=12, weight="bold")
    button_font = tkFont.Font(family="Helvetica", size=10)
    # 设置窗口大小
    window_width = 400
    window_height = 200

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)

    root.geometry(f'{window_width}x{window_height}+{x}+{y}')
    tk.Label(root, text="将在10s后重启 Napcat", font=label_font).pack(pady=(20, 10))
    tk.Button(root, text="立即重启", command=on_restart, font=button_font).pack(side=tk.LEFT, padx=(50, 10))
    tk.Button(root, text="取消重启", command=on_cancel, font=button_font).pack(side=tk.RIGHT, padx=(10, 50))
    root.after(10000, on_restart)
    root.mainloop()

async def tkinter_dialog():
    loop = asyncio.get_running_loop()
    future = loop.create_future()
    t = threading.Thread(target=run_tkinter_dialog, args=(loop, future))
    t.start()
    result = await future
    t.join()
    return result