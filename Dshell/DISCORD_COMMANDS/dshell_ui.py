from Dshell.full_import import (ButtonStyle,
                           PrivateChannel,
                           Interaction,
                           ui,
                           MISSING,
                           EasyModifiedViews,
                           CustomIDNotFound,
                           SelectMenu,
                           ComponentType,
                           random)

from ..DshellParser.ast_nodes import UiSelectNode, UiButtonNode, OptionUiSelectNode, ListNode, StrNode, IntNode, BoolNode

from ..DshellInterpreteur.utils_interpreter import regroupe_commandes

from ..DshellInterpreteur.dshell_scope import new_scope, get_scope, update_nbr_usage_scope, get_usage_scope

from Dshell.full_import import Any, TYPE_CHECKING, Union, Optional

from .utils.utils_type_validation import (_validate_optional_code_node,
                                          _validate_required_int,
                                          _validate_optional_int,
                                          _validate_optional_string,
                                          _validate_required_string,
                                          _validate_required_bool,
                                          _validate_missing_or_type)

from .utils.utils_global import utils_refactor_emoji

if TYPE_CHECKING:
    from ..DshellInterpreteur.dshell_interpreter import DshellInterpreteur

scope_id = "scope_id"

ButtonStyleValues: set = {i.name for i in ButtonStyle}
SelectSyleValues: dict = {'string': ComponentType.string_select,
                          'role': ComponentType.role_select,
                          'user': ComponentType.user_select,
                          'mention': ComponentType.mentionable_select,
                          'channel': ComponentType.channel_select}

async def build_ui_button_parameters(ui_button_node: UiButtonNode, interpreter: "DshellInterpreteur"):
    """
    Builds the parameters for a UI component from the UiNode.
    Can accept buttons and select menus.
    :param ui_node:
    :param interpreter:
    :return:
    """
    _CMD = "button"

    regrouped_parameters = await regroupe_commandes(ui_button_node.body, interpreter, normalise=True)
    args_button: dict[str, list[Any]] = regrouped_parameters.get_dict_parameters()

    code = args_button.pop('code', None)
    style = StrNode(args_button.pop('style', 'primary').lower())
    custom_id = args_button.pop('custom_id', StrNode('ui_button_'+str(random())))
    row = args_button.pop('row', IntNode(0))
    emoji = utils_refactor_emoji(args_button.pop('emoji', None))

    _validate_optional_code_node(code, "code", _CMD)
    _validate_required_string(style, "style", _CMD)
    _validate_required_string(custom_id, "custom_id", _CMD)
    _validate_required_int(row, "row", _CMD)
    _validate_optional_string(emoji, "emoji", _CMD)

    if style not in ButtonStyleValues:
        raise ValueError(f"Button style must be one of {', '.join(ButtonStyleValues)}, not '{style}' !")

    args_button['custom_id'] = custom_id
    args_button['row'] = row
    args_button['style'] = ButtonStyle[style]
    args_button['emoji'] = emoji
    args = args_button.pop('*', ())
    yield args, args_button, code


