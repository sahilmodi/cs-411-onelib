import pandas as pd
import barnum
import random
import string

cols = ["UserID", "Name", "Age", "Zipcode", "PaymentNumber", "Password"]
users = pd.read_csv("User.csv", names=cols + ["1"])
users = users[cols]
review = pd.read_csv("Review_old.csv")
# print(review.head())
review.UserID = [random.choice(users.UserID.values) for _ in range(review.shape[0])]
review.to_csv("Review.csv", index=False)

# chars = string.ascii_letters + string.digits
# new_rows = []
# for i in range(300):
#     name = " ".join(barnum.create_name())
#     age = random.randint(18, 65)
#     zc = random.choice(users.Zipcode.values)
#     pn = int("".join([random.choice(string.digits) for _ in range(9)]))
#     pw = "".join([random.choice(chars) for _ in range(random.randint(8, 16))])
#     new_rows.append([0, name, age, zc, pn, pw])

# df2 = pd.DataFrame(new_rows, columns=cols)
# users = users.append(df2, ignore_index=True)
# users.UserID = list(range(users.shape[0]))
# users.to_csv("User.csv", index=False)
