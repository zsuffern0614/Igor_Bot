import discord
import asyncio
import datetime
import time



class MyClient(discord.Client):
    def __init__(self):
        super().__init__()
        self.id = 351919953013637130
        self.name = 'Igor'
        self.description = 'Movie Curator'
        self.movie_list = []#List of movies weve seen and to vote on
        self.voters = {}#Dict of voters, name:vote
        self.candidates = []
        self.leaders = []
        self.state = 0
        self.wait_time = 30
        self.movie_choice = ""
        self.movie_role = "Camp Counselors"



    def get_string_of_voters(self):
        l = list(self.voters.keys())
        return '\n'.join(l)

    def get_string_of_movies(self):  
        return ''.join(list(reversed(self.movie_list)))

    def get_cnt_of_votes(self):
        l = []
        for key in self.voters:
            l.append(self.voters[key])
        return "\nYes Votes: " + str(l.count("Yes")) + "\n No Votes: " + str(l.count("No")) + "\n Abstain Votes: " + str(l.count("Abstain"))

    def get_yes_votes(self):
        l = []
        for key in self.voters:
            l.append(self.voters[key])
        return str(l.count("Yes"))

    def get_no_votes(self):
        l = []
        for key in self.voters:
            l.append(self.voters[key])
        return str(l.count("No"))

    def reset_voters(self):
        for key in self.voters:
            self.voters[key] = "Abstain"

    def load_movies(self):
        f = open("Movie_Rankings.txt","r")
        ans = f.readline().split(',')
        f.close()
        return list(reversed(ans))

    def save_movies(self, movies):
        f = open("Movie_Rankings.txt","w")
        f.write(",".join(list(reversed(movies))))
        f.close()

    def load_candidates(self):
        f = open("Voter_List.txt","r")
        ans = f.readline().split(',')
        f.close()
        return ans

    def save_candidates(self,voter,erase):
        f = open("Voter_List.txt","w")
        f.write(voter)
        if not erase:
            for voter in self.candidates[:9]:
                f.write(',' + voter)
        f.close()



    @asyncio.coroutine
    def on_ready(self):
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)
        print('------')
        #yield from self.send_message(discord.Object(id='350853529662914571'), 'Hello World!')
        # print(self.get_channel('350853529662914572').voice_members)
        for mem in self.get_channel('218491261152133120').voice_members:
            print(mem.name)
        self.movie_list = self.load_movies()
        self.candidates = self.load_candidates()
        leaders = []
        for mem in self.get_channel('218491261152133120').voice_members:
            for role in mem.roles:
                if self.movie in role.name:
                    leaders.append(mem.name)
        self.leaders = leaders
        # self.movie_list = list(reversed(self.get_channel('350853529662914571').topic.split('\n')))
        print(self.movie_list)
        #yield from self.edit_channel(self.get_channel('350853529662914571'),topic='please chnge')

    @asyncio.coroutine
    def on_message(self,message):
        if message.content[-5:] == 'Igor!':
            
            if message.content.startswith('Igor!'):
                yield from client.send_message(message.channel, 'Yes Master')

            if message.author.name in self.leaders and message.content.startswith('Science'):
                self.movie_choice = message.content[8:-6]
                self.movie_list = self.load_movies()
                self.candidates = self.load_candidates()
                commands = message.content.split(' ')
                yield from client.send_message(message.channel, 'I Shall Start The Voting ' + message.author.name)
                for mem in self.get_channel('218491261152133120').voice_members:
                    self.voters[mem.name] = 'Abstain'
                self.state = 1
                yield from client.send_message(message.channel, 'Eligible Voters are ' + self.get_string_of_voters())
                
                rank = len(self.movie_list);
                for movie in self.movie_list:
                    yield from client.send_message(message.channel, "\nIs " + self.movie_choice + " better then " + movie.replace('\n', ' ') + "?")
                    time = datetime.datetime.now();

                    def check(message):
                        return message.content.startswith('Vote') and self.state == 1 and message.author.name in self.voters and message.content[-5:] == 'Igor!'

                    votes = 0
                    while votes < len(self.voters.keys()) and (datetime.datetime.now() - time).seconds < self.wait_time:
                        if self.state == 0:
                            return True
                        msg = yield from client.wait_for_message(check=check,timeout=1)
                        if msg is not None:
                            if self.voters[msg.author.name] == 'Abstain' and msg.content[5:8] == "Yes":
                                self.voters[msg.author.name] = 'Yes'
                                yield from client.send_message(message.channel, msg.author.name + " Voted Yes!")
                                votes = votes + 1

                            elif self.voters[msg.author.name] == 'Abstain' and msg.content[5:7] == "No":
                                self.voters[msg.author.name] = 'No'
                                yield from client.send_message(message.channel, msg.author.name + " Voted No!")
                                votes = votes + 1
                            else:
                                yield from client.send_message(message.channel, msg.author.name + " You've already voted for this vote!")
                        elif self.state==2:
                            time = datetime.datetime.now()

                        if int(self.get_yes_votes()) + int(self.get_no_votes()) > len(self.voters)/2.0 + 1 and int(self.get_yes_votes()) > int(self.get_no_votes()):
                            break


                    if self.get_yes_votes() >= self.get_no_votes():
                        yield from client.send_message(message.channel, "The vote is: " + self.get_cnt_of_votes() + "\n So I'm getting a general Yes Vibe form the crowd so moving on...")
                        self.reset_voters()

                    else:
                        yield from client.send_message(message.channel, "The vote is: " + self.get_cnt_of_votes() + "\n So I'm getting a general No Vibe form the crowd.")
                        break

                    rank = rank - 1


                yield from client.send_message(message.channel, "It appears that " + self.movie_choice + " is ranked the " + str(rank) + " Movie Of All Time")
                self.movie_list.insert(len(self.movie_list)-rank,self.movie_choice)
                self.save_movies(self.movie_list)
                yield from self.edit_channel(self.get_channel('218490502356533249'),topic="Royal Academy of Movie Sciences Current Findings:\n\n"+"\n".join(list(reversed(self.movie_list))))
                yield from client.send_message(message.channel, "The new rankings have been posted!  Last thing before we end our night of science, " + self.candidates[0] + ", please Choose who will pick the next move!")

                candidates = ''
                for voter in self.voters.keys():
                    print (voter)
                    print (self.candidates)
                    if voter not in self.candidates:
                        candidates = candidates + voter + '\n'


                restart = False
                if candidates == '':
                    yield from client.send_message(message.channel, "It appears that we've gone through the list! So we will restart from the beginning!")
                    candidates = self.get_string_of_voters()
                    restart = True

                
                yield from client.send_message(message.channel, "The following are eligble to pick the next movie!\n" + candidates)

                def check_input(message):
                        return message.content.startswith('Pick') and (message.author.name in self.leaders or message.author.name == self.candidates[0]) and message.content[-5:] == 'Igor!'

                cont = True
                while cont:
                    msg_pick = yield from client.wait_for_message(check=check_input)
                    choice = msg_pick.content[5:-6]
                    if choice not in candidates:
                         yield from client.send_message(message.channel, "I'm terribly sorry but " + choice + " is not eligble to choose the next movie. The following are eligble to pick the next movie!\n" + candidates)
                    else:
                        cont = False

                yield from client.send_message(message.channel, self.candidates[0] + " has chosen " + choice + " to pick the next movie!")
                self.save_candidates(choice,restart)
                yield from client.send_message(message.channel, "And that is it! Every one have a good night! See you next time FOR SCIENCE!")
                self.state = 0




            if message.author.name in self.leaders and message.content.startswith('Pause') and self.state==1:
                yield from client.send_message(message.channel, "I have paused the voting!")
                self.state = 2

            if message.author.name in self.leaders and message.content.startswith('Unpause') and self.state==2:
                yield from client.send_message(message.channel, "We shall continue with the voting!")
                self.state = 1

            if message.author.name in self.leaders and message.content.startswith('Stop') and self.state>0:
                yield from client.send_message(message.channel, "I have stopped the voting!")
                self.state = 0





            if message.content.startswith('Standings') and self.state == 1:
                yield from client.send_message(message.channel, "The Current Standings are: " + self.get_cnt_of_votes())

            if message.author.name in self.leaders and message.content.startswith('Time'):
                self.wait_time = int(message.content[5:-6])  
                yield from client.send_message(message.channel, "I have changed the vote time to " + self.wait_time + " Master " + message.author.name + ".")
     

            if message.content.startswith('Status'):
                msg = "Master " + message.author.name + " I have the following settings: \n"
                msg = msg +  "Name: " + self.name + "\n"
                msg = msg +  "Description: " + self.description + "\n"
                msg = msg +  "Leader: " + ",".join(self.leaders) + "\n"
                msg = msg +  "Wait Time: " + str(self.wait_time) + "\n"


                yield from client.send_message(message.channel, msg)

            if message.content.startswith('Voters'):
                for mem in self.get_channel('218491261152133120').voice_members:
                    self.voters[mem.name] = 'Abstain'
                yield from client.send_message(message.channel, 'Eligible Voters are ' + self.get_string_of_voters())

            if message.content.startswith('Rankings'):
                yield from client.send_message(message.channel, 'The Movie Rankings are: \n\n' + self.get_string_of_movies())

            if message.content.startswith('Picked'):
                candidates = ''
                for cand in self.candidates:
                        candidates = candidates + cand + '\n'
                yield from client.send_message(message.channel, 'Peope who have choosen a movie and are ineligble to pick are: \n\n' + candidates)

            if message.content.startswith('Reload'):
                leaders = []
                self.voters = []
                for mem in self.get_channel('218491261152133120').voice_members:
                    self.voters[mem.name] = 'Abstain'
                    if "Movie Curator" in mem.roles:
                        leaders.append(mem)
                self.movie_list = self.load_movies()
                self.candidates = self.load_candidates()
                self.leaders = leaders


            if message.content.startswith('Rules'):
                yield from client.send_message(message.channel, "The Rules of Movie Night are as follows:\n")
                yield from client.send_message(message.channel, "1) When it's your turn to choose movie night, you can pick whatever movie you want")
                yield from client.send_message(message.channel, "2) Only people who are in the Movie channel Voice Chat are eligible to vote")
                yield from client.send_message(message.channel, "3) We will vote for one movie at a time, from lowest to highest, until we vote in the negative")
                yield from client.send_message(message.channel, "4) Who ever picked the last movie picks who gets to choose the next movie")
                yield from client.send_message(message.channel, "5) Eligible pickers are people who showed up for the movie and haven't picked the last 10 movies. If everyone in the chat has picked a movie, then the list resets and everyone is eligble again.")
                yield from client.send_message(message.channel, "6) When it's your turn to choose movie night, you can pick whatever movie you want")


            if message.content.startswith('Help'):
                yield from client.send_message(message.channel, "These are the following commands to assist with science:\n")
                yield from client.send_message(message.channel, "Rules Igor! - Lists out the rules of Movie Night")
                yield from client.send_message(message.channel, "Rankings Igor! - Lists out the scientific rankings of Movie Night")
                yield from client.send_message(message.channel, "Status Igor! - Lists out my current settings")
                yield from client.send_message(message.channel, "Voters Igor! - Lists out the voters for Movie Night")
                yield from client.send_message(message.channel, "Picked Igor! - Lists out who recently picked a movie\n")

                yield from client.send_message(message.channel, "The following commands are for voting:\n")
                yield from client.send_message(message.channel, "Science [Movie] Igor! - Starts the Voting Process of Movie Night with [Movie], Movie Curator Role Only")
                yield from client.send_message(message.channel, "Vote [Yes/No] Igor! - Vote Yes or No in the Voting Process")
                yield from client.send_message(message.channel, "Pick [Voter] Igor! - Pick who will pick the next movie for Movie Nigh, Movie Curator Role can answer if needed")
                yield from client.send_message(message.channel, "Standings Igor! - Lists out the current vote")
                yield from client.send_message(message.channel, "Pause Igor! - Pauses the the Voting Process, Movie Curator Role Only")
                yield from client.send_message(message.channel, "Unpause Igor! - Unpauses the Voting Process, Movie Curator Role Only")
                yield from client.send_message(message.channel, "Stop Igor! - Stops the Voting Process, Movie Curator Role Only\n")

                yield from client.send_message(message.channel, "The following commands are only avalible to those with the Movie Curator Role:\n")
                yield from client.send_message(message.channel, "Time [time in seconds] Igor! - Changes the time we take per vote")
                yield from client.send_message(message.channel, "Reload Igor! - Reloads the movie and candidates list in case of issues")

        if message.content.startswith('i want to watch'):
            yield from client.send_message(message.channel, "When it's your turn to choose movie night, you can pick whatever movie you want")




#Add functionality for someone to ask for the full list in a private message
#Add call out functionality
#Add WHEN ITS YOUR TURN TO CHOOSE YOU CAN PICK WHICHEVER MOVIE YOU WANT
#IMDB compatible

client = MyClient()
client.run('MzUxOTE5OTUzMDEzNjM3MTMw.DIZpkQ.KT2fL1HkKxEug8e7NGmm34vRH1Y')
