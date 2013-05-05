# vim: noai:ts=4:sw=4:expandtab:syntax=python

import traceback


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

        try:
            for i, elem in enumerate(self.bot.modules.modules['privmsg']):
                self.bot.modules.modules['privmsg'][elem].func(self.bot, event, event.arguments[0].split(), "")
        except:
            error_message = "Traceback (most recent call last):\n" + '\n'.join(traceback.format_exc().split("\n")[-4:-1])
            self.bot._debug(error_message, event=event)

        if event.arguments[0].startswith(self.bot.prefix):
            args = event.arguments[0][1:]
            commands = [s.strip() for s in args.split("|")]
            buf = ""

            for command in commands:
                cmdargs = [s.strip() for s in command.split()]
                command = cmdargs[0]
                cmdargs = cmdargs[1:]

                if self.bot.modules.modules['command'][command].privlevel == "admin":
                    if event.source.nick.lower() not in self.bot.config.get("bot", "owner").lower():
                        buf = "%s: Not authorized." % command
                        continue

                buf = self.bot.modules.modules['command'][command].func(self.bot, event, cmdargs, buf)

            self.bot._log("%s -> %s" % (event.target, buf), "out")

            lines = buf.split("\n")
            for index, line in enumerate(lines):
                if len(lines) > 5:
                    __import__("time").sleep(0.2)

                if index > 10:
                    client.privmsg(event.target, "[%d more lines omitted]" % (len(lines) - index))
                    break

                client.privmsg(event.target, line)
