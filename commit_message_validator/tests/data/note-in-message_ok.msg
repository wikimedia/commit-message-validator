resourceloader: Implement 'deprecated' option for FileModule

ResourceLoader modules can now carry a 'deprecated' option which can
be a boolean or an object with message key. This message or a default
deprecation message will be show whenever that module is used in production.

Note: This will not work in debug mode for ResourceLoaderFile modules
and this is deemed acceptable for the time being. We can revisit later.

Bug: T137772
Change-Id: Ib9ebd2d39a59fd41d8537e06884699f77b03580c
