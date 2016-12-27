# this will be a script for automatic tournament. (chris)
import sys
import operator
import Util

tournament_win_ratio = {}
tournament_rating = {}

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

			output = Util.play_match(p1, p2)

			p1_info = output.split(p1)[1].split('\n')
			p2_info = output.split(p2)[1].split('\n')

			p1_win_ratio = Util.get_win_ratio(p1_info[0])
			p1_rating = Util.get_rating(p1_info[1])
			p2_win_ratio = Util.get_win_ratio(p2_info[0])
			p2_rating = Util.get_rating(p2_info[1])

			tournament_win_ratio[p1] += p1_win_ratio
			tournament_rating[p1] += p1_rating
			tournament_win_ratio[p2] += p2_win_ratio
			tournament_rating[p2] += p2_rating

			m += 1
			print("Match " + str(m) + " of " + str(total_matches))

	sorted_dict = sorted(tournament_rating.items(), key=operator.itemgetter(1), reverse=True)
	output_string = ""

	for i in sorted_dict:
		player = i[0]
		output_string += player + ": " + str(tournament_win_ratio[player]/matches_per_player) \
						 + "% / "+ str(tournament_rating[player]/matches_per_player) + "\n"

	f = open("output_tournament.txt", "w+")
	f.write(output_string)
	f.close()

def main():
	players_path = sys.argv[1:]
	if(len(players_path) < 2):
		print("You need to pass at least two players")
		exit(0)

	play_matches(players_path)


main()