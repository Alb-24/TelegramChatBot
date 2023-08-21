import logging
from telegram import Update
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, MessageHandler
from my_data import MyData, Status

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

"""
####### List of commands #######
---> start - 🤖 starts the bot
---> chat - 💬 start searching for a partner
---> exit - 🔚 exit from the chat
---> newchat - ⏭ exit from the chat and open a new one
---> stats - 📊 show bot statistics (only for admin)
"""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Welcomes the user and sets his/her status to idle if he/she is not already in the database
    :param update: update received from the user
    :param context: context of the bot
    :return: status USER_ACTION
    """
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Welcome to this ChatBot! 🤖\nType /chat to start searching for a partner")

    if my_data.get_user_status(user_id=update.effective_chat.id) is None:
        my_data.set_user_status(user_id=update.effective_user.id, new_status=Status.IDLE)
        my_data.add_user(user_id=update.effective_user.id)

    return USER_ACTION


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Define the action to do based on the message received and the actual status of the user
    :param update: update received from the user
    :param context: context of the bot
    :return: None
    """

    if my_data.get_user_status(user_id=update.effective_user.id) == Status.COUPLED:
        # check if the user was paired by another one; if so, retrieve him/her
        other_user_id = my_data.search_partner_of(update.effective_user.id)
        if other_user_id is None:
            return await handle_not_in_chat(update, context)
        else:
            return await in_chat(update, other_user_id)
    else:
        return await handle_not_in_chat(update, context)


async def handle_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the /chat command, starting the search for a partner if the user is not already in search
    :param update: update received from the user
    :param context: context of the bot
    :return: None
    """
    # Handle the command /chat in different cases, based on the status of the user
    current_user = update.effective_user.id
    if my_data.get_user_status(user_id=current_user) == Status.PARTNER_LEFT:
        # First, check if the user has been left by his/her partner (he/she would have updated this user's status to
        # PARTNER_LEFT)
        my_data.set_user_status(user_id=current_user, new_status=Status.IDLE)

        return await start_search(update, context)
    elif my_data.get_user_status(user_id=current_user) == Status.IN_SEARCH:
        # Warn him/her that he/she is already in search
        return await handle_already_in_search(update, context)
    # If the status is not IN_SEARCH or PARTNER_LEFT, then the user is either IDLE or COUPLED, so check if he/she has
    # a partner
    other_user = my_data.search_partner_of(current_user)

    if other_user is not None:
        # If the user has been paired, then he/she is already in a chat, so warn him/her
        await context.bot.send_message(chat_id=current_user,
                                       text="🤖 You are already in a chat, type /exit to exit from the chat.")
        return None

    else:
        # Else, the user is in IDLE status, so simply start the search
        return await start_search(update, context)


async def handle_not_in_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the case when the user is not in chat
    :param update: update received from the user
    :param context: context of the bot
    :return: None
    """
    current_user = update.effective_user.id
    if my_data.get_user_status(user_id=current_user) in [Status.IDLE, Status.PARTNER_LEFT]:
        await context.bot.send_message(chat_id=current_user,
                                       text="🤖 You are not in a chat, type /chat to start searching for a partner.")
        return
    elif my_data.get_user_status(user_id=current_user) == Status.IN_SEARCH:
        await context.bot.send_message(chat_id=current_user,
                                       text="🤖 Message not delivered, you are still in search!")
        return


async def handle_already_in_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the case when the user is already in search
    :param update: update received from the user
    :param context: context of the bot
    :return: None
    """
    await context.bot.send_message(chat_id=update.effective_chat.id, text="🤖 You are already in search!")
    return


async def start_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Starts the search for a partner, setting the user status to in_search and adding him/her to the list of users
    :param update: update received from the user
    :param context: context of the bot
    :return: None
    """
    current_user = update.effective_user.id
    my_data.set_user_status(user_id=current_user, new_status=Status.IN_SEARCH)

    await context.bot.send_message(chat_id=current_user, text="🤖 Searching for a partner...")
    user_id = update.effective_chat.id
    logging.info("User %d started a search", user_id)

    if await retrieve_coupling_partner(update, context):
        # If the user has been paired, then simply return
        return
    else:
        logging.info("User: " + str(current_user) + " NOT PAIRED, no other partner in search")
        return


async def retrieve_coupling_partner(update, context) -> bool:
    """
    Retrieves the coupling partner for the current_user, if any
    :param update: update received from the user
    :param context: context of the bot
    :return: Boolean value, True if the user has been paired, False otherwise
    """
    current_user = update.effective_chat.id

    user_id = my_data.couple(current_user_id=current_user)

    if user_id is not None:
        # Send the message to both the users
        await context.bot.send_message(chat_id=current_user, text="🤖 You have been paired with an user")
        await context.bot.send_message(chat_id=user_id, text="🤖 You have been paired with an user")
        # Update their status to coupled
        my_data.set_user_status(user_id=current_user, new_status=Status.COUPLED)
        my_data.set_user_status(user_id=user_id, new_status=Status.COUPLED)

        return True
    else:
        return False


