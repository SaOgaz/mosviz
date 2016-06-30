from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import inspect
import traceback
import logging
from functools import wraps


class EventNode(object):
    def __init__(self, *args):
        self._args = args
        self.__handlers = []

    def __iadd__(self, other):
        self.__handlers.append(other)
        return self

    def __isub__(self, other):
        self.__handlers.remove(other)
        return self

    def emit(self, *args, **kwargs):
        if len(args) != len(self._args) and not set(kwargs.keys()).issubset(
                set(self._args)):
            raise ValueError("Unknown keyword in event emit arguments.")

        for handler in self.__handlers:
            # logging.info("Sending message from: '{}'".format(handler))
            if hasattr(handler, 'self'):
                handler(handler.self, *args, **kwargs)
            else:
                handler(*args, **kwargs)

    def clear(self):
        """
        Removes all handlers from object.
        """
        self.__handlers = []


class Dispatch(object):
    """
    Central communications object for all events.
    """
    @classmethod
    def register_event(cls, name, args=None):
        args = args or []

        if not hasattr(cls, name):
            setattr(cls, name, EventNode(*args))
        else:
            logging.warning("Event '{}' already exists. Please use a "
                            "different name.".format(name))

    @classmethod
    def register_listener(cls, name, func):
        if hasattr(cls, name):
            call_func = getattr(cls, name)
            call_func += func
        else:
            logging.warning("No such event: {}. Event must be registered "
                            "before listeners can be assigned.".format(name))

    @classmethod
    def unregister_listener(cls, name, func):
        if hasattr(cls, name):
            call_func = getattr(cls, name)
            call_func -= func
        else:
            logging.warning("No such event: {}.".format(name))


class DispatchHandle(object):
    """
    Interface for allowing classes to use decorators to define event
    listeners. Otherwise, classes would have to define all listeners in the
    `init` function using

    >>> Dispatch.register_listener("<event_name>", <class_method>)
    """
    @staticmethod
    def setup(inst):
        logging.info("Dispatch is now watching: {}".format(inst))
        members = inspect.getmembers(inst, predicate=inspect.ismethod)

        for func_name, func in members:
            if hasattr(func, 'wrapped'):
                if func.wrapped:
                    for name in func.event_names:
                        Dispatch.register_listener(name, func)

    @staticmethod
    def tear_down(inst):
        logging.info("Dispatch has stopped watching: {}".format(inst))
        members = inspect.getmembers(inst, predicate=inspect.ismethod)

        for func_name, func in members:
            if hasattr(func, 'wrapped'):
                if func.wrapped:
                    for name in func.event_names:
                        Dispatch.unregister_listener(name, func)

    @staticmethod
    def register_listener(*args):
        def decorator(func):
            func.wrapped = True
            func.event_names = args

            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except:
                    logging.error("Exception in '{}':\n{}".format(func.__name__,
                                                                  traceback.format_exc()))
            return wrapper
        return decorator


Dispatch.register_event("on_activated_window", args=["window"])

Dispatch.register_event("on_added_data", args=["data"])
Dispatch.register_event("on_added_window", args=["layer", "window"])
Dispatch.register_event("on_added_plot", args=["plot", "window"])
Dispatch.register_event("on_added_layer", args=["layer"])
Dispatch.register_event("on_added_to_window", args=["layer", "window"])

Dispatch.register_event("on_show_linelists_window")
Dispatch.register_event("on_dismiss_linelists_window")
Dispatch.register_event("on_request_linelists")
Dispatch.register_event("on_plot_linelists", args=["table_views"])
Dispatch.register_event("on_erase_linelabels")

Dispatch.register_event("on_removed_data", args=["data"])
Dispatch.register_event("on_removed_plot", args=["layer", "window"])
Dispatch.register_event("on_removed_layer", args=["layer", "window"])
Dispatch.register_event("on_removed_model", args=["model", "layer"])
Dispatch.register_event("on_removed_from_window", args=["layer", "window"])

Dispatch.register_event("on_updated_layer", args=["layer"])
Dispatch.register_event("on_updated_model", args=["model"])
Dispatch.register_event("on_updated_plot", args=["plot", "layer"])
Dispatch.register_event("on_updated_rois", args=["rois"])
Dispatch.register_event("on_updated_stats", args=["stats", "layer"])

Dispatch.register_event("on_selected_plot", args=["layer"])
Dispatch.register_event("on_selected_window", args=["window"])
Dispatch.register_event("on_selected_layer", args=["layer_item"])
Dispatch.register_event("on_selected_model", args=["model_item"])

Dispatch.register_event("on_clicked_layer", args=["layer_item"])
Dispatch.register_event("on_changed_layer", args=["layer_item"])
Dispatch.register_event("on_changed_model", args=["model_item"])

Dispatch.register_event("on_add_model", args=["layer"])
Dispatch.register_event("on_add_window", args=["data", "window"])
Dispatch.register_event("on_add_layer", args=["window", "layer", "from_roi"])
Dispatch.register_event("on_add_roi", args=[])

Dispatch.register_event("on_update_model", args=["layer"])

Dispatch.register_event("on_remove_data", args=["data"])
Dispatch.register_event("on_remove_layer", args=["layer"])
Dispatch.register_event("on_remove_model", args=["model"])
Dispatch.register_event("on_remove_all_data")

Dispatch.register_event("on_file_open", args=["file_name"])
Dispatch.register_event("on_file_read", args=["file_name", "file_filter"])

Dispatch.register_event("on_status_message", args=["message", "timeout"])
