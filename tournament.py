# this will be a script for automatic tournament. (chris)
import sys

tournament = {}

def main():
	players_path = sys.argv[1:]
	if(players_path < 2):
		print("You need to pass at least two players")
		exit(0)

	for i in players_path:
		tournament[i] = []


main()