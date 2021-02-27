#! /usr/bin/env python3

####################################################################################################################
# Description:
#
#   This script lets you connect to an IMAP-Server, select a folder and read the Emails inside the selected folder.
#   For a faster access the last used servername and email address are stored in a txt-file and used at next start.
#   Next milestone will be the functionality of sending emails.
#
#   For the user interface I use py_cui (https://github.com/jwlodek/py_cui).
#   For interaction with the server I use imapclient (https://github.com/mjs/imapclient).
#   For reading the mails I use pyzmail36 (https://github.com/ascoderu/pyzmail).
#
# Usage:
#
#   Use the arrow keys to switch between widgets. Press Enter to focus the selected widget and Escape to leave the
#   focus mode.
#   Enter server/mail/password details, select connect and press Enter. The folders will now be presented in the
#   folder widget.
#   Select a folder to view the contained mails in the seected folder widget. (This may take a while, stay calm!)
#   Select a mail to read the message in the message-widget.
#   If you like to connect to a different account, you have to select the disconnect button first.
#
# Author:   samari-k
# Version:  0.1
###################################################################################################################

import py_cui
import imapclient
import pyzmail

# TODO:
#   * integrate subfolders
#   * implement possibility to send/delete/move mails
#   * expand usability by adding more key commands
#   * visualize seen/unseen (maybe by colors?)
#   * use colors
#   * make error handling more elegant
#   * handle error-throwing mouseclicks
#   * show loading-popup while loading messages
#   * implement line-breaks in message-widget
#   * set minimum terminal size for a good look


class SimpleMailClient:
    def __init__(self, master):
        """create the cui with all necessary widgets"""
        
        self.master = master
        self.connection = None    # this will be the connection object, once the connection to the server is set up

        self.server_text_box = self.master.add_text_box('IMAP Server', 5, 0, column_span=2)
        self.email_text_box = self.master.add_text_box('E-Mail', 6, 0, column_span=2)
        self.password_text_box = self.master.add_text_box('Password', 7, 0, password=True, column_span=2)

        self.connect_button = self.master.add_button('connect', 9, 0, command=self.connect)
        self.disconnect_button = self.master.add_button('disconnect', 9, 1, command=self.disconnect)

        self.folder_scroll_menu = self.master.add_scroll_menu('folder', 0, 0, column_span=2, row_span=5)
        self.folder_scroll_menu.set_selectable(False)
        self.folder_scroll_menu.add_key_command(py_cui.keys.KEY_ENTER, self.select_folder)

        self.selected_folder_scroll_menu = self.master.add_scroll_menu('selected folder', 0, 2, column_span=10, row_span=5)
        self.selected_folder_scroll_menu.set_selectable(False)
        self.selected_folder_scroll_menu.add_key_command(py_cui.keys.KEY_ENTER, self.select_mail)

        self.message_text_block = self.master.add_text_block('message', 5, 2, column_span=10, row_span=7)
        self.message_text_block.set_selectable(False)

        try:
            # read server name and email from last login for faster access
            last_login_file = open('lastLogin.txt', 'r')
            self.server_text_box.set_text(last_login_file.readline()[:-1])
            self.email_text_box.set_text(last_login_file.readline())
            last_login_file.close()
        except:
            pass

    def connect(self):
        """connect to mail-server and present folders"""

        server = self.server_text_box.get()
        mail = self.email_text_box.get()
        password = self.password_text_box.get()

        try:
            # connect to specified IMAP-Server
            self.connection = imapclient.IMAPClient(server, ssl=True)
            self.connection.login(mail, password)
            self.message_text_block.set_text('connected successfully')

            # fetch list of all available folders
            folders = self.connection.list_folders()
            for folder in folders:
                self.folder_scroll_menu.add_item(folder[2])

            self.connect_button.set_selectable(False)
            self.disconnect_button.set_selectable(True)
            self.folder_scroll_menu.set_selectable(True)
            self.server_text_box.set_selectable(False)
            self.email_text_box.set_selectable(False)
            self.password_text_box.set_selectable(False)

            # save server name and email for faster future access
            last_login = open('lastLogin.txt', 'w')
            last_login.write('{}\n{}'.format(server, mail))
            last_login.close()

        except Exception as e:
            self.master.show_error_popup('connect', 'An error occured: {}'.format(str(e)))

    def disconnect(self):
        """disconnect from mail-server and clear the widgets"""
        try:
            self.connection.logout()
        except Exception as e:
            self.master.show_error_popup('disconnect', 'An error occured: {}'.format(str(e)))
        self.folder_scroll_menu.clear()
        self.selected_folder_scroll_menu.clear()
        self.message_text_block.set_text('disconnected.')

        self.connect_button.set_selectable(True)
        self.disconnect_button.set_selectable(False)
        self.folder_scroll_menu.set_selectable(False)
        self.selected_folder_scroll_menu.set_selectable(False)
        self.server_text_box.set_selectable(True)
        self.email_text_box.set_selectable(True)
        self.password_text_box.set_selectable(True)

    def select_folder(self):
        """select folder from folder_scroll_menu and present all contained mails"""

        self.selected_folder_scroll_menu.clear()

        try:
            self.connection.select_folder(self.folder_scroll_menu.get())

            mail_uids = self.connection.search()[::-1]  # This stores a list of all unique IDs of the mails in the selected folder

            for mail_uid in mail_uids:
                raw_message = self.connection.fetch([mail_uid], ['BODY[]', 'FLAGS'])
                message = pyzmail.PyzMessage.factory(raw_message[mail_uid][b'BODY[]'])
                subject = message.get_subject()
                sender = message.get_addresses('from')[0][1]

                # put all infos together in one line in the selected_folder_scroll_menu
                self.selected_folder_scroll_menu.add_item('{} - {} - {}'.format(mail_uid, sender, subject))

        except Exception as e:
            self.master.show_error_popup('select_folder', 'An error occured: {}'.format(str(e)))

        self.selected_folder_scroll_menu.set_selectable(True)

    def select_mail(self):
        """select mail from selected_folder_scroll_menu and present its plaintext message in message_text_block"""

        self.message_text_block.clear()
        mail_descriptor = self.selected_folder_scroll_menu.get()
        mail_uid = int(mail_descriptor[:mail_descriptor.find(' ')])

        try:
            raw_message = self.connection.fetch([mail_uid], ['BODY[]', 'FLAGS'])
            message = pyzmail.PyzMessage.factory(raw_message[mail_uid][b'BODY[]'])
            self.message_text_block.set_text(message.text_part.get_payload().decode('UTF-8'))
        except Exception as e:
            self.master.show_error_popup('select_mail', 'An error occured: {}'.format(str(e)))


if __name__ == '__main__':
    root = py_cui.PyCUI(12, 12)
    root.toggle_unicode_borders()
    root.set_title('Simple Mail Client')
    mailclient = SimpleMailClient(root)
    root.start()
