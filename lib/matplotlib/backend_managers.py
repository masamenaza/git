"""
`ToolManager`
    Class that makes the bridge between user interaction (key press,
    toolbar clicks, ..) and the actions in response to the user inputs.
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import six
import warnings

import matplotlib.cbook as cbook
import matplotlib.widgets as widgets
from matplotlib.rcsetup import validate_stringlist
import matplotlib.backend_tools as tools


class ToolEvent(object):
    """Event for tool manipulation (add/remove)"""
    def __init__(self, name, tool):
        self.name = name
        self.tool = tool


class ToolTriggerEvent(ToolEvent):
    """Event to inform  that a tool has been triggered"""
    def __init__(self, name, tool, canvasevent=None):
        ToolEvent.__init__(self, name, tool)
        self.canvasevent = canvasevent


class ToolManagerMessageEvent(object):
    """
    Event carrying messages from toolmanager

    Messages usually get displayed to the user by the toolbar
    """
    def __init__(self, name, message):
        self.name = name
        self.message = message


class ToolManager(object):
    """
    Helper class that groups all the user interactions for a Figure

    Attributes
    ----------
    figure: `Figure`
    keypresslock: `widgets.LockDraw`
        `LockDraw` object to know if the `canvas` key_press_event is locked
    messagelock: `widgets.LockDraw`
        `LockDraw` object to know if the message is available to write
    """

    def __init__(self, figure=None):
        warnings.warn('Treat the new Tool classes introduced in v1.5 as ' +
                       'experimental for now, the API will likely change in ' +
                       'version 2.1 and perhaps the rcParam as well')

        self._key_press_handler_id = None

        self._tools = {}
        self._keys = {}
        self._toggled = {}
        self._callbacks = cbook.CallbackRegistry()

        # to process keypress event
        self.keypresslock = widgets.LockDraw()
        self.messagelock = widgets.LockDraw()

        self._figure = None
        self.set_figure(figure)

    @property
    def canvas(self):
        """Canvas managed by FigureManager"""
        if not self._figure:
            return None
        return self._figure.canvas

    @property
    def figure(self):
        """Figure that holds the canvas"""
        return self._figure

    @figure.setter
    def figure(self, figure):
        self.set_figure(figure)

    def set_figure(self, figure, update_tools=True):
        """
        Sets the figure to interact with the tools

        Parameters
        ==========
        figure: `Figure`
        update_tools: bool
            Force tools to update figure
        """
        if self._key_press_handler_id:
            self.canvas.mpl_disconnect(self._key_press_handler_id)
        self._figure = figure
        if figure:
            self._key_press_handler_id = self.canvas.mpl_connect(
                'key_press_event', self._key_press)
        if update_tools:
            for tool in self._tools.values():
                tool.figure = figure

    def toolmanager_connect(self, s, func):
        """
        Connect event with string *s* to *func*.

        Parameters
        ----------
        s : String
            Name of the event

            The following events are recognized

            - 'tool_message_event'
            - 'tool_removed_event'
            - 'tool_added_event'

            For every tool added a new event is created

            - 'tool_trigger_TOOLNAME`
              Where TOOLNAME is the id of the tool.

        func : function
            Function to be called with signature
            def func(event)
        """
        return self._callbacks.connect(s, func)

    def toolmanager_disconnect(self, cid):
        """
        Disconnect callback id *cid*

        Example usage::

            cid = toolmanager.toolmanager_connect('tool_trigger_zoom',
                                                  on_press)
            #...later
            toolmanager.toolmanager_disconnect(cid)
        """
        return self._callbacks.disconnect(cid)

    def message_event(self, message):
        """ Emit a `ToolManagerMessageEvent`"""
        s = 'tool_message_event'
        event = ToolManagerMessageEvent(s, message)
        self._callbacks.process(s, event)

    @property
    def active_toggle(self):
        """Currently toggled tools"""

        return self._toggled

    def get_tool_keymap(self, name):
        """
        Get the keymap associated with the specified tool

        Parameters
        ----------
        name : string
            Name of the Tool

        Returns
        -------
        list : list of keys associated with the Tool
        """

        keys = [k for k, i in six.iteritems(self._keys) if i == name]
        return keys

    def _remove_keys(self, name):
        for k in self.get_tool_keymap(name):
            del self._keys[k]

    def update_keymap(self, name, *keys):
        """
        Set the keymap to associate with the specified tool

        Parameters
        ----------
        name : string
            Name of the Tool
        keys : keys to associate with the Tool
        """

        if name not in self._tools:
            raise KeyError('%s not in Tools' % name)

        self._remove_keys(name)

        for key in keys:
            for k in validate_stringlist(key):
                if k in self._keys:
                    warnings.warn('Key %s changed from %s to %s' %
                                  (k, self._keys[k], name))
                self._keys[k] = name

    def remove_tool(self, name):
        """
        Remove tool from `ToolManager`

        Parameters
        ----------
        name : string
            Name of the Tool
        """

        tool = self.get_tool(name)
        tool.destroy()

        # If is a toggle tool and toggled, untoggle
        if getattr(tool, 'toggled', False):
            self.trigger_tool(tool, 'toolmanager')

        self._remove_keys(name)

        s = 'tool_removed_event'
        event = ToolEvent(s, tool)
        self._callbacks.process(s, event)

        del self._tools[name]

    def add_tool(self, tool_name, *args, **kwargs):
        """
        Add *tool* to `ToolManager`

        If successful adds a new event `tool_trigger_name` where **name** is
        the **name** of the tool, this event is fired everytime
        the tool is triggered.

        Parameters
        ----------
        name : str
            Name of the tool, treated as the ID, has to be unique
        tool : class_like, i.e. str or type
            Reference to find the class of the Tool to added.

        Notes
        -----
        args and kwargs get passed directly to the tools constructor.

        See Also
        --------
        matplotlib.backend_tools.ToolBase : The base class for tools.
        """

        tool_cls = tools.get_tool(tool_name, self.canvas.__module__)

        if tool_name in self._tools:
            warnings.warn('A "Tool class" with the same name already exists, '
                          'not added')
            return self._tools[tool_name]

        tool_obj = tool_cls(self, tool_name, *args, **kwargs)
        self._tools[tool_name] = tool_obj

        if tool_cls.default_keymap is not None:
            self.update_keymap(tool_name, tool_cls.default_keymap)

        # For toggle tools init the radio_group in self._toggled
        if isinstance(tool_obj, tools.ToolToggleBase):
            # None group is not mutually exclusive, a set is used to keep track
            # of all toggled tools in this group
            if tool_obj.radio_group is None:
                self._toggled.setdefault(None, set())
            else:
                self._toggled.setdefault(tool_obj.radio_group, None)

            # If initially toggled
            if tool_obj.toggled:
                self._handle_toggle(tool_obj, None)
        tool_obj.set_figure(self.figure)

        self._tool_added_event(tool_obj)
        return tool_obj

    def _tool_added_event(self, tool):
        s = 'tool_added_event'
        event = ToolEvent(s, tool)
        self._callbacks.process(s, event)

    def _handle_toggle(self, tool, canvasevent):
        """
        Toggle tools, need to untoggle prior to using other Toggle tool
        Called from trigger_tool

        Parameters
        ----------
        tool: Tool object
        canvasevent : Event
            Original Canvas event or None
        """

        radio_group = tool.radio_group
        # radio_group None is not mutually exclusive
        # just keep track of toggled tools in this group
        if radio_group is None:
            if tool.name in self._toggled[None]:
                self._toggled[None].remove(tool.name)
            else:
                self._toggled[None].add(tool.name)
            return

        # If the tool already has a toggled state, untoggle it
        if self._toggled[radio_group] == tool.name:
            toggled = None
        # If no tool was toggled in the radio_group
        # toggle it
        elif self._toggled[radio_group] is None:
            toggled = tool.name
        # Other tool in the radio_group is toggled
        else:
            # Untoggle previously toggled tool
            self.trigger_tool(self._toggled[radio_group], canvasevent)
            toggled = tool.name

        # Keep track of the toggled tool in the radio_group
        self._toggled[radio_group] = toggled

    def trigger_tool(self, name, canvasevent=None):
        """
        Trigger a tool and emit the tool_trigger_[name] event

        Parameters
        ----------
        name : string
            Name of the tool
        canvasevent : Event
            Original Canvas event or None
        """
        tool = self.get_tool(name)
        if tool is None:
            return
        self._trigger_tool(name, canvasevent)
        s = 'tool_trigger_%s' % name
        event = ToolTriggerEvent(s, tool, canvasevent)
        self._callbacks.process(s, event)

    def _trigger_tool(self, name, canvasevent=None):
        """
        Trigger on a tool

        Method to actually trigger the tool
        """
        tool = self.get_tool(name)

        if isinstance(tool, tools.ToolToggleBase):
            self._handle_toggle(tool, canvasevent)

        # Important!!!
        # This is where the Tool object gets triggered
        tool.trigger(canvasevent)

    def _key_press(self, event):
        if event.key is None or self.keypresslock.locked():
            return

        name = self._keys.get(event.key, None)
        if name is None:
            return
        self.trigger_tool(name, canvasevent=event)

    @property
    def tools(self):
        """Return the tools controlled by `ToolManager`"""

        return self._tools

    def get_tool(self, name, warn=True):
        """
        Return the tool object, also accepts the actual tool for convenience

        Parameters
        ----------
        name : str, ToolBase
            Name of the tool, or the tool itself
        warn : bool, optional
            If this method should give warnings.
        """
        if isinstance(name, tools.ToolBase) and name.name in self._tools:
            return name
        if name not in self._tools:
            if warn:
                warnings.warn("ToolManager does not control tool %s" % name)
            return None
        return self._tools[name]
