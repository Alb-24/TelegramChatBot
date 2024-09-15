import sqlite3
from UserStatus import UserStatus


def create_db():
    # Connect to the chatbot database
    conn = sqlite3.connect('chatbot_database.db')
    c = conn.cursor()
    # Create the users table if it does not exist (user_id, status, partner_id)
    c.execute("CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, status TEXT, partner_id TEXT)")
    conn.commit()
    conn.close()


def insert_user(user_id):
    # Connect to the chatbot database
    conn = sqlite3.connect('chatbot_database.db')
    c = conn.cursor()
    # Check if the user is already in the users table
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if c.fetchone():
        # If the user is already in the users table, do nothing
        conn.close()
        return

    # Otherwise, insert the user into the users table
    c.execute("INSERT INTO users VALUES (?, ?, ?)", (user_id, UserStatus.IDLE, None))  # No partner_id initially
    conn.commit()
    conn.close()


def remove_user(user_id):
    # If a user disconnects, remove him/her from the users table
    conn = sqlite3.connect('chatbot_database.db')  # Connect to the chatbot database
    c = conn.cursor()
    # Check if the user had a partner
    partner_id = get_partner_id(user_id)
    if partner_id:
        # If the user had a partner, remove the user from the partner's row
        c.execute("UPDATE users SET partner_id=NULL WHERE user_id=?", (partner_id,))
        # Update the partner's status to UserStatus.PARTNER_LEFT
        set_user_status(partner_id, UserStatus.PARTNER_LEFT)
    else:
        # Simply remove the user from the users table
        c.execute("DELETE FROM users WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()


def get_user_status(user_id):
    # Connect to the chatbot database
    conn = sqlite3.connect('chatbot_database.db')
    c = conn.cursor()
    # Get the status of the user
    c.execute("SELECT status FROM users WHERE user_id=?", (user_id,))
    status = c.fetchone()[0]
    conn.close()
    return status


def set_user_status(user_id, new_status):
    # Connect to the chatbot database
    conn = sqlite3.connect('chatbot_database.db')
    c = conn.cursor()
    # Set the status of the user
    c.execute("UPDATE users SET status=? WHERE user_id=?", (new_status, user_id))
    conn.commit()
    conn.close()


def get_partner_id(user_id):
    # Connect to the chatbot database
    conn = sqlite3.connect('chatbot_database.db')
    c = conn.cursor()
    # If the user is a guest, then search for the host
    c.execute("SELECT user_id FROM users WHERE partner_id=?", (user_id,))
    other_user_id = c.fetchone()
    if not other_user_id:
        # If no user is found, return None
        conn.close()
        return None
    # otherwise, return the other user's id
    other_user_id = other_user_id[0]
    conn.close()

    return other_user_id


def couple(current_user_id):
    # Connect to the chatbot database
    conn = sqlite3.connect('chatbot_database.db')
    c = conn.cursor()
    # If the user is not the current one and is in search, then couple them
    c.execute("SELECT user_id FROM users WHERE status=? AND user_id!=?", (UserStatus.IN_SEARCH, current_user_id,))
    # Verify if another user in search is found
    other_user_id = c.fetchone()
    if not other_user_id:
        # If no user is found, return None
        return None
    # If another user in search is found, couple the users
    other_user_id = other_user_id[0]
    # Update both users' partner_id to reflect the coupling
    c.execute("UPDATE users SET partner_id=? WHERE user_id=?", (other_user_id, current_user_id))
    c.execute("UPDATE users SET partner_id=? WHERE user_id=?", (current_user_id, other_user_id))

    # Update both users' status to UserStatus.COUPLED
    c.execute("UPDATE users SET status=? WHERE user_id=?", (UserStatus.COUPLED, current_user_id))
    c.execute("UPDATE users SET status=? WHERE user_id=?", (UserStatus.COUPLED, other_user_id))

    conn.commit()
    conn.close()

    return other_user_id


def uncouple(user_id):
    # Connect to the chatbot database
    conn = sqlite3.connect('chatbot_database.db')
    c = conn.cursor()
    # Retrieve the partner_id of the user
    partner_id = get_partner_id(user_id)
    if not partner_id:
        # If the user is not coupled, return None
        return None

    # Update both users' partner_id to reflect the uncoupling
    c.execute("UPDATE users SET partner_id=NULL WHERE user_id=?", (user_id,))
    c.execute("UPDATE users SET partner_id=NULL WHERE user_id=?", (partner_id,))
    # Update both users' status to UserStatus.IDLE
    c.execute("UPDATE users SET status=? WHERE user_id=?", (UserStatus.IDLE, user_id))
    c.execute("UPDATE users SET status=? WHERE user_id=?", (UserStatus.IDLE, partner_id))
    conn.commit()
    conn.close()
    return


def retrieve_users_number():
    # Connect to the chatbot database
    conn = sqlite3.connect('chatbot_database.db')
    c = conn.cursor()
    # Retrieve the number of users in the users table
    c.execute("SELECT COUNT(*) FROM users")
    total_users_number = c.fetchone()[0]
    # Retrieve the number of users who are currently coupled
    c.execute("SELECT COUNT(*) FROM users WHERE status='coupled'")
    paired_users_number = c.fetchone()[0]
    conn.close()
    return total_users_number, paired_users_number


def reset_users_status():
    # Connect to the chatbot database
    conn = sqlite3.connect('chatbot_database.db')
    c = conn.cursor()
    # Reset the status of all users to UserStatus.IDLE
    c.execute("UPDATE users SET status=?", (UserStatus.IDLE,))
    conn.commit()
    conn.close()
