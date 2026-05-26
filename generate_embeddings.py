from sentence_transformers import SentenceTransformer
import psycopg2

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Connect to PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="postgres",
    password="password"
)

cur = conn.cursor()

# Fetch users
cur.execute("""
    SELECT id, name, username, email
    FROM user_table
""")

rows = cur.fetchall()

for row in rows:

    user_id = row[0]

    name = row[1] or ""
    username = row[2] or ""
    email = row[3] or ""

    # Combine user information
    text = f"{name} {username} {email}"

    # Generate embedding
    embedding = model.encode(text).tolist()

    # Update embedding column
    cur.execute("""
        UPDATE user_table
        SET embedding = %s
        WHERE id = %s
    """, (embedding, user_id))

conn.commit()

cur.close()
conn.close()

print("User embeddings stored successfully!")