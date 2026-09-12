from ..full_import import Message
from ..full_import import Union, Optional
from ..full_import import Forbidden, HTTPException
from ..DshellParser.ast_nodes import IntNode, StrNode, PollNode, ListNode, FloatNode

from .utils.utils_message import utils_get_message

async def dshell_get_poll(ctx: Message, message: Optional[Union[IntNode, StrNode]] = None):
    """
    Get a poll from a message.
    :param ctx:
    :param message:
    :return:
    """

    target_message = await utils_get_message(ctx, message) if message is not None else ctx

    return PollNode(target_message.poll) if target_message.poll is not None else None

async def dshell_end_poll(ctx: Message, target: Optional[Union[IntNode, StrNode, PollNode]] = None):
    """
    End a poll from a message.
    :param ctx:
    :param target:
    :return:
    """

    if isinstance(target, PollNode):
        target_poll = target.poll

        if target_poll is not None and not target_poll.has_ended():
            try:
                await target_poll.end()
            except Forbidden:
                raise PermissionError(f"I don't have the permission to end the poll '{target_poll.question}'")
            except HTTPException:
                raise RuntimeError(f"An error occurred while ending the poll '{target_poll.question}'")
            except RuntimeError:
                raise RuntimeError("This poll wasn't attached to a message")

        return IntNode(0) # Return a dummy value since we don't have a message ID in this case

    else:
        target_message = await utils_get_message(ctx, target) if target is not None else ctx
        target_poll = target_message.poll

        if target_poll is not None and not target_poll.has_ended():
            try:
                await target_poll.end()
            except Forbidden:
                raise PermissionError(f"I don't have the permission to end the poll on message {target_message.id}")
            except HTTPException:
                raise RuntimeError(f"An error occurred while ending the poll on message {target_message.id}")
            except RuntimeError:
                raise RuntimeError("This poll wasn't attached to a message")

        return IntNode(target_message.id)

async def dshell_get_question_poll(ctx: Message, target: Optional[Union[IntNode, StrNode, PollNode]] = None) -> Union[StrNode, None]:
    """
    Get the question of a poll from a message.
    :param ctx:
    :param target:
    :return:
    """

    if isinstance(target, PollNode):
        target_poll = target.poll

        if target_poll is None:
            return None

        return StrNode((target_poll.question.emoji or "") + " " + target_poll.question.text)

    else:
        target_message = await utils_get_message(ctx, target) if target is not None else ctx
        target_poll = target_message.poll

        if target_poll is None:
            return None

        return StrNode((target_poll.question.emoji or "") + " " + target_poll.question.text)


async def dshell_get_answers_poll(ctx: Message, target: Optional[Union[IntNode, StrNode, PollNode]] = None) -> Union[ListNode, None]:
    """
    Get the answers of a poll from a message.
    :param ctx:
    :param target:
    :return:
    """

    if isinstance(target, PollNode):
        target_poll = target.poll

        if target_poll is None:
            return None

        return PollNode(target_poll).get_answers()

    else:
        target_message = await utils_get_message(ctx, target) if target is not None else ctx
        target_poll = target_message.poll

        if target_poll is None:
            return None

        return PollNode(target_poll).get_answers()


async def dshell_get_results_poll(ctx: Message, target: Optional[Union[IntNode, StrNode, PollNode]] = None) -> Union[ListNode, None]:
    """
    Get the results of a poll from a message.
    :param ctx:
    :param target:
    :return:
    """

    if isinstance(target, PollNode):
        target_poll = target.poll

        if target_poll is None:
            return None

        return PollNode(target_poll).get_results()

    else:

        target_message = await utils_get_message(ctx, target) if target is not None else ctx

        target_poll = target_message.poll

        if target_poll is None:
            return None

        return PollNode(target_poll).get_results()

async def dshell_get_total_results_poll(ctx: Message, target: Optional[Union[IntNode, StrNode, PollNode]] = None) -> Union[IntNode, None]:
    """
    Get the total number of votes in a poll from a message.
    :param ctx:
    :param target:
    :return:
    """

    if isinstance(target, PollNode):
        target_poll = target.poll

        if target_poll is None:
            return None

        return PollNode(target_poll).get_total_results()

    else:

        target_message = await utils_get_message(ctx, target) if target is not None else ctx

        target_poll = target_message.poll

        if target_poll is None:
            return None

        return PollNode(target_poll).get_total_results()

async def dshell_get_expiry_poll(ctx: Message, target: Optional[Union[IntNode, StrNode, PollNode]] = None) -> Union[FloatNode, None]:
    """
    Get the expiry time of a poll from a message.
    :param ctx:
    :param target:
    :return:
    """

    if isinstance(target, PollNode):
        target_poll = target.poll

        if target_poll is None:
            return None

        return PollNode(target_poll).get_expiry()

    else:

        target_message = await utils_get_message(ctx, target) if target is not None else ctx

        target_poll = target_message.poll

        if target_poll is None:
            return None

        return PollNode(target_poll).get_expiry()