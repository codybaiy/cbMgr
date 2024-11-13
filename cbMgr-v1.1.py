import win32clipboard
import tkinter as tk
from PIL import Image,ImageTk
import io
import win32con

class ClipboardManager:
    def __init__(self, max_entries=5):
        self.max_entries = max_entries
        self.last_content = None
        self.history = []
        self.root = tk.Tk()
        self.root.title("Clipboard History")
        self.listbox = tk.Listbox(self.root, width=80, height=15)
        self.listbox.pack(padx=10, pady=10)
        self.listbox.bind("<<ListboxSelect>>", self.show_image_preview)
        self.image_label = tk.Label(self.root, text="在此显示预览", width=40, height=15)
        self.image_label.pack(side=tk.LEFT, padx=10, pady=10)
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Delete", command=self.delete_item_from_mgr)
        self.menu.add_command(label="Copy", command=self.copy_item_from_mgr)
        self.listbox.bind("<Button-3>", self.show_menu)
        self.monitor_clipboard()

    @staticmethod
    def get_content_from_board():
        try:
            win32clipboard.OpenClipboard()
            if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_UNICODETEXT):
                text = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
                return text
            if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_DIB):
                clipboard_data = win32clipboard.GetClipboardData(win32clipboard.CF_DIB)
                image_data = io.BytesIO(clipboard_data)
                img = Image.open(image_data)
                return img
        except Exception as e:
            print(f"Error getting content from clipboard: {e}")
        finally:
            try:
                win32clipboard.CloseClipboard()
            except:
                pass
        return None

    def copy_text_to_board(self,content):
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            res = self.history[content]
            if isinstance(res,str):
                win32clipboard.SetClipboardData(win32clipboard.CF_UNICODETEXT, res[3:])
            if isinstance(res,Image.Image):
                self.copy_image_to_clipboard(res)
        except Exception as e:
            print(f"Error copying text to clipboard: {e}")

    def delete_item_from_mgr(self):
        selected_index = self.listbox.curselection()
        if selected_index:
            self.listbox.delete(selected_index[0])
            self.history.pop(selected_index[0])
            self.update_listbox()

    def copy_item_from_mgr(self):
        selected_index = self.listbox.curselection()
        if selected_index:
            self.copy_text_to_board(selected_index[0])

    def show_menu(self, event):
        self.menu.post(event.x_root, event.y_root)

    def monitor_clipboard(self):
        self.root.after(1000, self.check_clipboard)

    def check_clipboard(self):
        current_content = self.get_content_from_board()
        if current_content and current_content != self.last_content:
            self.add_to_history(current_content)
            self.update_listbox()
            self.last_content = current_content
        self.monitor_clipboard()

    def add_to_history(self,cont):
        if len(self.history) >= self.max_entries:
            self.history.pop(0)
        self.history.append(cont)
    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for index, item in enumerate(self.history, start=1):
            self.listbox.insert(tk.END, f"{index}. {item}")

    def show_image_preview(self, event):
        selection = self.listbox.curselection()
        if selection:
            index = selection[0]
            selected_item  = self.history[index]
            if isinstance(selected_item , Image.Image):
                selected_item.thumbnail((800,400))
                photo = ImageTk.PhotoImage(selected_item)
                img_width, img_height = selected_item.size
                self.image_label.config(width=img_width, height=img_height, image=photo, text="")
                self.image_label.image = photo
            elif isinstance(selected_item, str):
                self.image_label.config(image='', width=80, text=selected_item)

    @staticmethod
    def image_to_dib(image1):
        image1 = image1.convert("RGBA")
        byte_arr = io.BytesIO()
        image1.save(byte_arr, format="BMP")
        return byte_arr.getvalue()[14:]

    def copy_image_to_clipboard(self,image):
        try:
            dib_data = self.image_to_dib(image)
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32con.CF_DIB, dib_data)
            win32clipboard.CloseClipboard()
        except Exception as e:
            print(f"Error copying image to clipboard: {e}")
if __name__ == "__main__":
    a = ClipboardManager()
    a.root.mainloop()


