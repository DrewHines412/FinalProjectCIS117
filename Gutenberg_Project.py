#Andrew Hines
#05/14/2025
#Guttenberg Final Project

import ssl
import urllib.request
import tkinter as tk
from tkinter import messagebox, scrolledtext
import sqlite3
import re
from collections import Counter

DB_NAME = 'books.db'

def init_db():
    ''' Initialize the database with the necessary tables.'''
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            title TEXT PRIMARY KEY
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS frequencies (
            title TEXT,
            word TEXT,
            freq INTEGER,
            FOREIGN KEY(title) REFERENCES books(title)
        )
    ''')
    conn.commit()
    conn.close()


def save_book(title, word_freq):
    ''' Save the book title and its word frequency to the database.'''
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO books (title) VALUES (?)', (title,))
    cursor.execute('DELETE FROM frequencies WHERE title = ?', (title,))
    for word, freq in word_freq:
        cursor.execute('INSERT INTO frequencies (title, word, freq) VALUES (?, ?, ?)', (title, word, freq))
    conn.commit()
    conn.close()


def get_book(title):
    ''' Retrieve the book title and its word frequency from the database.'''
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT word, freq FROM frequencies WHERE title = ? ORDER BY freq DESC LIMIT 10', (title,))
    rows = cursor.fetchall()
    conn.close()
    if rows:
        return [(word, freq) for word, freq in rows]
    return None

def fetch_text(url):
    ''' Fetch the text content of a given URL.'''
    try:
        # Open the URL and fetch the content
        context = ssl._create_unverified_context() #bypasses security encryption that kept causing error
        with urllib.request.urlopen(url, context=context) as response:
            # Read the response and decode it into text
            return response.read().decode('utf-8')
    except Exception as e:
        # Raise an exception if an error occurs
        raise RuntimeError(f"Failed to fetch text from the URL: {e}")


def get_top_words(text, n=10):
    ''' Extract the top n words from the given text using regular expressions and Counter class'''
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    counter = Counter(words)
    return counter.most_common(n)


def extract_title(text):
    ''' Extract the title of a book from the given text using regular expressions.'''
    match = re.search(r'Title:\s*(.+)', text)
    if match:
        return match.group(1).strip()
    return None

def search_title():
    ''' Search for a book in the database using its title and display the results. Also shows error
    messages if necessary.'''
    title = title_entry.get().strip()
    ''' Get the title from the title entry field and strip leading and trailing spaces.'''
    if not title:
        messagebox.showerror("Error", "Please enter a book title.")
        return
    data = get_book(title)
    if data:
        display_results(title, data)
    else:
        messagebox.showinfo("Info", "Book not found in local database.")


def search_url():
    ''' Search for a book in the database using its Project Gutenberg URL and display the results. Also shows error'''
    url = url_entry.get().strip()
    if not url:
        messagebox.showerror("Error", "Please enter a book URL.")
        return
    try:
        text = fetch_text(url)
        top_words = get_top_words(text)
        title = extract_title(text) or "Unknown Title"
        print(f"[DEBUG] Extracted title: {title}")
        save_book(title, top_words)
        display_results(title, top_words)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch or process book.\n{e}")


def display_results(title, word_freq):
    ''' Display the results of a search in the GUI.'''
    result_text.delete("1.0", tk.END)
    result_text.insert(tk.END, f"Top 10 Words in '{title}':\n\n")
    for word, freq in word_freq:
        result_text.insert(tk.END, f"{word}: {freq}\n")


if __name__ == "__main__":
    ''' Main function to run the GUI.'''
    init_db()

    root = tk.Tk()
    root.title("Word Searcher")
    ''' Create and configure the main window. '''

    bg_image = tk.PhotoImage(file="Zen.gif")
    bg_label = tk.Label(root, image=bg_image)
    bg_label.pack()
    bg_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    bg_label.image = bg_image
    ''' Add the background image to the window. '''

    tk.Label(root, text="Enter Book Title:").pack()
    title_entry = tk.Entry(root, width=50)
    title_entry.pack()
    tk.Button(root, text="Search Title", command=search_title).pack(pady=5)
    ''' Create and configure the title entry field. '''

    tk.Label(root, text="Enter Project Gutenberg URL:").pack()
    url_entry = tk.Entry(root, width=50)
    url_entry.pack()
    tk.Button(root, text="Search URL", command=search_url).pack(pady=5)
    ''' Create and configure the URL entry field. '''

    result_text = scrolledtext.ScrolledText(root, width=60, height=15)
    result_text.pack(pady=10)
    ''' Create and configure the results text field. '''

    root.mainloop()
    ''' Start the main event loop. '''
