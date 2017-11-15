Add AuthManager

This implements the AuthManager class and its needed interfaces and
subclasses, and integrates them into the backend portion of MediaWiki.
Integration with frontend portions of MediaWiki (e.g. ApiLogin,
Special:Login) is left for a followup.

Bug: T91699
Bug: T71589
Bug: T111299
Co-Authored-by: Gergő Tisza <gtisza@wikimedia.org>
Change-Id: If89d24838e326fe25fe867d02181eebcfbb0e196