async def build_ui_select_parameters(ui_select_node: UiSelectNode, interpreter: "DshellInterpreteur"):
    """
    Builds the parameters for a UI select menu from the UiNode.
    :param ui_select_node:
    :param interpreter:
    :return:
    """
    _CMD = "select"

    regrouped_parameters = await regroupe_commandes(ui_select_node.body, interpreter, normalise=True)
    args_select: dict[str, list[Any]] = regrouped_parameters.get_dict_parameters()

    code = args_select.pop('code', None)
    custom_id = args_select.pop('custom_id', StrNode('ui_select_'+str(random())))
    select_type = StrNode(args_select.pop('type', 'string').lower())

    disabled = args_select.get('disabled', BoolNode(0))
    max_values = args_select.get('max', IntNode(1))
    min_values = args_select.get('min', IntNode(1))
    placeholder = args_select.get('placeholder', StrNode(""))
    row = args_select.pop('row', IntNode(0))

    _validate_optional_code_node(code, "Select code", _CMD)
    _validate_required_string(custom_id, "custom_id", _CMD)
    _validate_required_string(select_type, "type", _CMD)
    _validate_required_bool(disabled, "disabled", _CMD)
    _validate_required_int(max_values, "max", _CMD)
    _validate_required_int(max_values, "min", _CMD)
    _validate_required_string(placeholder, "placeholder", _CMD)
    _validate_optional_int(row, "row", _CMD)

    if select_type not in SelectSyleValues:
        raise TypeError(f"Select style must be one of {', '.join(SelectSyleValues.keys())}, not '{select_type}' !")

    args_select["disabled"] = disabled
    args_select["max_values"] = max_values
    args_select["min_values"] = min_values
    args_select["options"] = await build_ui_select_options(ui_select_node.options, interpreter)
    args_select["placeholder"] = placeholder
    args_select["row"] = row
    args_select["type"] = SelectSyleValues[select_type]
    args_select['custom_id'] = custom_id
    args = args_select.pop('*', ())

    yield args, args_select, code

async def build_ui_select_options(option_nodes: list[OptionUiSelectNode], interpreter: "DshellInterpreteur"):
    """
    Builds the options for a UI select menu from the OptionUiSelectNode.
    :param option_nodes:
    :param interpreter:
    :return:
    """
    _CMD = "option"

    option_results: list[dict[str, Any]] = []

    for option_node in option_nodes:
        regrouped_parameters = await regroupe_commandes(option_node.body, interpreter, normalise=True)
        args_option: dict[str, list[Any]] = regrouped_parameters.get_dict_parameters()

        label = args_option.pop('label', None)
        value = args_option.pop('value', MISSING)
        description = args_option.pop('description', None)
        emoji = utils_refactor_emoji(args_option.pop('emoji', None))
        default = args_option.pop('default', False)

        _validate_required_string(label, "label", _CMD)
        _validate_missing_or_type(value, "value", StrNode, _CMD)
        _validate_optional_string(description, "description", _CMD)
        _validate_optional_string(emoji, "emoji", _CMD)
        _validate_required_bool(default, "default", _CMD)

        if len(label) > 100:
            raise ValueError("Option label must be less than 100 characters !")

        if value and len(value) > 100:
            raise ValueError("Option value must be less than 100 characters !")

        if description is not None and len(description) > 100:
            raise ValueError("Option description must be less than 100 characters !")

        option_dict = {
            'label': label,
            'value': value,
            'description': description,
            'emoji': emoji,
            'default': default,
        }
        option_results.append(option_dict)

    return option_results


async def build_ui(ui_node: Union[UiButtonNode, UiSelectNode], interpreter: "DshellInterpreteur") -> EasyModifiedViews:
    """
    Builds a UI component from the UiNode.
    Can accept buttons and select menus.
    :param ui_node:
    :param interpreter:
    :return:
    """

    async def ui_timeout(ctx):
        update_nbr_usage_scope(interpreter.scope_id, -1)

    view = EasyModifiedViews(timeout=600, call_on_timeout=ui_timeout, disabled_on_timeout=True)

    if isinstance(ui_node, UiButtonNode):
        async for _, args_button, code in build_ui_button_parameters(ui_node, interpreter):
            b = ui.Button(**args_button)
            view.add_items(b)
            view.set_callable(b.custom_id, _callable=ui_button_callback, data={'code': code, scope_id: interpreter.scope_id})
        update_nbr_usage_scope(interpreter.scope_id, 1)

    elif isinstance(ui_node, UiSelectNode):
        s = SelectMenu()
        async for _, args_select, code in build_ui_select_parameters(ui_node, interpreter):

            options = args_select.pop("options", [])
            select_type = args_select.pop("type")

            if select_type == ComponentType.string_select:
                menu = s.add_string_select_menu(**args_select)

                for option in options:
                    menu.add_option(**option)

                s.set_callable(args_select["custom_id"], _callable=ui_select_callback, data={'code': code, scope_id: interpreter.scope_id})

            elif select_type == ComponentType.role_select:
                s.add_role_select_menu(**args_select)
                s.set_callable(args_select["custom_id"], _callable=ui_select_callback, data={'code': code, scope_id: interpreter.scope_id})

            elif select_type == ComponentType.user_select:
                s.add_user_select_menu(**args_select)
                s.set_callable(args_select["custom_id"], _callable=ui_select_callback, data={'code': code, scope_id: interpreter.scope_id})

            elif select_type == ComponentType.mentionable_select:
                s.add_mentionable_select_menu(**args_select)
                s.set_callable(args_select["custom_id"], _callable=ui_select_callback, data={'code': code, scope_id: interpreter.scope_id})

            elif select_type == ComponentType.channel_select:
                s.add_channel_select_menu(**args_select)
                s.set_callable(args_select["custom_id"], _callable=ui_select_callback, data={'code': code, scope_id: interpreter.scope_id})

        view.add_items(s)
        update_nbr_usage_scope(interpreter.scope_id, 1)

    else:
        raise TypeError(f"UI node must be UiButtonNode or UiSelectNode, not {type(ui_node)} !")

    return view


