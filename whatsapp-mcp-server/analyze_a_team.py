from whatsapp import list_messages, classify_group_messages, Message
import sqlite3
from datetime import datetime, timedelta

# Parameters
chat_jid = '120363050380912916@g.us'  # A-Team group JID
days_to_analyze = 5

# Get raw messages for analysis
conn = sqlite3.connect('../whatsapp-bridge/store/messages.db')
cursor = conn.cursor()
cursor.execute('''
    SELECT messages.timestamp, messages.sender, messages.content, messages.is_from_me 
    FROM messages 
    WHERE messages.chat_jid = ? AND messages.timestamp > ?
    ORDER BY messages.timestamp
    LIMIT 100
''', (chat_jid, (datetime.now() - timedelta(days=days_to_analyze)).isoformat()))

messages_raw = []
senders = set()

for row in cursor.fetchall():
    msg = Message(
        timestamp=datetime.fromisoformat(row[0]),
        sender=row[1],
        content=row[2],
        is_from_me=row[3],
        chat_jid=chat_jid,
        id=''
    )
    messages_raw.append(msg)
    senders.add(row[1])

conn.close()

# Analysis 1: Regular classification (assuming no Shopflo team members)
classification1 = classify_group_messages(messages_raw, [])

# Analysis 2: Classification with all senders considered as Shopflo team
shopflo_team_numbers = list(senders)
classification2 = classify_group_messages(messages_raw, shopflo_team_numbers)

# Print results
print(f"Analysis of A-Team group for the last {days_to_analyze} days:")
print(f"Total messages analyzed: {len(messages_raw)}")
print(f"Unique senders: {len(senders)}")
print(f"Senders: {', '.join(senders)}")
print("\nClassification scenarios:")
print(f"1. Regular classification (no Shopflo team members): {classification1}")
print(f"2. Classification with all senders as Shopflo team: {classification2}")

# Sample messages (first 5)
print("\nSample messages:")
for i, msg in enumerate(messages_raw[:5]):
    sender = "Me" if msg.is_from_me else msg.sender
    print(f"{i+1}. [{msg.timestamp}] From: {sender}: {msg.content[:50]}...") 