async def handle_exit_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the /exit command, exiting from the chat if the user is in chat
    :param update: update received from the user
    :param context: context of the bot
    :return: None
    """
    await exit_chat(update, context)
    return


async def handle_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the /stats command, showing the bot statistics if the user is the admin
    :param update: update received from the user
    :param context: context of the bot
    :return: None
    """
    await my_data.stats(context=context, user_id=update.effective_user.id)
    return


async def exit_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Exits from the chat, sending a message to the other user and updating the status of both the users
    :param update: update received from the user
    :param context: context of the bot
    :return: a boolean value, True if the user was in chat (and so exited), False otherwise
    """
    current_user = update.effective_user.id
    if my_data.get_user_status(user_id=current_user) != Status.COUPLED:
        await context.bot.send_message(chat_id=current_user, text="🤖 You are not in a chat!")
        return False

    other_user = my_data.search_partner_of(current_user)
    if other_user is None:
        return False

    await context.bot.send_message(chat_id=current_user, text="🤖 Ending chat...")
    await context.bot.send_message(chat_id=other_user,
                                   text="🤖 Your partner has left the chat, type /chat to start searching for a new "
                                        "partner.")
    await update.message.reply_text("🤖 You have left the chat.")

    my_data.set_user_status(user_id=current_user, new_status=Status.IDLE)
    my_data.set_user_status(user_id=other_user, new_status=Status.PARTNER_LEFT)

    my_data.remove_paired_users(user_id=current_user, partner_id=other_user)

    return True


async def exit_then_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the /newchat command, exiting from the chat and starting a new search if the user is in chat
    :param update: update received from the user
    :param context: context of the bot
    :return: None
    """
    current_user = update.effective_user.id
    if my_data.get_user_status(user_id=current_user) == Status.IN_SEARCH:
        return await handle_already_in_search(update, context)
    # If exit_chat returns True, then the user was in chat and successfully exited
    if await exit_chat(update, context):
        logging.info("User: " + str(current_user) + " LEFT the chat")
    # Either the user was in chat or not, start the search
    return await start_search(update, context)


async def in_chat(update: Update, other_user_id) -> None:
    """
    Handles the case when the user is in chat
    :param update: update received from the user
    :param other_user_id: id of the other user in chat
    :return: None
    """
    # Check if the message is a reply to another message
    if update.message.reply_to_message is not None:
        # If the message is a reply to another message, check if the message is a reply to a message sent by the user
        # himself or by the other user
        if update.message.reply_to_message.from_user.id == update.effective_user.id:
            # The message is a reply to a message sent by the user himself, so send the message to the replyed+1
            # message (the one copyed by the bot has id+1)
            await update.effective_chat.copy_message(chat_id=other_user_id, message_id=update.message.message_id,
                                                     protect_content=True,
                                                     reply_to_message_id=update.message.reply_to_message.message_id + 1)
        # Check if the message is a reply to a message sent by the other user that is actual in chat
        elif update.message.reply_to_message.from_user.id == other_user_id:
            # The message is a reply to a message sent by the other user, so send the message to the replyed-1
            # message (the one copied by the bot has id-1)
            await update.effective_chat.copy_message(chat_id=other_user_id, message_id=update.message.message_id,
                                                     protect_content=True,
                                                     reply_to_message_id=update.message.reply_to_message.message_id - 1)
        else:
            # The message is a reply to a message sent by another user, so send the message without replying
            await update.effective_chat.copy_message(chat_id=other_user_id, message_id=update.message.message_id,
                                                     protect_content=True)
    else:
        # The message is not a reply to another message, so send the message without replying
        await update.effective_chat.copy_message(other_user_id, update.message.message_id, protect_content=True)
    return


# Define status for the conversation handler
USER_ACTION = 0

if __name__ == '__main__':
    my_data = MyData()
    application = ApplicationBuilder().token(my_data.token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            USER_ACTION: [
                MessageHandler(
                    (filters.TEXT | filters.ATTACHMENT) & ~ filters.COMMAND & ~filters.Regex("exit") & ~filters.Regex(
                        "chat")
                    & ~filters.Regex("newchat") & ~filters.Regex("stats"),
                    handle_message),
                CommandHandler("exit", handle_exit_chat),
                CommandHandler("chat", handle_chat),
                CommandHandler("newchat", exit_then_chat),
                CommandHandler("stats", handle_stats)]
        },
        fallbacks=[MessageHandler(filters.TEXT, handle_not_in_chat)]
    )
    application.add_handler(conv_handler)
    application.run_polling()
