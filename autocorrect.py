import tkinter as tk
from tkinter import simpledialog, messagebox
from spellchecker import SpellChecker
import time

# Create the main application class
class AutoCorrectApp:
    def __init__(self, root):
        # Setting up the window
        self.root = root
        self.root.title("Real-Time Autocorrect Tool")
        self.root.geometry("600x500")
        self.root.config(background="#3380cc")


        # Default settings
        self.typing_delay = 500  # Time in milliseconds
        self.text_font = ("Arial", 14)  # Default font and size

        # Menu setup
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # Settings menu
        self.settings_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Settings", menu=self.settings_menu)
        self.settings_menu.add_command(label="Change Delay Time", command=self.change_delay_time)
        self.settings_menu.add_command(label="Change Font Style", command=self.change_font_style)

        # Title label
        title_label = tk.Label(root, text="Real-Time Autocorrect Tool", 
                               background="#0a2929", 
                               fg="White", 
                               font=("Arial", 16))
        title_label.pack(pady=10)

        # Initialize the SpellChecker object
        self.spell_checker = SpellChecker()

        # Default typing delay and font settings
        self.typing_delay = 500
        self.text_font = ("Arial", 14)

        # Create a text box to type the text
        self.text_box = tk.Text(root, 
                                wrap="word", 
                                font=self.text_font, 
                                height=10, 
                                width=50, 
                                fg="Black", 
                                bg="#c2f0f0")
        self.text_box.pack(pady=20)

        # Highlight settings
        self.text_box.tag_configure("misspelled", foreground="red")
        self.text_box.tag_configure("suggestion", foreground="blue", underline=True)

        # Frame for suggestion buttons
        self.suggestions_frame = tk.Frame(root)
        self.suggestions_frame.pack(pady=5, fill=tk.X)

        # Canvas to contain suggestion buttons and scrolling
        self.canvas = tk.Canvas(self.suggestions_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar for suggestions
        self.scrollbar = tk.Scrollbar(self.suggestions_frame,
                                    orient="horizontal",
                                    command=self.canvas.xview)
        self.scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Link scrollbar to canvas
        self.canvas.config(xscrollcommand=self.scrollbar.set)

        # Frame to hold buttons inside the canvas
        self.button_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.button_frame, anchor="nw")

        # Track the last time the user typed
        self.last_typing_time = time.time()

        # Bind the key release event to check spelling
        self.text_box.bind("<KeyRelease>", self.on_key_release)

    def on_key_release(self, event=None):
        # Update the last typing time whenever the user types something
        self.last_typing_time = time.time()
        self.root.after(self.typing_delay, self.check_spelling)

    def check_spelling(self):
        # If enough time has passed after typing, check spelling
        if time.time() - self.last_typing_time >= self.typing_delay / 1000:
            text = self.text_box.get("1.0", "end-1c")
            words = text.split()
            # Find misspelled words
            misspelled_words = list(self.spell_checker.unknown(words))

            # Remove previous highlights and suggestions
            self.text_box.tag_remove("misspelled", "1.0", "end")
            self.text_box.tag_remove("suggestion", "1.0", "end")
            self.clear_suggestions()  # Clear previous suggestions

            # Highlight misspelled words and show suggestions
            for word in misspelled_words:
                self.highlight_misspelled_word(word, words)

    def highlight_misspelled_word(self, misspelled_word, words):
        # Get suggestions for the misspelled word and sort them
        suggestions = list(self.spell_checker.candidates(misspelled_word))
        suggestions.sort(key=lambda w: self.spell_checker.word_frequency[w], reverse=True)

        # Get the top 3 or 4 suggestions
        top_suggestions = suggestions[:5]

        # Highlight the misspelled word in the text box
        text = self.text_box.get("1.0", "end-1c")
        start_idx = text.find(misspelled_word)
        end_idx = start_idx + len(misspelled_word)

        if start_idx != -1:
            start_pos = f"1.0+{start_idx}c"
            end_pos = f"1.0+{end_idx}c"

            self.text_box.tag_add("misspelled", start_pos, end_pos)

            # Create buttons for suggestions
            for suggestion in top_suggestions:
                self.create_suggestion_button(suggestion)

            # Update canvas scroll region for suggestions
            self.button_frame.update_idletasks()
            self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def create_suggestion_button(self, suggestion):
        # Create a button for each suggestion
        button = tk.Button(self.button_frame,
                            text=suggestion, 
                            width=15,
                            height=2, 
                            bg="light blue", 
                           font=("Arial", 12), 
                           command=lambda: self.replace_word(suggestion))
        button.pack(side=tk.LEFT, padx=10)

    def replace_word(self, selected_word):
    # Get the current text from the text box
        text = self.text_box.get("1.0", "end-1c")
        misspelled_word = self.get_current_misspelled_word(text)
    
        if misspelled_word:
        # Replace the first occurrence of the misspelled word with the selected suggestion
            corrected_text = text.replace(misspelled_word, selected_word, 1)
        
        # Update the text box with the corrected text
            self.text_box.delete("1.0", "end")
            self.text_box.insert("1.0", corrected_text)
    
        # Clear the suggestion buttons after replacing the word
            self.clear_suggestions()

        # Re-check the spelling to ensure the text is updated
            self.check_spelling()

    def clear_suggestions(self):
        # Remove all suggestion buttons from the frame
        for widget in self.button_frame.winfo_children():
            widget.destroy()

    def get_current_misspelled_word(self, text):
        # Find the first misspelled word in the text
        words = text.split()
        misspelled_words = list(self.spell_checker.unknown(words))
        return misspelled_words[0] if misspelled_words else None

    def change_delay_time(self):
        # Allow the user to change the delay time between typing and spell check
        new_delay = simpledialog.askinteger("Delay Time", 
                                            "Enter new delay time in ms (100-2000):", 
                                            minvalue=100, 
                                            maxvalue=2000)
        if new_delay:
            self.typing_delay = new_delay
            messagebox.showinfo("Settings", 
                                f"Delay time updated to {self.typing_delay} ms")

    def change_font_style(self):
        # Allow the user to change the font style and size
        new_font = simpledialog.askstring("Font Style", "Enter font name (e.g., Arial):")
        new_size = simpledialog.askinteger("Font Size", "Enter font size (e.g., 12):")
        if new_font and new_size:
            self.text_font = (new_font, new_size)
            self.text_box.config(font=self.text_font)
            messagebox.showinfo("Settings", f"Font updated to {new_font} {new_size}")

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = AutoCorrectApp(root)
    root.mainloop()
