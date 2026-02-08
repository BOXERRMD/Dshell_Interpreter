from Dshell.full_import import (ButtonStyle,
                           PrivateChannel,
                           Interaction,
                           Button,
                           MISSING,
                           EasyModifiedViews,
                           CustomIDNotFound,
                           SelectMenu,
                           ComponentType,
                           Select,
                           random)

from .._DshellParser.ast_nodes import UiSelectNode, UiButtonNode, CodeNode, OptionUiSelectNode, ListNode

from .._DshellInterpreteur.utils_interpreter import regroupe_commandes

from .._DshellInterpreteur.dshell_scope import new_scope

from Dshell.full_import import Any, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .._DshellInterpreteur.dshell_interpreter import DshellInterpreteur


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
    regrouped_parameters = await regroupe_commandes(ui_button_node.body, interpreter, normalise=True)
    args_button: dict[str, list[Any]] = regrouped_parameters.get_dict_parameters()

    code = args_button.pop('code', None)
    style = args_button.pop('style', 'primary').lower()
    custom_id = args_button.pop('custom_id', 'ui_button_'+str(random()))
    row = args_button.pop('row', 0)

    if code is not None and not isinstance(code, CodeNode):
        raise TypeError(f"Button code muste be a CodeNode or None, not {type(code)}")

    if not isinstance(custom_id, str):
        raise TypeError(f"Button custom_id must be a string, not {type(custom_id)} !")

    if style not in ButtonStyleValues:
        raise ValueError(f"Button style must be one of {', '.join(ButtonStyleValues)}, not '{style}' !")

    args_button['custom_id'] = custom_id
    args_button['row'] = row
    args_button['style'] = ButtonStyle[style]
    args = args_button.pop('*', ())
    yield args, args_button, code


