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

import logging
from redis import Redis
from telegram import Update
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
        "_logger",
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
        # Setting up an instance-specific logger
        self._logger = logging.getLogger(
            f"{self.__class__.__name__}_{name or 'default'}"
        )
        self._logger.setLevel(
            logging.DEBUG
        )  # Set logging level (DEBUG for detailed logs)

        # Example of adding a console handler (can add file handlers, etc.)
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        self._logger.addHandler(handler)

        self._logger.debug(
            "Initializing ConversationHandler instance with name: %s", name
        )

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
                self._logger.warning(
                    "Handler %s handles updates of type `str`, but ConversationHandler only handles `Update`.",
                    handler.__class__.__name__,
                )
            elif isinstance(handler, TypeHandler) and not issubclass(
                    handler.type, Update
            ):
                warn(
                    f"The `ConversationHandler` only handles updates of type `telegram.Update`. "
                    f"The TypeHandler is set to handle {handler.type.__name__}.",
                    stacklevel=2,
                )
                self._logger.warning(
                    "Handler TypeHandler is set to handle %s, but ConversationHandler only handles `Update`.",
                    handler.type.__name__,
                )

    @property
    def entry_points(self) -> List[BaseHandler[Update, Any]]:
        self._logger.debug("Retrieving entry points.")
        return self._entry_points

    @property
    def states(self) -> Dict[object, List[BaseHandler[Update, Any]]]:
        self._logger.debug("Retrieving states.")
        return self._states

    @property
    def fallbacks(self) -> List[BaseHandler[Update, Any]]:
        self._logger.debug("Retrieving fallbacks.")
        return self._fallbacks

    @property
    def allow_reentry(self) -> bool:
        self._logger.debug("Allow reentry: %s", self._allow_reentry)
        return self._allow_reentry

    @property
    def name(self) -> Optional[str]:
        self._logger.debug("Retrieving name: %s", self._name)
        return self._name

    @property
    def map_to_parent(self) -> Optional[Dict[object, object]]:
        self._logger.debug("Retrieving map_to_parent.")
        return self._map_to_parent

    def _get_key(self, update: Update) -> "Union[int, Tuple[int, int]]":
        if update.effective_user is None:
            self._logger.error("Can't build key for update without effective user!")
            raise RuntimeError("Can't build key for update without effective user!")
        key = update.effective_user.id
        self._logger.debug("Generated key for update: %s", key)
        return key

    def check_update(self, update: object) -> "Optional[_CheckUpdateType[Any]]":
        self._logger.debug("Checking update: %s", update)

        if not isinstance(update, Update):
            self._logger.debug("Update is not of type `telegram.Update`.")
            return None
        if update.channel_post or update.edited_channel_post:
            self._logger.debug("Ignoring channel post or edited channel post.")
            return None
        if update.callback_query and not update.callback_query.message:
            self._logger.debug("Ignoring callback query without a message.")
            return None

        key = self._get_key(update)
        state: Optional[bytes] = self.redis.hget(self.name, key)
        if state is not None:
            state = state.decode()

        self._logger.debug(
            "Selecting conversation %s with state %s", str(key), str(state)
        )

        handler: Optional[BaseHandler] = None

        if state is None or self.allow_reentry:
            self._logger.debug("Checking entry points.")
            for entry_point in self.entry_points:
                check = entry_point.check_update(update)
                if check is not None and check is not False:
                    handler = entry_point
                    self._logger.debug("Selected entry point: %s", handler)
                    break
            else:
                if state is None:
                    self._logger.debug("No state and no matching entry point found.")
                    return None

        if state is not None and handler is None:
            self._logger.debug("Checking states.")
            for candidate in self.states.get(state, []):
                check = candidate.check_update(update)
                if check is not None and check is not False:
                    handler = candidate
                    self._logger.debug("Selected state handler: %s", handler)
                    break
            else:
                self._logger.debug("Checking fallbacks.")
                for fallback in self.fallbacks:
                    check = fallback.check_update(update)
                    if check is not None and check is not False:
                        handler = fallback
                        self._logger.debug("Selected fallback: %s", handler)
                        break
                else:
                    self._logger.debug("No handler or fallback matched.")
                    return None

        self._logger.debug(
            "Update check passed with state: %s, handler: %s", state, handler
        )
        return state, key, handler, check

    async def handle_update(
            self,
            update: Update,
            application: "Application[Any, Any, Any, Any, Any, Any]",
            check_result: "_CheckUpdateType[Any]",
            context: Any,
    ) -> "Optional[object]":
        self._logger.debug("Handling update for conversation.")
        current_state, conversation_key, handler, handler_check_result = check_result
        raise_dp_handler_stop = False

        try:
            self._logger.debug("Executing handler.")
            new_state: object = await handler.handle_update(
                update, application, handler_check_result, context
            )
        except ApplicationHandlerStop as exception:
            self._logger.debug(
                "ApplicationHandlerStop raised with state: %s", exception.state
            )
            new_state = exception.state
            raise_dp_handler_stop = True

        if isinstance(self.map_to_parent, dict) and new_state in self.map_to_parent:
            self._logger.debug("Mapping new state to parent: %s", new_state)
            self._update_state(self.END, conversation_key, handler)
            if raise_dp_handler_stop:
                raise ApplicationHandlerStop(self.map_to_parent.get(new_state))
            return self.map_to_parent.get(new_state)

        if current_state != self.WAITING:
            self._logger.debug("Updating state to: %s", new_state)
            self._update_state(new_state, conversation_key, handler)

        if raise_dp_handler_stop:
            self._logger.debug("Raising ApplicationHandlerStop.")
            raise ApplicationHandlerStop
        return None

    def _update_state(
            self,
            new_state: object,
            key: Union[int, Tuple[int, int]],
            handler: Optional[BaseHandler] = None,
    ) -> None:
        self._logger.debug("Updating conversation state to: %s", new_state)
        if new_state == self.END:
            self._logger.debug("Ending conversation.")
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
                self._logger.warning("Unknown state returned: %s", new_state)
            self.redis.hset(self.name, key, new_state)
            self._logger.debug("State updated for key: %s", key)

    def __repr__(self) -> str:
        """Give a string representation of the handler in the form ``ClassName[callback=...]``.

        As this class doesn't implement :meth:`object.__str__`, the default implementation
        will be used, which is equivalent to :meth:`__repr__`.

        Returns:
            :obj:`str`
        """
        return f"ConversationHandler ({self.name})"
