import win32clipboard
import win32con
import tkinter as tk


class ClipboardManager:
    def __init__(self, max_entries=5):
        self.max_entries = max_entries
        self.last_content = None
        self.history = []
        self.root = tk.Tk()
        self.root.title("Clipboard History")
        self.listbox = tk.Listbox(self.root, width=80, height=15)
        self.listbox.pack(padx=10, pady=10)
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Delete", command=self.delete_item_from_mgr)
        self.menu.add_command(label="Copy", command=self.copy_item_from_mgr)
        self.listbox.bind("<Button-3>", self.show_menu)
        self.monitor_clipboard()

    @staticmethod
    def get_text_from_board():
        try:
            win32clipboard.OpenClipboard()
            if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
                return text
        except Exception as e:
            print(f"Error getting text from clipboard: {e}")
        finally:
            try:
                win32clipboard.CloseClipboard()
            except Exception as e:
                print(f"Error closing clipboard: {e}")
        return None

    @staticmethod
    def copy_text_to_board(content):
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, content)
        except Exception as e:
            print(f"Error copying text to clipboard: {e}")
        finally:
            try:
                win32clipboard.CloseClipboard()
            except Exception as e:
                print(f"Error closing clipboard: {e}")

    def delete_item_from_mgr(self):
        selected_index = self.listbox.curselection()
        if selected_index:
            self.listbox.delete(selected_index[0])
            self.history.pop(selected_index[0])
            self.update_listbox()

    def copy_item_from_mgr(self):
        selected_index = self.listbox.curselection()
        if selected_index:
            words = self.listbox.get(selected_index[0])[3:]
            self.copy_text_to_board(words)

    def show_menu(self, event):
        self.menu.post(event.x_root, event.y_root)

    def monitor_clipboard(self):
        self.root.after(1000, self.check_clipboard)

    def check_clipboard(self):
        current_content = self.get_text_from_board()
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


if __name__ == "__main__":
    a = ClipboardManager()
    a.root.mainloop()