async def build_ui_select_parameters(ui_select_node: UiSelectNode, interpreter: "DshellInterpreteur"):
    """
    Builds the parameters for a UI select menu from the UiNode.
    :param ui_select_node:
    :param interpreter:
    :return:
    """
    regrouped_parameters = await regroupe_commandes(ui_select_node.body, interpreter, normalise=True)
    args_select: dict[str, list[Any]] = regrouped_parameters.get_dict_parameters()

    code = args_select.pop('code', None)
    custom_id = args_select.pop('custom_id', 'ui_select_'+str(random()))
    select_type = args_select.pop('type', 'string').lower()

    disabled = args_select.get('disabled', False)
    max_values = args_select.get('max', 1)
    min_values = args_select.get('min', 1)
    placeholder = args_select.get('placeholder', "")
    row = args_select.pop('row', 0)

    if code is not None and not isinstance(code, CodeNode):
        raise TypeError(f"Select code muste be a CodeNode or None, not {type(code)}")

    if not isinstance(custom_id, str):
        raise TypeError(f"Select custom_id must be a string, not {type(custom_id)} !")

    if select_type is None or not isinstance(select_type, str) or select_type not in SelectSyleValues:
        raise TypeError(f"Select type must be a string, not {type(select_type)} !")

    if not isinstance(disabled, bool):
        raise TypeError(f"Select disabled must be a bool, not {type(disabled)} !")

    if not isinstance(max_values, int):
        raise TypeError(f"Select max_values must be an int, not {type(max_values)} !")

    if not isinstance(min_values, int):
        raise TypeError(f"Select min_values must be an int, not {type(min_values)} !")

    if not isinstance(placeholder, str):
        raise TypeError(f"Select placeholder must be a string, not {type(placeholder)} !")

    if row is not None and not isinstance(row, int):
        raise TypeError(f"Select row must be an int or None, not {type(row)} !")

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
    option_results: list[dict[str, Any]] = []

    for option_node in option_nodes:
        regrouped_parameters = await regroupe_commandes(option_node.body, interpreter, normalise=True)
        args_option: dict[str, list[Any]] = regrouped_parameters.get_dict_parameters()

        label = args_option.pop('label', None)
        value = args_option.pop('value', MISSING)
        description = args_option.pop('description', None)
        emoji = args_option.pop('emoji', None)
        default = args_option.pop('default', False)

        if label is None or not isinstance(label, str):
            raise TypeError(f"Option label must be a string, not {type(label)} !")

        if len(label) > 100:
            raise ValueError("Option label must be less than 100 characters !")

        if value and not isinstance(value, str):
            raise TypeError(f"Option value must be a string, not {type(value)} !")

        if value and len(value) > 100:
            raise ValueError("Option value must be less than 100 characters !")

        if description is not None and not isinstance(description, str):
            raise TypeError(f"Option description must be a string or None, not {type(description)} !")

        if description is not None and len(description) > 100:
            raise ValueError("Option description must be less than 100 characters !")

        if emoji is not None and not isinstance(emoji, str):
            raise TypeError(f"Option emoji must be a string or None, not {type(emoji)} !")

        if not isinstance(default, bool):
            raise TypeError(f"Option default must be a bool, not {type(default)} !")

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
    view = EasyModifiedViews()

    if isinstance(ui_node, UiButtonNode):
        async for _, args_button, code in build_ui_button_parameters(ui_node, interpreter):
            b = Button(**args_button)
            view.add_items(b)
            view.set_callable(b.custom_id, _callable=ui_button_callback, data={'code': code, 'interpreter': interpreter})

    elif isinstance(ui_node, UiSelectNode):
        s = SelectMenu()
        async for _, args_select, code in build_ui_select_parameters(ui_node, interpreter):

            options = args_select.pop("options", [])
            select_type = args_select.pop("type")

            if select_type == ComponentType.string_select:
                menu = s.add_string_select_menu(**args_select)

                for option in options:
                    menu.add_option(**option)

                s.set_callable(args_select["custom_id"], _callable=ui_select_callback, data={'code': code, 'interpreter': interpreter})

            elif select_type == ComponentType.role_select:
                s.add_role_select_menu(**args_select)
                s.set_callable(args_select["custom_id"], _callable=ui_select_callback, data={'code': code, 'interpreter': interpreter})

            elif select_type == ComponentType.user_select:
                s.add_user_select_menu(**args_select)
                s.set_callable(args_select["custom_id"], _callable=ui_select_callback, data={'code': code, 'interpreter': interpreter})

            elif select_type == ComponentType.mentionable_select:
                s.add_mentionable_select_menu(**args_select)
                s.set_callable(args_select["custom_id"], _callable=ui_select_callback, data={'code': code, 'interpreter': interpreter})

            elif select_type == ComponentType.channel_select:
                s.add_channel_select_menu(**args_select)
                s.set_callable(args_select["custom_id"], _callable=ui_select_callback, data={'code': code, 'interpreter': interpreter})

        view.add_items(s)

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
                ui: Button = view.get_ui(args_button['custom_id'])
            except CustomIDNotFound:
                raise ValueError(f"Button with custom_id '{args_button['custom_id']}' not found in the view !")

            ui.label = args_button.get('label', ui.label)
            ui.style = args_button.get('style', ui.style)
            ui.emoji = args_button.get('emoji', ui.emoji)
            ui.disabled = args_button.get('disabled', ui.disabled)
            ui.url = args_button.get('url', ui.url)
            ui.row = args_button.get('row', ui.row)
            new_code = code if code is not None else view.get_callable_data(args_button['custom_id'])['code']
            view.set_callable(args_button['custom_id'], _callable=ui_button_callback, data={'code': new_code, 'interpreter': interpreter})

    elif isinstance(ui_node, UiSelectNode):

        async for args, args_select, code in build_ui_select_parameters(ui_select_node=ui_node, interpreter=interpreter):
            try:
                ui: Select = view.get_ui(args_select['custom_id'])
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
            view.set_callable(args_select['custom_id'], _callable=ui_select_callback, data={'code': new_code, 'interpreter': interpreter})

    return view


