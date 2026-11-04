
from database import get_transactions

df = get_transactions()

print("Database connection successful!")
print("Dataset shape:", df.shape)
print(df.head())
