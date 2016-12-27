import subprocess

def get_win_ratio(line):
	return float(line.split('won ')[1].split('%')[0])

def get_rating(line):
	return float(line.split('(')[1].split(' of')[0])

def play_match(p1, p2):
	match = subprocess.Popen("python rpsrunner.py " + p1 + " " + p2,
									stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
	return match.communicate()[0]
