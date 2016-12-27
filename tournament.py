# this will be a script for automatic tournament. (chris)
import sys
import subprocess
import operator

tournament_win_ratio = {}
tournament_rating = {}

def get_win_ratio(line):
	return float(line.split('won ')[1].split('%')[0])

def get_rating(line):
	return float(line.split('(')[1].split(' of')[0])

def play_matches(players):
	for i in players:
		tournament_win_ratio[i] = 0
		tournament_rating[i] = 0

	matches_per_player = 2 * len(players) - 2
	total_matches = len(players) * (len(players) - 1)
	m = 0
	for p1 in players:
		for p2 in players:
			if(p1 == p2):
				continue

			match = subprocess.Popen("python rpsrunner.py " + p1 + " " + p2,
									stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
			output = match.communicate()[0].split('\n')
			if(p1 in output[7]):
				p1_win_ratio = get_win_ratio(output[7])
				p1_rating = get_rating(output[8])
				p2_win_ratio = get_win_ratio(output[11])
				p2_rating = get_rating(output[12])
			else:
				p1_win_ratio = get_win_ratio(output[11])
				p1_rating = get_rating(output[12])
				p2_win_ratio = get_win_ratio(output[7])
				p2_rating = get_rating(output[8])

			tournament_win_ratio[p1] += p1_win_ratio
			tournament_rating[p1] += p1_rating
			tournament_win_ratio[p2] += p2_win_ratio
			tournament_rating[p2] += p2_rating

			m += 1
			print("Match " + str(m) + " of " + str(total_matches))

	sorted_dict = sorted(tournament_rating.items(), key=operator.itemgetter(1), reverse=True)

	for i in sorted_dict:
		player = i[0]
		print(player + ": " + str(tournament_win_ratio[player]/matches_per_player) + "% / " + 
			  str(tournament_rating[player]/matches_per_player))

def main():
	players_path = sys.argv[1:]
	if(players_path < 2):
		print("You need to pass at least two players")
		exit(0)

	play_matches(players_path)



main()