Permissions
===========

The `PermissionLevel` class
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: xbotpp.permission.PermissionLevel
	:members:

Generic `PermissionLevel` classes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: xbotpp.permission.AdminPermissionLevel
   :show-inheritance:
   :undoc-members:

.. autoclass:: xbotpp.permission.ChannelOpPermissionLevel
   :show-inheritance:
   :undoc-members:

.. autoclass:: xbotpp.permission.ChannelVoicePermissionLevel
   :show-inheritance:
   :undoc-members:

Specific global permissions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

	Modules can specify their own permission levels, the ones listed here relate
	to core bot commands or actions.

.. automodule:: xbotpp.permission
   :members: 
   :exclude-members: PermissionLevel, AdminPermissionLevel, ChannelOpPermissionLevel, ChannelVoicePermissionLevel
   :show-inheritance:
   :undoc-members:
   :member-order: bysource