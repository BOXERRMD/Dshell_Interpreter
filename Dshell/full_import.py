from asyncio import sleep
from typing import TypeVar, Optional, Callable, Union, Any, TYPE_CHECKING
from copy import deepcopy
from pycordViews import EasyModifiedViews, SelectMenu
from pycordViews.views.errors import CustomIDNotFound
from datetime import timedelta, datetime, UTC
from requests import get

from discord.ui import Button, Select
from discord import (ButtonStyle, Interaction, Guild, Member, Role, Permissions, PermissionOverwrite, Message, MISSING,
                     CategoryChannel, VoiceChannel, TextChannel, Thread, PartialMessage, NotFound, ForumChannel, Colour,
                     Embed, AutoShardedBot, ComponentType, AllowedMentions)
from discord.abc import PrivateChannel
from discord.utils import get, _MissingSentinel
from contextvars import ContextVar
from re import *
from random import randint, choice, random
from enum import Enum, auto, StrEnum
