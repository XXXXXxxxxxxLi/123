from faker import Faker
import random

fake = Faker()

# 生成随机用户数据
def generate_users(n=10):
    users = []
    for _ in range(n):
        user = {
            'username': fake.user_name(),
            'email': fake.email(),
            'password': fake.password(),
            'full_name': fake.name()
        }
        users.append(user)
    return users

# 生成随机书籍数据
def generate_books(n=10):
    books = []
    for _ in range(n):
        book = {
            'title': fake.catch_phrase(),
            'author': fake.name(),
            'cover_image': fake.image_url(),
            'description': fake.text(),
            'average_rating': round(random.uniform(1, 5), 2)
        }
        books.append(book)
    return books

# 执行函数并打印结果
users = generate_users(5)  # 生成5个用户
books = generate_books(10)  # 生成10本书

print("Generated Users:")
for user in users:
    print(user)

print("\nGenerated Books:")
for book in books:
    print(book)