async def ui_button_callback(button: Button, interaction: Interaction, data: dict[str, Any]):
    """
    Callback for UI buttons.
    Executes the code associated with the button.
    :param button:
    :param interaction:
    :param data:
    :return:
    """
    code = data.pop('code', None)
    interpreter: "DshellInterpreteur" = data.pop('interpreter', None)
    if code is not None:
        local_env = {
            '__ret__': None,
            '__guild__': interaction.guild.name if interaction.guild else None,
            '__channel__': interaction.channel.name if interaction.channel else None,
            '__author__': interaction.user.id,
            '__author_name__': interaction.user.name,
            '__author_display_name__': interaction.user.display_name,
            '__author_avatar__': interaction.user.display_avatar.url if interaction.user.display_avatar else None,
            '__author_discriminator__': interaction.user.discriminator,
            '__author_bot__': interaction.user.bot,
            '__author_nick__': interaction.user.nick if hasattr(interaction.user, 'nick') else None,
            '__author_id__': interaction.user.id,
            '__message__': interaction.message.content if hasattr(interaction.message, 'content') else None,
            '__message_id__': interaction.message.id if hasattr(interaction.message, 'id') else None,
            '__channel_name__': interaction.channel.name if interaction.channel else None,
            '__channel_type__': interaction.channel.type.name if hasattr(interaction.channel, 'type') else None,
            '__channel_id__': interaction.channel.id if interaction.channel else None,
            '__private_channel__': isinstance(interaction.channel, PrivateChannel),
        }
        local_env.update(data)
        from .._DshellInterpreteur.dshell_interpreter import DshellInterpreteur
        with new_scope(interpreter, local_env):
            await DshellInterpreteur(code, ctx=interaction, debug=False, vars_env=interpreter.env).execute()
    else:
        await interaction.response.defer(invisible=True)

    data.update({'code': code, 'interpreter': interpreter})

async def ui_select_callback(select: Select, interaction: Interaction, data: dict[str, Any]):
    """
    Callback for UI select menus.
    Executes the code associated with the select menu.
    :param select:
    :param interaction:
    :param data:
    :return:
    """
    code = data.pop('code', None)
    interpreter: "DshellInterpreteur" = data.pop('interpreter', None)
    if code is not None:
        local_env = {
            '__ret__': None,
            '__guild__': interaction.guild.name if interaction.guild else None,
            '__channel__': interaction.channel.name if interaction.channel else None,
            '__author__': interaction.user.id,
            '__author_name__': interaction.user.name,
            '__author_display_name__': interaction.user.display_name,
            '__author_avatar__': interaction.user.display_avatar.url if interaction.user.display_avatar else None,
            '__author_discriminator__': interaction.user.discriminator,
            '__author_bot__': interaction.user.bot,
            '__author_nick__': interaction.user.nick if hasattr(interaction.user, 'nick') else None,
            '__author_id__': interaction.user.id,
            '__message__': interaction.message.content if hasattr(interaction.message, 'content') else None,
            '__message_id__': interaction.message.id if hasattr(interaction.message, 'id') else None,
            '__channel_name__': interaction.channel.name if interaction.channel else None,
            '__channel_type__': interaction.channel.type.name if hasattr(interaction.channel, 'type') else None,
            '__channel_id__': interaction.channel.id if interaction.channel else None,
            '__private_channel__': isinstance(interaction.channel, PrivateChannel),
            '__values__': ListNode([i.id for i in select.values]) if select.values and hasattr(select.values[0], 'id') else ListNode(select.values)
        }
        local_env.update(data)
        from .._DshellInterpreteur.dshell_interpreter import DshellInterpreteur
        with new_scope(interpreter, local_env):
            await DshellInterpreteur(code, ctx=interaction, debug=False, vars_env=interpreter.env).execute()
    else:
        await interaction.response.defer(invisible=True)

    data.update({'code': code, 'interpreter': interpreter})