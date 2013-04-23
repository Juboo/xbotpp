# vim: noai:ts=4:sw=4:expandtab:syntax=python


class BotIO:
    """\
    Class handling the IO functions of xbot++.
    """

    def __init__(self, bot):
        self.bot = bot

    def read(self, client, event):
        """\
        Reads input from an IRC event (like a channel message), calls message-bound modules, and determines
        if any command modules need to be executed.

        If the received message starts with the bot prefix character, this function assumes that the message
        is a bot command string.

        Handling of bot commands flows as following:

        (1)
            Split the message by the pipe character (``|``), and treat each segment as a separate command
            in a sequence of commands.

        (2)
            Take the first word of a command as the command's name, and search for the command in the
            dictionary of known commands.

        (3)
            If the command exists, check that the user executing the command has the privileges to do so,
            stopping execution if he does not.

        (4)
            Execute the command, storing the output of the command in the buffer, and passing the arguments
            passed and the output buffer of the previously executed command in the sequence to the command,
            if any.

        (5)
            If there are any commands in the sequence left to be executed, jump to (2).

        :param client: the :py:class:`irc.client` that received the command
        :type client: :py:class:`irc.client`
        :param event: the :py:class:`irc.client.Event` that triggered this function
        :type event: :py:class:`irc.client.Event`
        """

        for i, elem in enumerate(self.bot.modules.modules['privmsg']):
            self.bot.modules.modules['privmsg'][elem][0](self.bot, event, event.arguments[0].split(), "")

        if event.arguments[0].startswith(self.bot.prefix):
            args = event.arguments[0][1:]
            commands = [s.strip() for s in args.split("|")]
            buf = ""

            for command in commands:
                cmdargs = [s.strip() for s in command.split()]
                command = cmdargs[0]
                cmdargs = cmdargs[1:]

                if self.bot.modules.modules['command'][command][1] == "admin":
                    if event.source.nick.lower() not in self.bot.config.get("bot", "owner").lower():
                        buf = "%s: Not authorized." % command
                        continue

                buf = self.bot.modules.modules['command'][command][0](self.bot, event, cmdargs, buf)

            self.bot._log("%s -> %s" % (event.target, buf), "out")
            for line in buf.split("\n"):
                client.privmsg(event.target, line)