async def rebuild_ui(ui_node: Union[UiButtonNode, UiSelectNode], view: EasyModifiedViews, interpreter: "DshellInterpreteur") -> EasyModifiedViews:
    """
    Rebuilds a UI component from an existing EasyModifiedViews.
    :param view:
    :param interpreter:
    :return:
    """
    if isinstance(ui_node, UiButtonNode):

        async for args, args_button, code in build_ui_button_parameters(ui_node, interpreter):
            try:
                ui: ui.Button = view.get_ui(args_button['custom_id'])
            except CustomIDNotFound:
                raise ValueError(f"Button with custom_id '{args_button['custom_id']}' not found in the view !")

            ui.label = args_button.get('label', ui.label)
            ui.style = args_button.get('style', ui.style)
            ui.emoji = args_button.get('emoji', ui.emoji)
            ui.disabled = args_button.get('disabled', ui.disabled)
            ui.url = args_button.get('url', ui.url)
            ui.row = args_button.get('row', ui.row)
            new_code = code if code is not None else view.get_callable_data(args_button['custom_id'])['code']
            view.set_callable(args_button['custom_id'], _callable=ui_button_callback, data={'code': new_code, scope_id: interpreter.scope_id})

    elif isinstance(ui_node, UiSelectNode):

        async for args, args_select, code in build_ui_select_parameters(ui_select_node=ui_node, interpreter=interpreter):
            try:
                ui: ui.Select = view.get_ui(args_select['custom_id'])
            except CustomIDNotFound:
                raise ValueError(f"Select menu with custom_id '{args_select['custom_id']}' not found in the view !")

            ui.placeholder = args_select.get('placeholder', ui.placeholder)
            ui.min_values = args_select.get('min_values', ui.min_values)
            ui.max_values = args_select.get('max_values', ui.max_values)
            ui.disabled = args_select.get('disabled', ui.disabled)

            ui.options.clear()
            options = args_select.pop("options", [])
            for option in options:
                ui.add_option(**option)

            new_code = code if code is not None else view.get_callable_data(args_select['custom_id'])['code']
            view.set_callable(args_select['custom_id'], _callable=ui_select_callback, data={'code': new_code, scope_id: interpreter.scope_id})

    return view


