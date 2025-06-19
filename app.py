import tkinter as tk
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:  # Pillow is optional
    Image = None
    ImageTk = None
    PIL_AVAILABLE = False
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:  # Pandas is optional
    pd = None
    PANDAS_AVAILABLE = False
import csv
from urllib.request import urlopen
import io
import webbrowser
import ast

class NewsApp:
    def __init__(self):
        self.load_gui()
        self.load_news_items()
        self.show_categories()
        self.root.mainloop()

    def load_gui(self):
        self.root = tk.Tk()
        self.root.geometry('350x550')
        self.root.resizable(0, 0)
        self.root.title('NewsShorts')
        self.root.configure(background='black')

    def load_news_items(self):
        if PANDAS_AVAILABLE:
            self.df = pd.read_csv('merged_summ_news_final.csv', index_col=0)
            if 'category' in self.df.columns:
                self.df['category'] = self.df['category'].apply(ast.literal_eval)
        else:
            self.df = []
            with open('merged_summ_news_final.csv', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'category' in row and row['category']:
                        try:
                            row['category'] = ast.literal_eval(row['category'])
                        except Exception:
                            row['category'] = [row['category']]
                    self.df.append(row)

    def show_categories(self):
        self.clear_frame()

        category_frame = tk.Frame(self.root, bg='black')
        category_frame.pack(pady=20)

        intro_label = tk.Label(category_frame, text=" Please click on the below category of your interest:", font=("Helvetica", 10), bg='black', fg='white')
        intro_label.pack(pady=5)

        if PANDAS_AVAILABLE:
            categories = self.df['category'].apply(lambda x: x[0] if isinstance(x, (list, tuple)) else ast.literal_eval(x)[0]).unique()
        else:
            categories = sorted({row['category'][0] if isinstance(row['category'], list) else row['category'] for row in self.df})
        for category in categories:
            category_button = tk.Button(category_frame,width=15, height= 4 , text=category.capitalize(),
                                        command=lambda cat=category: self.show_category(cat))
            category_button.pack(pady=5)

    def show_category(self, category):
        self.clear_frame()
        if PANDAS_AVAILABLE:
            category_df = self.df[self.df['category'].apply(lambda x: x[0] if isinstance(x, (list, tuple)) else ast.literal_eval(x)[0]) == category]
        else:
            category_df = [row for row in self.df if (row['category'][0] if isinstance(row['category'], list) else row['category']) == category]

        self.current_category = category
        self.current_index = 0

        news_frame = tk.Frame(self.root, bg='black')
        news_frame.pack(pady=20)

        self.news_image = tk.Label(news_frame, bg='black')
        self.news_image.pack()

        self.source_name = tk.Label(news_frame, text="", font=("Helvetica", 10, "italic"), bg='black', fg='white',justify='left')
        self.source_name.pack()

        self.news_title = tk.Label(news_frame, text="", font=("Helvetica", 16), wraplength=350, bg='black', fg='white', justify='center')
        self.news_title.pack(pady=(10, 20))

        self.news_summary = tk.Label(news_frame, text="", wraplength=350, justify='center', bg='black', fg='white')
        self.news_summary.pack(pady=(2, 20))

        self.update_news(category_df, self.current_index)

        prev_button = tk.Button(news_frame, text='Prev', width=10, height= 5, command=lambda: self.navigate(-1))
        prev_button.pack(side='left')

        read_more_button = tk.Button(news_frame, text='Read More', width=15, height= 5, command=lambda: self.read_more())
        read_more_button.pack(side='left') # padx=10

        next_button = tk.Button(news_frame, text='Next', width=10, height= 5, command=lambda: self.navigate(1))
        next_button.pack(side='left')

        home_button = tk.Button(news_frame, text='Home', width=10, height= 5, command=lambda: self.show_categories())
        home_button.pack(side='left')

    def navigate(self, delta):
        self.current_index += delta
        if PANDAS_AVAILABLE:
            category_df = self.df[self.df['category'].apply(lambda x: x[0] if isinstance(x, (list, tuple)) else ast.literal_eval(x)[0]) == self.current_category]
        else:
            category_df = [row for row in self.df if (row['category'][0] if isinstance(row['category'], list) else row['category']) == self.current_category]
        if self.current_index < 0:
            self.current_index = 0
        elif self.current_index >= len(category_df):
            self.current_index = len(category_df) - 1
        self.update_news(category_df, self.current_index)

    def update_news(self, category_df, idx):

        print("Category:", self.current_category)
        print("Index:", self.current_index)
        # Load and display image if Pillow is available
        if PIL_AVAILABLE:
            try:
                image_url = (category_df.iloc[idx]['image_url']
                             if PANDAS_AVAILABLE else category_df[idx]['image_url'])
                raw_data = urlopen(image_url).read()
                image = Image.open(io.BytesIO(raw_data))
                image = image.resize((350, 250))  # Resize the image as needed
                photo = ImageTk.PhotoImage(image)
                self.news_image.config(image=photo)
                self.news_image.image = photo  # To prevent garbage collection
            except Exception:
                img_url = 'https://www.hhireb.com/wp-content/uploads/2019/08/default-no-img.jpg'
                raw_data = urlopen(img_url).read()
                image = Image.open(io.BytesIO(raw_data)).resize((350, 250))
                photo = ImageTk.PhotoImage(image)
                self.news_image.config(image=photo)
                self.news_image.image = photo
        else:
            # Fallback if Pillow is not installed
            self.news_image.config(text='[Image unavailable]', image='')
            self.news_image.image = None

        # Update source name label with the source information
        if PANDAS_AVAILABLE:
            row = category_df.iloc[idx]
        else:
            row = category_df[idx]
        source_info = "source: " + row['source_id']
        self.source_name.config(text=source_info)
        self.news_title.config(text=row['title_en'])
        self.news_summary.config(text=row['summaries_en'])

    def read_more(self):
        if PANDAS_AVAILABLE:
            link = self.df[(self.df['category'].apply(lambda x: x[0] if isinstance(x, (list, tuple)) else ast.literal_eval(x)[0]) == self.current_category)].iloc[self.current_index]['link']
        else:
            category_items = [row for row in self.df if (row['category'][0] if isinstance(row['category'], list) else row['category']) == self.current_category]
            link = category_items[self.current_index]['link']
        # open browser
        webbrowser.open(link)

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()


obj = NewsApp()
