This is the subject line of the commit

The body of the commit message starts after a blank line. It contains just
about any random text, but each line should not exceed 100 characters. Really
there is no good reason for any body line to exceed 72 characters (80 column
display with an 8 character tab leading the line) except in the case of a long
URL that is embedded in the message.

The commit message ends with a footer section containing one or more lines
providing parsable meta-data about the commit such as Phabricator tasks that
it addresses and the unique Gerrit change identifier for the patch. This
footer must be separated from the message body by a single blank line.

Other checks:
- First line <=80 characters
- Second line blank
- No line >100 characters (unless it is only a URL)
- Footer lines ("Foo: ...") are capitalized and have a space after the ':'
- "Bug: " is followed by one task id ("Tnnnn")
- "Depends-On:" is followed by one change id ("I...")
- "Change-Id:" is followed one change id ("I...")
- No "Task: ", "Fixes: ", "Closes: " lines
- Message has at least 3 lines (subject, blank, Change-Id)
- For any footer line, next line is not blank
- For any footer line, prior line is another footer line or blank
- Exactly one "Change-Id: " line per commit
- Any "Bug:" and "Depends-On:" lines come before "Change-Id:"
- "(cherry picked from commit ...)" is last line in footer if present

https://www.mediawiki.org/wiki/Gerrit/Commit_message_guidelines

Bug: T109119
Bug: T142804
Depends-On: I2deb4cd50d50a87a34b0bf4277ad55f77e75dd0d
Change-Id: Ifcd397165df1cbf9fa04f2044e1bb33ad7414d8d
(cherry picked from commit a24ca11e277afd8b5259d44b2d645d4dbb99502f)
