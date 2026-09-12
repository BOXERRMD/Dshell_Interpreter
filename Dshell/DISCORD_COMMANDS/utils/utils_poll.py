
from ...DshellParser.ast_nodes import ConstructPollNode, AnswerPollNode, PollNode, StrNode, IntNode, BoolNode, ListNode
from ...DISCORD_COMMANDS.utils.utils_type_validation import (_validate_required_int,
                                                            _validate_required_bool,
                                                            _validate_required_string,
                                                            _validate_required_list_node,
                                                            _validate_optional_string)
from ...DshellInterpreteur.utils_interpreter import regroupe_commandes
from ...full_import import Poll, PollAnswer, Any

async def build_poll(node: ConstructPollNode, interpreter: "DshellInterpreteur") -> PollNode:
    """
    Build a poll from a ConstructPollNode.
    """
    _CMD = "poll"

    args = await regroupe_commandes(node.body, interpreter)

    args_poll: dict[str, StrNode] = args.get_dict_parameters()

    question = args_poll.get('question', StrNode("No question provided"))
    duration = args_poll.get('duration', IntNode(24))
    multiselect = args_poll.get('multiselect', BoolNode(False))
    if len(node.answers) <= 10:
        answers = ListNode([await build_answer_poll(i, interpreter) for i in node.answers])
    else:
        raise ValueError("Too many answers for the poll.")

    _validate_required_string(question, "question", _CMD)
    _validate_required_int(duration, "duration", _CMD)
    _validate_required_bool(multiselect, "multiselect", _CMD)
    _validate_required_list_node(answers, "answers", _CMD)

    return PollNode(Poll(question=question, duration=duration, allow_multiselect=multiselect, answers=answers))

async def build_answer_poll(node: AnswerPollNode, interpreter: "DshellInterpreteur") -> PollAnswer:
    """
    Build an answer poll from an AnswerPollNode.
    """
    _CMD = "poll answer"

    args = await regroupe_commandes(node.body, interpreter)

    args_answer: list[Any] = args.get_non_specified_parameters()
    kwargs_answer: dict[str, StrNode] = args.get_dict_parameters()

    text = kwargs_answer.get('text', StrNode("No text provided") if not args_answer else args_answer[0])
    emoji = kwargs_answer.get('emoji', None if len(args_answer) < 2 else args_answer[1])

    _validate_required_string(text, "text", _CMD)
    _validate_optional_string(emoji, "emoji", _CMD)

    return PollAnswer(text=text, emoji=emoji)