async def ui_button_callback(button: ui.Button, interaction: Interaction, data: dict[str, Any]):
    """
    Callback for UI buttons.
    Executes the code associated with the button.
    :param button:
    :param interaction:
    :param data:
    :return:
    """
    code = data.get('code', None)
    scope: Optional[str] = data.get(scope_id, None)

    if code is not None:
        message = interaction
        local_env = {
            '__ret__': None,  # environment variables, '__ret__' is used to store the return value of commands
            '__loop__': None,  # used to store the current loop variable in loop nodes if the loop identifier is not specified
            '__break__': BoolNode(0), # used to break a loop

            '__author__': IntNode(message.user.id),
            '__author_name__': StrNode(message.user.name),
            '__author_display_name__': StrNode(message.user.display_name),
            '__author_avatar__': StrNode(message.user.display_avatar.url) if message.user.display_avatar else None,
            '__author_discriminator__': StrNode(message.user.discriminator),
            '__author_bot__': BoolNode(message.user.bot),
            '__author_nick__': StrNode(message.user.nick) if hasattr(message.user, 'nick') else None,
            '__author_id__': IntNode(message.user.id),
            '__author_add_reaction__': None, # Can be overwritten by add vars_env parameter to get the author on message add event reaction
            '__author_remove_reaction__': None, # Can be overwritten by add vars_env parameter to get the author on message remove event reaction

            '__message__': StrNode(message.message.content),
            '__message_content__': StrNode(message.message.content),
            '__message_id__': IntNode(message.message.id),
            '__message_author__': IntNode(message.message.author.id),
            '__message_before__': StrNode(message.message.content),  # same as __message__, but before edit. Can be overwritten by add vars_env parameter
            '__message_created_at__': StrNode(message.message.created_at),
            '__message_edited_at__': StrNode(message.message.edited_at),
            '__message_reactions__': ListNode([StrNode(reaction.emoji) for reaction in message.message.reactions], bypass_limit_elt=True, editable=False),
            '__message_add_reaction__': None, # Can be overwritten by add vars_env parameter to get the reaction added on message add event reaction
            '__message_remove_reaction__': None, # Can be overwritten by add vars_env parameter to get the reaction removed on message remove event reaction
            '__message_url__': StrNode(message.message.jump_url) if hasattr(message.message, 'jump_url') else None,
            '__last_message__': IntNode(message.message.channel.last_message_id),

            '__channel__': IntNode(message.message.channel.id),
            '__channel_name__': StrNode(message.message.channel.name),
            '__channel_type__': StrNode(message.message.channel.type.name) if hasattr(message.message.channel, 'type') else None,
            '__channel_id__': IntNode(message.message.channel.id),
            '__private_channel__': BoolNode(isinstance(message.message.channel, PrivateChannel)),
        }

        if message.guild is not None:
            local_env.update(
                {
            '__guild__': IntNode(message.channel.guild.id),
            '__guild_name__': StrNode(message.channel.guild.name),
            '__guild_id__': IntNode(message.channel.guild.id),
            '__guild_members__': ListNode([IntNode(member.id) for member in message.channel.guild.members], bypass_limit_elt=True, editable=False),
            '__guild_member_count__': IntNode(message.channel.guild.member_count),
            '__guild_icon__': StrNode(message.channel.guild.icon.url) if message.channel.guild.icon else None,
            '__guild_owner_id__': IntNode(message.channel.guild.owner_id),
            '__guild_description__': StrNode(message.channel.guild.description),
            '__guild_roles__': ListNode([IntNode(role.id) for role in message.channel.guild.roles], bypass_limit_elt=True, editable=False),
            '__guild_roles_count__': IntNode(len(message.channel.guild.roles)),
            '__guild_emojis__': ListNode([IntNode(emoji.id) for emoji in message.channel.guild.emojis], bypass_limit_elt=True, editable=False),
            '__guild_emojis_count__': IntNode(len(message.channel.guild.emojis)),
            '__guild_channels__': ListNode([IntNode(channel.id) for channel in message.channel.guild.channels], bypass_limit_elt=True, editable=False),
            '__guild_text_channels__': ListNode([IntNode(channel.id) for channel in message.channel.guild.text_channels], bypass_limit_elt=True, editable=False),
            '__guild_voice_channels__': ListNode([IntNode(channel.id) for channel in message.channel.guild.voice_channels], bypass_limit_elt=True, editable=False),
            '__guild_categories__': ListNode([IntNode(channel.id) for channel in message.channel.guild.categories], bypass_limit_elt=True, editable=False),
            '__guild_stage_channels__': ListNode([IntNode(channel.id) for channel in message.channel.guild.stage_channels], bypass_limit_elt=True, editable=False),
            '__guild_forum_channels__': ListNode([IntNode(channel.id) for channel in message.channel.guild.forum_channels], bypass_limit_elt=True, editable=False),
            '__guild_channels_count__': IntNode(len(message.channel.guild.channels)),
                }
            )
        else:
            local_env.update(
                {
            '__guild__': None,
            '__guild_name__': None,
            '__guild_id__': None,
            '__guild_members__': None,
            '__guild_member_count__': None,
            '__guild_icon__': None,
            '__guild_owner_id__': None,
            '__guild_description__': None,
            '__guild_roles__': None,
            '__guild_roles_count__': None,
            '__guild_emojis__': None,
            '__guild_emojis_count__': None,
            '__guild_channels__': None,
            '__guild_text_channels__': None,
            '__guild_voice_channels__': None,
            '__guild_categories__': None,
            '__guild_stage_channels__': None,
            '__guild_forum_channels__': None,
            '__guild_channels_count__': None,
                }
            )

        from ..DshellInterpreteur.dshell_interpreter import DshellInterpreteur

        new_interpreter = DshellInterpreteur(
            code,
            ctx=interaction,
            debug=False,
            vars_env=scope)

        with new_scope(new_interpreter, local_env):
            await new_interpreter.execute()

    else:
        await interaction.response.defer(invisible=True)


