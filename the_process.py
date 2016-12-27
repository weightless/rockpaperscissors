# this script test one bot(first at parameters) against all other(the others parameters)
# I called this as "The Process" to test bot before upload to RPS Contest
import sys
import Util

def play_matches(players):
	challenger = players[0]
	challenged = players[1:]

	if(challenger in challenged):
		challenged.remove(challenger)

	final_win_ratio = 0
	final_rating = 0
	final_wins = 0

	for index, p in enumerate(challenged):
		print(str(index+1) + " of " + str(len(challenged)))
		output = Util.play_match(challenger, p)

		challenger_info = output.split(challenger)[1].split('\n')
		p_info = output.split(p)[1].split('\n')

		challenger_win_ratio = Util.get_win_ratio(challenger_info[0])
		challenger_rating = Util.get_rating(challenger_info[1])

		challenged_win_ratio = Util.get_win_ratio(p_info[0])

		if(challenger_win_ratio > challenged_win_ratio):
			final_wins += 1
		final_win_ratio += challenger_win_ratio
		final_rating += challenger_rating

	print("Final test results:")
	print("> " + str(len(challenged)) + " tests")
	print("> Total absolute wins: " + str(final_wins) + "(" + str(final_wins/len(challenged)) + "%)")
	print("> Win ratio: " + str(final_win_ratio/len(challenged)))
	print("> Rating: " + str(final_rating/len(challenged)))

def main():
	players_path = sys.argv[1:]
	if(len(players_path) < 2):
		print("You need to pass at least two players")
		exit(0)

	play_matches(players_path)

main()