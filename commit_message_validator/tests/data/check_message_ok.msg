Add mediawiki::iwlink define and use it with role::mobilefrontend

Add a new Puppet define that can be used to easily add rows to the
interwiki links table. The define is used to add a few interwiki
language links to mobilewiki provisioned by role:mobilefrontend.

Bug: T106633
Change-Id: Ifcd397165df1cbf9fa04f2044e1bb33ad7414d8d
