
from subprocess import Popen, PIPE
def os_system(command):
    process = Popen(command, stdout=PIPE, shell=True)
    while True:
        line = process.stdout.readline()
        if not line:
            break
        yield line

def orderTally(tally):
	output = list()
	SortedwordsTally2 = sorted(tally.items(), key=lambda x: (-x[1], x[0]))
	for i in SortedwordsTally2:
		tempList = list()
		tempList.append(i[0])
		tempList.append(i[1])
		output.append(tempList)	
	return output

def trendingwords(num_days, num_words, blacklist_limit):
	first = True
	all_data = dict()
	sectionCount = 0
	interval = num_days*24*60*60
	currentTime = 0

	first_section = True	
	blacklist = dict()

	loop_count = 0
	for line in os_system('sqlite3 ~/Library/Messages/chat.db "select handle_id, is_from_me, date, text from message"'):

		line = line.strip()
		
		elems = line.split("|")
		
		if len(elems) > 4: # that means that there were "|" symbols in the text message
			while len(elems) > 4:
				elems[len(elems) - 2] =  elems[len(elems) - 2] + "|" + elems[len(elems) - 1]
				elems.remove(elems[len(elems) - 1])


		if len(elems) == 4: #that's what we expect
			person = elems[0]
			speaker = elems[1]
			time = elems[2]
			text = elems[3]

			if first is True:
				# print msgs.returnDatetime(time)
				currentTime = int(time)
				all_data[sectionCount] = dict()
			first = False

			words = text.split()

			if int(time) - currentTime <= interval:
				for word in words:
					if word not in all_data[sectionCount]:
						all_data[sectionCount][word] = 0
					all_data[sectionCount][word] += 1
					if first_section is True and blacklist_limit is not 0:
						# print "added loop " + str(loop_count)
						blacklist[word] = 0
					elif loop_count < blacklist_limit:   #makes sense?
						if word not in blacklist:
							# print "added loop " + str(loop_count)
							blacklist[word] = 0


			elif int(time) - currentTime > interval:
				loop_count += 1
				# print blacklist
				first_section = False
				to_delete = list()
				for black_word in blacklist:
					if black_word not in all_data[sectionCount]:
						blacklist[black_word] += 1
						if blacklist[black_word] >= blacklist_limit:
							to_delete.append(black_word)
				for delete_this in to_delete:
					blacklist.pop(delete_this, None)
				currentTime = int(time)
				sectionCount += 1
				col_words = dict()
				all_data[sectionCount] = dict()
				for word in words:
					if word not in all_data[sectionCount]:
						all_data[sectionCount][word] = 0
					all_data[sectionCount][word] += 1



		elif len(elems) == 1: #that means there was only text because the text message was printed in several lines
			text = elems[0]
			words = text.split()
			for word in words:
				if word not in all_data[sectionCount]:
					all_data[sectionCount][word] = 0
				all_data[sectionCount][word] += 1
		else:
			print "-"*20 + "\n" + "[!] something went wrong with this line" + "\n" + "its elements are in this array:"
			print elems
			print "-"*20

		
	
	for segment in all_data:
		ordered_tally = orderTally(all_data[segment])
		print str(segment) + ". " + str(num_days) + " days:"
		
		if len(ordered_tally) <= num_words:
			for word, tally in ordered_tally:
				print "\t", word, tally
		else:
			c = 0
			for word, tally in ordered_tally:
				if c >= num_words:
					break
				if word not in blacklist:
					print "\t", word, tally
					c += 1

# first argument: amount of days of one time segment
# second argument: amount of words printed out per time segment
# third argument: blacklisting parameter modifies how often 
# 	a word has to not appear in order to get off the blacklist 
# 	(the higher, the more words end up on the black list
#	if it's 0, then the blacklist will be empty)


trendingwords(30, 5, 29)







