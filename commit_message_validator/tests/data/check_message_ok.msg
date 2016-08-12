This is the subject line of the commit

The body of the commit message starts after a blank line. It contains just
about any random text, but each line should not exceed 100 characters. Really
there is no good reason for any body line to exceed 72 characters (80 column
display with an 8 character tab leading the line) except in the case of a long
URL that is embedded in the message.

Other checks:
- First line <=80 characters
- Second line blank
- No line >100 characters unless it is a URL
- "Bug:" is capitalized
- "Bug:" is followed by a space
- Exactly one task id on each Bug: line
- "Depends-On:" is capitalized
- "Depends-On:" is followed by a space
- Exactly one change id on each Depends-On: line
- No "Task: ", "Fixes: ", "Closes: " lines
- For any "^Bug: " line, next line is not blank
- For any "^Bug: " line, prior line is another Bug: line or empty
- For any "^Depends-On: " line, next line is not blank
- For any "^Depends-On: " line, prior line is Bug|Depends-On or empty
- Exactly one "Change-Id: " line per commit
- For "Change-Id: " line, prior line is empty or "^(Bug|Depends-On): "
- No blank lines between any "(Bug|Depends-On): " lines and "Change-Id: "
- Only "(cherry picked from commit" can follow "Change-Id: "
- Message has at least 3 lines (subject, blank, Change-Id)

https://www.mediawiki.org/wiki/Gerrit/Commit_message_guidelines

Bug: T109119
Depends-On: I2deb4cd50d50a87a34b0bf4277ad55f77e75dd0d
Change-Id: Ifcd397165df1cbf9fa04f2044e1bb33ad7414d8d
(cherry picked from commit a24ca11e277afd8b5259d44b2d645d4dbb99502f)