async def ui_select_callback(select: ui.Select, interaction: Interaction, data: dict[str, Any]):
    """
    Callback for UI select menus.
    Executes the code associated with the select menu.
    :param select:
    :param interaction:
    :param data:
    :return:
    """
    code = data.get('code', None)
    scope: Optional[str] = data.get(scope_id, None)

    message = interaction
    if code is not None:
        local_env = {
            '__values__': ListNode([IntNode(i.id) for i in select.values]) if select.values and hasattr(
                select.values[0], 'id') else ListNode(StrNode(i) for i in select.values),
            '__ret__': None,  # environment variables, '__ret__' is used to store the return value of commands
            '__loop__': None,
            # used to store the current loop variable in loop nodes if the loop identifier is not specified
            '__break__': BoolNode(0),  # used to break a loop

            '__author__': IntNode(message.user.id),
            '__author_name__': StrNode(message.user.name),
            '__author_display_name__': StrNode(message.user.display_name),
            '__author_avatar__': StrNode(message.user.display_avatar.url) if message.user.display_avatar else None,
            '__author_discriminator__': StrNode(message.user.discriminator),
            '__author_bot__': BoolNode(message.user.bot),
            '__author_nick__': StrNode(message.user.nick) if hasattr(message.user, 'nick') else None,
            '__author_id__': IntNode(message.user.id),
            '__author_add_reaction__': None,
            # Can be overwritten by add vars_env parameter to get the author on message add event reaction
            '__author_remove_reaction__': None,
            # Can be overwritten by add vars_env parameter to get the author on message remove event reaction

            '__message__': StrNode(message.message.content),
            '__message_content__': StrNode(message.message.content),
            '__message_id__': IntNode(message.message.id),
            '__message_author__': IntNode(message.message.author.id),
            '__message_before__': StrNode(message.message.content),
            # same as __message__, but before edit. Can be overwritten by add vars_env parameter
            '__message_created_at__': StrNode(message.message.created_at),
            '__message_edited_at__': StrNode(message.message.edited_at),
            '__message_reactions__': ListNode([StrNode(reaction.emoji) for reaction in message.message.reactions],
                                              bypass_limit_elt=True, editable=False),
            '__message_add_reaction__': None,
            # Can be overwritten by add vars_env parameter to get the reaction added on message add event reaction
            '__message_remove_reaction__': None,
            # Can be overwritten by add vars_env parameter to get the reaction removed on message remove event reaction
            '__message_url__': StrNode(message.message.jump_url) if hasattr(message.message, 'jump_url') else None,
            '__last_message__': IntNode(message.message.channel.last_message_id),

            '__channel__': IntNode(message.message.channel.id),
            '__channel_name__': StrNode(message.message.channel.name),
            '__channel_type__': StrNode(message.message.channel.type.name) if hasattr(message.message.channel,
                                                                                      'type') else None,
            '__channel_id__': IntNode(message.message.channel.id),
            '__private_channel__': BoolNode(isinstance(message.message.channel, PrivateChannel)),
        }

        if message.guild is not None:
            local_env.update(
                {
                    '__guild__': IntNode(message.channel.guild.id),
                    '__guild_name__': StrNode(message.channel.guild.name),
                    '__guild_id__': IntNode(message.channel.guild.id),
                    '__guild_members__': ListNode([IntNode(member.id) for member in message.channel.guild.members],
                                                  bypass_limit_elt=True, editable=False),
                    '__guild_member_count__': IntNode(message.channel.guild.member_count),
                    '__guild_icon__': StrNode(message.channel.guild.icon.url) if message.channel.guild.icon else None,
                    '__guild_owner_id__': IntNode(message.channel.guild.owner_id),
                    '__guild_description__': StrNode(message.channel.guild.description),
                    '__guild_roles__': ListNode([IntNode(role.id) for role in message.channel.guild.roles],
                                                bypass_limit_elt=True, editable=False),
                    '__guild_roles_count__': IntNode(len(message.channel.guild.roles)),
                    '__guild_emojis__': ListNode([IntNode(emoji.id) for emoji in message.channel.guild.emojis],
                                                 bypass_limit_elt=True, editable=False),
                    '__guild_emojis_count__': IntNode(len(message.channel.guild.emojis)),
                    '__guild_channels__': ListNode([IntNode(channel.id) for channel in message.channel.guild.channels],
                                                   bypass_limit_elt=True, editable=False),
                    '__guild_text_channels__': ListNode(
                        [IntNode(channel.id) for channel in message.channel.guild.text_channels], bypass_limit_elt=True,
                        editable=False),
                    '__guild_voice_channels__': ListNode(
                        [IntNode(channel.id) for channel in message.channel.guild.voice_channels],
                        bypass_limit_elt=True, editable=False),
                    '__guild_categories__': ListNode(
                        [IntNode(channel.id) for channel in message.channel.guild.categories], bypass_limit_elt=True,
                        editable=False),
                    '__guild_stage_channels__': ListNode(
                        [IntNode(channel.id) for channel in message.channel.guild.stage_channels],
                        bypass_limit_elt=True, editable=False),
                    '__guild_forum_channels__': ListNode(
                        [IntNode(channel.id) for channel in message.channel.guild.forum_channels],
                        bypass_limit_elt=True, editable=False),
                    '__guild_channels_count__': IntNode(len(message.channel.guild.channels)),
                }
            )
        else:
            local_env.update(
                {
                    '__guild__': None,
                    '__guild_name__': None,
                    '__guild_id__': None,
                    '__guild_members__': None,
                    '__guild_member_count__': None,
                    '__guild_icon__': None,
                    '__guild_owner_id__': None,
                    '__guild_description__': None,
                    '__guild_roles__': None,
                    '__guild_roles_count__': None,
                    '__guild_emojis__': None,
                    '__guild_emojis_count__': None,
                    '__guild_channels__': None,
                    '__guild_text_channels__': None,
                    '__guild_voice_channels__': None,
                    '__guild_categories__': None,
                    '__guild_stage_channels__': None,
                    '__guild_forum_channels__': None,
                    '__guild_channels_count__': None,
                }
            )

        local_env.update(data)
        from ..DshellInterpreteur.dshell_interpreter import DshellInterpreteur
        new_interpreter = DshellInterpreteur(
            code,
            ctx=interaction,
            debug=False,
            vars_env=scope)

        with new_scope(new_interpreter, local_env):
            await new_interpreter.execute()

    else:
        await interaction.response.defer(invisible=True)
