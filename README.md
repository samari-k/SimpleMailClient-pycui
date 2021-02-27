# SimpleMailClient-pycui
A simple mail client using py_cui, imapclient and pyzmail

## Description:

   This script lets you connect to an IMAP-Server, select a folder and read the Emails inside the selected folder.
   For a faster access the last used servername and email address are stored in a txt-file and used at next start.
   Next milestone will be the functionality of sending emails.

   For the user interface I use py_cui (https://github.com/jwlodek/py_cui).
   
   For interaction with the server I use imapclient (https://github.com/mjs/imapclient).
   
   For reading the mails I use pyzmail36 (https://github.com/ascoderu/pyzmail).

## Usage:

   Use the arrow keys to switch between widgets. Press Enter to focus the selected widget and Escape to leave the
   focus mode.
   Enter server/mail/password details, select connect and press Enter. The folders will now be presented in the
   folder widget.
   Select a folder to view the contained mails in the seected folder widget. (This may take a while, stay calm!)
   Select a mail to read the message in the message-widget.
   If you like to connect to a different account, you have to select the disconnect button first.

 Author:   samari-k
 Version:  0.1
