Email 2 PushBullet
========

Email to PushBullet notification


This simple script allows to redirect mail input(from postfix, for example) from a certain mail address to PushBullet notification. Useful to send pushes from sources which are able to send email only.


### Example usage

Lets imagine that we want to redirect all emails sent to push@example.com to your PushBullet account(and therefore to your mobile devices, browser excensions, etc)
Keep in mind that instructions below were tested on Debian 6 with python 2.6
So, thats what you should do:

#### Step zero: setup and configure postfix for domain example.com and other prerequisites

Bla-bla-bla

#### Step 1: create shell script

First, create shell script which will contain email2pb call and an API key. If you will directly specify python script with a API key in aliases file - this'll be a major security hole.
So our script will be something like this:

```
#!/bin/sh
/usr/bin/python /var/spool/postfix/email2pb/email2pb.py --key YOUR_PUSHBULLET_API_KEY
```

Let's name it...umm... `/var/spool/postfix/email2pb/email2pb`
And make it executable:

```
chmod +x /var/spool/postfix/email2pb/email2pb
```

Why there? My example was tested in Debian, and postfix's home dir on Debian 6 is /var/spool/postfix
Rememer, postfix should be able to acces your script.


#### Step 2: add mail alias

Open /etc/aliases file and append a line there:

```
push: |/var/spool/postfix/email2pb/email2pb
```
Save the file and execute `newaliases` command.

#### Step 3: test it

Send email to push@example.com and, if it didn't work, check /var/log/mail.log


Thats it.
