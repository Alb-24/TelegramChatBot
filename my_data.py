import logging
import config  # Import the config file, where the bot token and the admin id are stored


# This class is used to store the data of the bot, like the token, the admin id, the list of paired users and
# the list of active users
class MyData:
    def __init__(self):
        self._token = config.BOT_TOKEN
        self._admin_id = config.ADMIN_ID
        self._list_paired = {}
        self._list_users = []

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, value):
        raise PermissionError("Cannot directly access this value")

    @property
    def admin_id(self):
        return self._admin_id

    @admin_id.setter
    def admin_id(self, value):
        raise PermissionError("Cannot directly access this value")

    @property
    def list_paired(self):
        raise PermissionError("Cannot directly access this value, use the related functions")

    @property
    def list_users(self):
        raise PermissionError("Cannot directly access this value, use the related functions")

    def add_user(self, user_id):
        """
        Adds a user to the list of active users
        :param user_id: id of the user to add
        :return: a boolean value, True if the user is added, False if not because he/she is already present
        """
        if user_id not in self._list_users:
            self._list_users.append(user_id)
            return True
        else:
            return False

    def remove_user(self, user_id):
        """
        Removes a user from the list of active users
        :param user_id: id of the user to remove
        :return: a boolean value, True if the user is removed, False if not because he/she is not present
        """
        if user_id in self._list_users:
            self._list_users.remove(user_id)
            return True
        else:
            return False

    def remove_paired_user(self, user_id):
        """
        Removes a user from the list of paired users
        :param user_id: id of the user to remove
        :return: None
        """
        del self._list_paired[user_id]

    def return_list_users(self, user_id):
        """
        Returns the list of all the users, only to the admin
        :return: list of all the users
        """
        if user_id == self._admin_id:
            return self._list_users

    def get_host_users(self):
        """
        Returns the list of users who made the pair, being the "host" of the conversation
        :return: list of pairing users
        """
        return self._list_paired.keys()

    def get_guest_users(self):
        """
        Returns the list of users that have already been paired by someone else, being the "guest" of the pairing
        :return:
        """
        return self._list_paired.values()

    def set_partner_of(self, host_user_id, guest_user_id):
        """
        Sets the partner of a user
        :param host_user_id: id of the user who has retrieved the guest and made the pairing
        :param guest_user_id: id of the user who has been paired by the guest
        :return: None
        """
        self._list_paired[host_user_id] = guest_user_id

    async def stats(self, context, user_id):
        """
        Sends the stats of the bot to the user, if the user is the admin
        :param context: context of the message
        :param user_id: id of the user who sent the message
        :return: None
        """
        if user_id == self._admin_id:
            await context.bot.send_message(chat_id=user_id, text="Welcome to the admin panel")
            await context.bot.send_message(chat_id=user_id,
                                           text="Number of paired users: " + str(len(self._list_paired)))
            await context.bot.send_message(chat_id=user_id,
                                           text="Number of active users: " + str(len(self._list_users)))
        else:
            logging.warning("User " + str(user_id) + " tried to access the admin panel")

    def search_partner_of(self, user_id):
        """
        Returns the partner of a user, if present
        :param user_id: id of the user to search the partner of
        :return: The id of the partner, None if not found
        """
        if user_id in self.get_guest_users():
            # if the user is a guest, then search for the host
            for host, guest in self._list_paired.items():
                if guest == user_id:
                    return host
        elif user_id in self.get_host_users():
            # if the user is a host, then search for the guest
            return self._list_paired[user_id]
        else:
            return None

    def couple(self, current_user_id, context):
        """
        Couples a user with another one who is also in search, if present
        :param current_user_id: id of the user to couple
        :param context: context of the message
        :return: the id of the coupled user, None if not found
        """
        for other_user_id in self._list_users:
            # If the user is not the current one and is in search, then couple them
            if self.get_user_status(context, user_id=other_user_id) == "in_search" and other_user_id != current_user_id:
                # The current user will be the host (coupling user), while the other one the guest (coupled user)
                self.set_partner_of(host_user_id=current_user_id, guest_user_id=other_user_id)

                return other_user_id
        return None

    @staticmethod
    def get_user_status(context, user_id):
        return context.bot_data.get(str(user_id) + '_status', None)
