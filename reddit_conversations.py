#!/usr/bin/python3
# A program which creates a tkinter window were in it is possible
# to see reddit conversations and filter them by length, participants
# response time and sentiment.

# Author: J.F.P. (Richard) Scholtens



from tkinter import *
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import ttk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import praw
import threading
import datetime
import json


class Application(Frame):
    def __init__(self, master=None):
        """This class creates a window with two frames."""
        Frame.__init__(self, master)
        self.grid()
        self.master.title("Reddit conversation sentiment.")

        # Configuring the window with rows and columns.
        for r in range(6):
            self.master.rowconfigure(r, weight=1)    
        for c in range(6):
            self.master.columnconfigure(c, weight=1)

        # Creates two frames
        self.frame1 = Frame(master, height=100,width=300, bg="white")
        self.frame1.grid(row = 0, column = 0, rowspan = 6, columnspan = 3, sticky = W+E+N+S) 
        self.frame2 = Frame(master, height=100,width=150)
        self.frame2.grid(row = 0, column = 3, rowspan = 6, columnspan = 3, sticky = W+E+N+S)

        # Creates labels that explain the different filters
        Label(self.frame2, text="Min. number of participants:").grid(column=0, row=0, sticky='w')
        Label(self.frame2, text="Max. number of participants:").grid(column=0, row=1, sticky='w')
        Label(self.frame2, text="Min. length of conversation:").grid(column=0, row=2, sticky='w')
        Label(self.frame2, text="Max. length of conversation:").grid(column=0, row=3, sticky='w')
        Label(self.frame2, text="Min. response time in minutes:").grid(column=0, row=4, sticky='w')
        Label(self.frame2, text="Max. response time in minutes:").grid(column=0, row=5, sticky='w')
        Label(self.frame2, text="Sentiment:").grid(column=0, row=6, sticky='w')

        # Create update button
        Button(self.frame2, text="Update",  command=self.start).grid(column=1,row=12)

        # Create filter buttons
        self.min_participants = StringVar(self.frame2)
        self.min_participants.set("2")
        self.opt = OptionMenu(self.frame2, self.min_participants, "2","3","4","5","6","7","8","9","10").grid(column=1,row=0)

        self.max_participants = StringVar(self.frame2)
        self.max_participants.set("10")
        self.opt2 = OptionMenu(self.frame2, self.max_participants, "2","3","4","5","6","7","8","9","10").grid(column=1,row=1)

        # Create entry for min comments
        self.min_comments = Entry(self.frame2, width=6)
        self.min_comments.insert(0, "2")
        self.min_comments.grid(column=1,row=2)

        # Create entry for max comments
        self.max_comments = Entry(self.frame2, width=6)
        self.max_comments.insert(10, "10")
        self.max_comments.grid(column=1,row=3)

        # Creates spinbox for min time
        self.time_value = StringVar(self.frame2)
        self.time_value.set("0")
        self.min_time = Spinbox(self.frame2, from_=0, to=2880, increment = 1, textvariable=self.time_value, width=4).grid(column=1, row=4)

        # Creates spinbox for max time
        self.time_value2 = IntVar(self.frame2)
        self.time_value2.set("2880")
        self.max_time = Spinbox(self.frame2, from_=-0, to = 2880, increment = 1, textvariable=self.time_value2, width=4).grid(column=1, row=5)

        # Creates an option menu where you can pick the sentiment you want
        self.sentiment = StringVar(self.frame2)
        self.sentiment.set("Neutral")
        self.opt3 = OptionMenu(self.frame2, self.sentiment, "Neutral", "Positive", "Negative").grid(column=1, row=6)

        # Create a menu instance
        menu = Menu(self.master)
        self.master.config(menu=menu)

        # Create the file objects
        menu_file = Menu(menu)
        menu.add_cascade(menu=menu_file, label='File')
        menu_file.add_command(label='Open', command=self.load)
        menu_file.add_command(label='Exit', command=self.master.quit)

        menu_edit = Menu(menu)
        menu.add_cascade(menu=menu_edit, label='Search')
        menu_edit.add_command(label='Search username', command=self.search_username)

        menu_3 = Menu(menu)
        menu.add_cascade(menu=menu_3, label='Credentials')
        menu_3.add_command(label='Reset', command=self.reset)
        menu_3.add_command(label='Change', command=self.newcredentials)  

        # Adds a seperator between menufiles.
        menu_file.add_separator()

        # Creates text in the window with a scrollbar wich can be edited .
        self.S = Scrollbar(self.frame1)
        self.T = Text(self.frame1)
        self.S.pack(side=RIGHT,fill=Y)
        self.T.pack(side=LEFT, fill=Y)
        self.S.config(command=self.T.yview)
        self.T.config(yscrollcommand=self.S.set)

        # Logging in on Reddit.  
        self.username = "USERNAME"
        self.password = "PASSWORD"
        self.client_id = "CLIENT_ID"
        self.client_secret = "CLIENT_SECRET" 
        self.bot_login()
        self.file = None
        self.sid = SentimentIntensityAnalyzer()

   
    def newcredentials(self):
        """This function asks username, password, client id and clientsecret. It then writes the answers to credentials.txt."""
        self.username = simpledialog.askstring("Input","What is the username?")
        self.password = simpledialog.askstring("Input","What is the password?")
        self.client_id = simpledialog.askstring("Input","What is the client id?")
        self.client_secret = simpledialog.askstring("Input","What is the client secret?")
        self.bot_login()

    def reset(self):
        """This function rewrites credentials.txt with the lines of the back-up.txt."""
        self.username = "mingbai"
        self.password = "Spices"
        self.client_id = "_J4D2EctRUBJvg"
        self.client_secret = "Xx0CvhFNIHhA_d5AfmDhx8sEYOw" 
        self.bot_login()


    def bot_login(self):
        """Reads every line from credentials.txt and logs in reddit praw."""
        self.r = praw.Reddit(username = self.username,
            password = self.password,
            client_id = self.client_id,
            client_secret = self.client_secret,
            user_agent = "Human Interaction IK bot")

        try:
            self.r.user.me()
        except:
            self.T.delete(1.0, END)
            print("Your credentials are invalid. Please fill in the correct credentials.")
            self.T.insert(END, "Your credentials are invalid. Please fill in the correct credentials.")


    def filterinput(self, data):
        """Checks which filters are set and passes
        the remaining conversations to the print function.
        It checks for number of participants, length of the
        conversation, amount of time in between and sentiment."""
        try:
            min_participants = self.min_participants.get()
            max_participants = self.max_participants.get()
            min_comments = self.min_comments.get()
            max_comments = self.max_comments.get()
            sentiment = self.sentiment.get()
            min_time = int(self.time_value.get())*60
            max_time = int(self.time_value2.get())*60
            count = 1
            conv_lst = []
            new_conv = []
            for user_dic in self.file:
                conversation = user_dic["Conversation"]
                participants = user_dic["Participants"]
                if (len(conversation) >= int(min_comments) and 
                    len(conversation) <= int(max_comments) and 
                    participants >= int(min_participants) and 
                    participants <= int(max_participants)):
                    sent_analyze = self.sentimentfinder(conversation)
                    if sent_analyze == sentiment:
                        prev_timestamp = False
                        for dic in conversation:
                            datetimeFormat = '%Y-%m-%d %H:%M:%S'
                            conv =[dic]
                            conv.sort(key=lambda x:x["Timestamp"])
                            comment = self.r.comment(id=dic["Comment"])
                            timestamp = str(datetime.datetime.fromtimestamp(comment.created_utc))
                            count += 1
                            if prev_timestamp:
                                diff = datetime.datetime.strptime(timestamp, datetimeFormat) - datetime.datetime.strptime(prev_timestamp, datetimeFormat)
                                if min_time < diff.seconds and diff.seconds < max_time:
                                    new_conv.append(dic)
                            prev_timestamp = timestamp
                        conv_lst.append({"User": self.user, "Conversation": new_conv, "Participants": participants})
                        new_conv = []
            self.print_by_order(conv_lst)
            self.frame2.config(state='normal', text="Filter")
        except TclError:
            pass


    def sentimentfinder(self, lst):
        """Finds the sentiment of a conversation and returns it."""
        oldsentiment = 0
        message = []
        sentimentset = set()
        for dic in lst:
            comment = self.r.comment(id=dic["Comment"])
            scores = self.sid.polarity_scores(comment.body)
            newsentiment = scores['compound']
            if oldsentiment > newsentiment:
                sentimentset.add('Negative')
            elif newsentiment > oldsentiment:
                sentimentset.add('Positive')
            else:
                sentimentset.add('Neutral')
            oldsentiment = newsentiment
            if len(sentimentset) == 1:
                return list(sentimentset)[0]


    def load(self):
        """This function allows the user to load in json files."""
        file_path =  filedialog.askopenfilename(title = "Select file", filetypes = [('JSON file','.json')])
        if file_path:
            self.T.delete(1.0,END)
            with open(file_path, encoding='utf-8') as f:
                data = json.loads(f.read())
                self.print_by_order(data)
        self.file = data


    def start(self):
        """This function allows threading so the program is going to freeze."""
        threading.Thread(target=self.get_comments, daemon=True).start()


    def search_username(self):
        """This function allows the user to look for a different username."""
        check = True
        while check:
            try:
                self.user = simpledialog.askstring("Input","Please insert a username?")
                check = False
            except:
                print("The window glitched. Please try again.")
                pass
        self.start()


    def get_comments(self):
        """This function searches for all the comments made by the given username.
        It makes dictionaries as following:
        {User, Participants, Conversation: {Timestamp, Comment, User}}"""
        check = True
        while check:
            if not self.file:
                try:
                    self.user = simpledialog.askstring("Input","Please insert a username?")
                    if self.user:
                        check = False
                except:
                    print("The window glitched. Please try again.")
                    pass
            else:
                break
        conv_lst = []
        count = 0
        try:
            self.r.redditor(self.user).fullname
            author_lst = []
            for comment in self.r.redditor(self.user).comments.new(limit=100):
                count += 1
                conversation = []
                ancestor = comment
                refresh_counter = 0
                while not ancestor.is_root:
                    ancestor = ancestor.parent()
                    if refresh_counter % 9 == 0:
                        ancestor.refresh()
                    refresh_counter += 1
                if 2 < len(ancestor.replies) < 10:
                    author_lst.append(ancestor.author)
                    if ancestor.author:
                        conversation.append({"Timestamp": ancestor.created_utc, "Comment": str(ancestor.id), "User": ancestor.author.name})
                    else:
                        conversation.append({"Timestamp": ancestor.created_utc, "Comment": str(ancestor.id), "User": "Deleted user"})
                    for reply in ancestor.replies:
                        try:
                            author_lst.append(reply.author)
                            conversation.append({"Timestamp": reply.created_utc, "Comment": str(reply.id), "User": reply.author.name})
                        except:
                            pass
                    conversation = [dict(tupleized) for tupleized in set(tuple(sorted(item.items())) for item in conversation)]
                    author_lst = list(set(author_lst))
                    conv_dic = {"User": self.user, "Conversation": conversation, "Participants": len(author_lst)}
                    conv_lst.append(conv_dic)
                    conversation = []
                    author_lst = []
            self.file = conv_lst
            self.filterinput(conv_lst)
        except:
            print("This username is not available.")


    def print_by_order(self, data):
        """This function inserts the conversations in the correct order into the left frame.
        The correct order is determined by the timestamp."""
        self.T.delete(1.0, END)
        try:
            dic = data[0]
            self.user = dic["User"]
            conv_file = open(self.user + '.json','w')
            json.dump(data, conv_file)
            self.file = data
            for user_dic in data:
                count = 0
                conversation = user_dic["Conversation"]
                prev_timestamp = False
                for dic in conversation:
                    comment = self.r.comment(id=dic["Comment"])
                    timestamp = str(datetime.datetime.fromtimestamp(comment.created_utc))
                    count += 1
                    datetimeFormat = '%Y-%m-%d %H:%M:%S'
                    if prev_timestamp:
                        diff = abs(datetime.datetime.strptime(timestamp, datetimeFormat) - datetime.datetime.strptime(prev_timestamp, datetimeFormat))
                        print("({0}) {1} {2}:\t{3}\n".format(count, diff, comment.author, comment.body.split('\n', 1)[0]))
                        self.T.insert(END, "({0}) {1} {2}:\t{3}\n".format(count, diff, comment.author, comment.body.split('\n', 1)[0]))
                    else:
                        print("({0}{1:<9} {2}:\t{3}\n".format(count, ")", comment.author, comment.body.split('\n', 1)[0]))
                        self.T.insert(END, "({0}{1:<9} {2}:\t{3}{2}\n".format(count, ")", comment.author, comment.body.split('\n', 1)[0]))
                    prev_timestamp = timestamp
                self.T.insert(END, "\n")
            conv_file.close()
        except:
            self.T.insert(END, "No conversations were found.")
            print("No conversations were found")


def main():
    """Starts up the application."""
    root = Tk()
    app = Application(master=root)
    app.mainloop()
if __name__ == "__main__":
    main()