#!/usr/bin/env python

from typing import (
    Any,
    Dict,
    Final,
    List,
    Optional,
    Tuple,
    Union,
)

from redis import Redis
from telegram import Update
from telegram._utils.logging import get_logger
from telegram._utils.warnings import warn
from telegram.ext._application import ApplicationHandlerStop
from telegram.ext import (  
    BaseHandler,
    StringCommandHandler,
    StringRegexHandler,
    TypeHandler,
    Application,
)

_CheckUpdateType = Tuple[object, object, BaseHandler[Update, Any], object]
_LOGGER = get_logger(__name__, class_name="ConversationHandler")


class ConversationHandler(BaseHandler[Update, Any]):

    __slots__ = (
        "_allow_reentry",
        "_child_conversations",
        "_entry_points",
        "_fallbacks",
        "_map_to_parent",
        "_name",
        "_states",
        "redis",
    )

    END: Final[int] = -1
    WAITING: Final[int] = -3

    block = True

    def __init__(
        self,
        name: Optional[str],
        entry_points: List[BaseHandler[Update, Any]],
        states: Dict[object, List[BaseHandler[Update, Any]]],
        fallbacks: List[BaseHandler[Update, Any]],
        redis: Redis,
        allow_reentry: bool = False,
        map_to_parent: Optional[Dict[object, object]] = None,
    ):
        self.redis = redis
        self._entry_points = entry_points
        self._states = states
        self._fallbacks = fallbacks
        self._allow_reentry = allow_reentry
        self._name = name
        self._map_to_parent = map_to_parent
        self._child_conversations = {
            handler
            for handler in entry_points
            + fallbacks
            + [h for hs in states.values() for h in hs]
            if isinstance(handler, ConversationHandler)
        }

        for handler in (
            entry_points + fallbacks + [h for hs in states.values() for h in hs]
        ):
            if isinstance(handler, (StringCommandHandler, StringRegexHandler)):
                warn(
                    f"The `ConversationHandler` only handles updates of type `telegram.Update`. "
                    f"{handler.__class__.__name__} handles updates of type `str`.",
                    stacklevel=2,
                )
            elif isinstance(handler, TypeHandler) and not issubclass(
                handler.type, Update
            ):
                warn(
                    f"The `ConversationHandler` only handles updates of type `telegram.Update`. "
                    f"The TypeHandler is set to handle {handler.type.__name__}.",
                    stacklevel=2,
                )

    @property
    def entry_points(self) -> List[BaseHandler[Update, Any]]:
        return self._entry_points

    @property
    def states(self) -> Dict[object, List[BaseHandler[Update, Any]]]:
        return self._states

    @property
    def fallbacks(self) -> List[BaseHandler[Update, Any]]:
        return self._fallbacks

    @property
    def allow_reentry(self) -> bool:
        return self._allow_reentry

    @property
    def name(self) -> Optional[str]:
        return self._name

    @property
    def map_to_parent(self) -> Optional[Dict[object, object]]:
        return self._map_to_parent

    def _get_key(self, update: Update) -> "Union[int, Tuple[int, int]]":
        if update.effective_user is None:
            raise RuntimeError("Can't build key for update without effective user!")
        return update.effective_user.id

    def check_update(self, update: object) -> "Optional[_CheckUpdateType[Any]]":

        if not isinstance(update, Update):
            return None
        if update.channel_post or update.edited_channel_post:
            return None
        if update.callback_query and not update.callback_query.message:
            return None

        key = self._get_key(update)
        state: Optional[bytes] = self.redis.hget(self.name, key)
        if state is not None:
            state = state.decode()

        _LOGGER.debug("Selecting conversation %s with state %s", str(key), str(state))

        handler: Optional[BaseHandler] = None

        if state is None or self.allow_reentry:
            for entry_point in self.entry_points:
                check = entry_point.check_update(update)
                if check is not None and check is not False:
                    handler = entry_point
                    break
            else:
                if state is None:
                    return None

        if state is not None and handler is None:
            for candidate in self.states.get(state, []):
                check = candidate.check_update(update)
                if check is not None and check is not False:
                    handler = candidate
                    break
            else:
                for fallback in self.fallbacks:
                    check = fallback.check_update(update)
                    if check is not None and check is not False:
                        handler = fallback
                        break
                else:
                    return None

        return state, key, handler, check

    async def handle_update(
        self,
        update: Update,
        application: "Application[Any, Any, Any, Any, Any, Any]",
        check_result: "_CheckUpdateType[Any]",
        context: Any,
    ) -> "Optional[object]":
        current_state, conversation_key, handler, handler_check_result = check_result
        raise_dp_handler_stop = False

        try:
            new_state: object = await handler.handle_update(
                update, application, handler_check_result, context
            )
        except ApplicationHandlerStop as exception:
            new_state = exception.state
            raise_dp_handler_stop = True

        if isinstance(self.map_to_parent, dict) and new_state in self.map_to_parent:
            self._update_state(self.END, conversation_key, handler)
            if raise_dp_handler_stop:
                raise ApplicationHandlerStop(self.map_to_parent.get(new_state))
            return self.map_to_parent.get(new_state)

        if current_state != self.WAITING:
            self._update_state(new_state, conversation_key, handler)

        if raise_dp_handler_stop:
            raise ApplicationHandlerStop
        return None

    def _update_state(
        self,
        new_state: object,
        key: Union[int, Tuple[int, int]],
        handler: Optional[BaseHandler] = None,
    ) -> None:
        if new_state == self.END:
            if self.redis.hexists(self.name, key):
                self.redis.hdel(self.name, key)
        elif new_state is not None:
            if new_state not in self.states:
                warn(
                    f"{repr(handler.callback.__name__) if handler is not None else 'BaseHandler'} "
                    f"returned state {new_state} which is unknown to the "
                    f"ConversationHandler{' ' + self.name if self.name is not None else ''}.",
                    stacklevel=2,
                )
            self.redis.hset(self.name, key, new_state)
