__all__ = [
    'dshell_respond_interaction',
    'dshell_defer_interaction',
    'dshell_delete_original_message'
]


from Dshell.full_import import (Interaction,
                           Embed,
                           EasyModifiedViews)

from .utils.utils_message import utils_autorised_mentions
from .utils.utils_type_validation import (_validate_optional_number,
                                          _validate_optional_embed,
                                          _validate_optional_view,
                                          _validate_optional_string,
                                          _validate_optional_bool,
                                          _validate_required_bool)

async def dshell_respond_interaction(ctx: Interaction,
                                     content: str = None,
                                     delete=None,
                                     global_mentions: bool = None,
                                     everyone_mention: bool = True,
                                     roles_mentions: bool = True,
                                     users_mentions: bool = True,
                                     reply_mention: bool = False,
                                     hide: bool = False,
                                     embeds=None,
                                     view=None) -> int:
    """
    Répond à une interaction Discord avec un message.
    
    Cette fonction permet de répondre à une interaction Discord (comme un slash command)
    avec un message personnalisé. Elle supporte les mentions, les embeds, les vues (boutons/menus)
    et peut rendre la réponse éphémère (visible uniquement par l'utilisateur).
    
    :param ctx: Le contexte de l'interaction Discord
    :type ctx: Interaction
    :param content: Le contenu textuel du message (optionnel)
    :type content: str | None
    :param delete: Temps en secondes avant suppression automatique du message (optionnel)
    :type delete: int | float | None
    :param global_mentions: Active/désactive toutes les mentions (override les autres paramètres si défini)
    :type global_mentions: bool | None
    :param everyone_mention: Autorise la mention @everyone et @here
    :type everyone_mention: bool
    :param roles_mentions: Autorise les mentions de rôles
    :type roles_mentions: bool
    :param users_mentions: Autorise les mentions d'utilisateurs
    :type users_mentions: bool
    :param reply_mention: Mentionne l'auteur de l'interaction dans la réponse
    :type reply_mention: bool
    :param hide: Rend le message éphémère (visible uniquement par l'utilisateur qui a déclenché l'interaction)
    :type hide: bool
    :param embeds: Embed(s) à inclure dans le message (Embed unique ou ListNode d'Embeds)
    :type embeds: Embed | ListNode | None
    :param view: Vue interactive (boutons, menus) à attacher au message
    :type view: View | None
    :return: L'ID du message envoyé
    :rtype: int
    :raises Exception: Si le contexte n'est pas une Interaction
    :raises TypeError: Si les types des paramètres sont invalides
    
    Example:
        >>> await dshell_respond_interaction(ctx, content="Bonjour!", hide=True)
        123456789
    """
    _CMD = "sri"

    if not isinstance(ctx, Interaction):
        raise Exception(f'Respond to an interaction must be used in an interaction context, not {type(ctx)} !')

    _validate_optional_string(content, "Content", _CMD)
    _validate_optional_number(delete, "Delete", _CMD)
    _validate_optional_bool(global_mentions, "Global mentions", _CMD)
    _validate_required_bool(everyone_mention, "Everyone mention", _CMD)
    _validate_required_bool(roles_mentions, "Roles mentions", _CMD)
    _validate_required_bool(users_mentions, "Users mentions", _CMD)
    _validate_required_bool(reply_mention, "Reply mention", _CMD)
    _validate_required_bool(hide, "Hide", _CMD)

    allowed_mentions = utils_autorised_mentions(global_mentions,
                                                everyone_mention,
                                                roles_mentions,
                                                users_mentions,
                                                reply_mention)

    from Dshell.DshellParser.ast_nodes import ListNode

    _validate_optional_embed(embeds, "Embeds", _CMD)

    if embeds is None:
        embeds = ListNode([])

    elif isinstance(embeds, Embed):
        embeds = ListNode([embeds])

    _validate_optional_view(view, "View", _CMD)

    sended_message = await ctx.response.send_message(
                                     content=str(content),
                                     ephemeral=hide,
                                     allowed_mentions=allowed_mentions,
                                     delete_after=delete,
                                     embeds=embeds,
                                     view=view)

    return sended_message.id

async def dshell_defer_interaction(ctx: Interaction) -> bool:
    """
    Diffère la réponse d'une interaction Discord.
    
    Cette fonction indique à Discord que le bot traite l'interaction et répondra plus tard.
    Cela empêche l'interaction d'expirer (timeout de 3 secondes par défaut).
    Utile pour les opérations longues qui nécessitent plus de temps de traitement.
    
    :param ctx: Le contexte de l'interaction Discord
    :type ctx: Interaction
    :return: True si le defer a réussi
    :rtype: bool
    :raises Exception: Si le contexte n'est pas une Interaction
    
    Example:
        >>> await dshell_defer_interaction(ctx)
        True
    """

    if not isinstance(ctx, Interaction):
        raise Exception(f'Respond to an interaction must be used in an interaction context, not {type(ctx)} !')

    await ctx.response.defer()

    return True

async def dshell_delete_original_message(ctx: Interaction) -> int:
    """
    Supprime le message original d'une interaction Discord.
    
    Cette fonction supprime le message qui a déclenché l'interaction.
    Fonctionne uniquement avec les interactions qui ont un message associé.
    
    :param ctx: Le contexte de l'interaction Discord
    :type ctx: Interaction
    :return: L'ID du message supprimé
    :rtype: int
    :raises Exception: Si le contexte n'est pas une Interaction
    
    Example:
        >>> await dshell_delete_original_message(ctx)
        987654321
    """

    if not isinstance(ctx, Interaction):
        raise Exception(f'Respond to an interaction must be used in an interaction context, not {type(ctx)} !')

    await ctx.delete_original_message()

    return ctx.message.id
