from collections import defaultdict
import pandas as pd
import random
from tqdm import tqdm

library = pd.read_csv("Library.csv")
books = pd.read_csv("Book.csv")

data = defaultdict(list)
seed = 0
books_per_library = 100
for libid in tqdm(library["LibraryID"].values, dynamic_ncols=True):
    rand_books = books.sample(frac=books_per_library/books.shape[0], random_state=seed, replace=False)
    for isbn in rand_books.ISBN.values:
        data["LibraryID"].append(libid)
        data["ISBN"].append(isbn)
        random.seed(seed)
        data["Quantity"].append(random.randint(1, 5))
        buyable = random.random() < 0.1
        late_fee = None if buyable else round(random.random() * 10, 2)
        price = round(random.random() * 30, 2) if buyable else None
        timelimitdays = None if buyable else random.randint(1, 21)
        data["Buyable"].append(buyable) 
        data["LateFee"].append(late_fee)
        data["Price"].append(price)
        data["TimeLimitDays"].append(timelimitdays)
        seed += 1

library_books = pd.DataFrame.from_dict(data)
libary_books = library_books[["LibraryID", "ISBN", "Quantity", "LateFee", "Price", "Buyable", "TimeLimitDays"]]
library_books.to_csv("LibraryBook.csv", index=False)
