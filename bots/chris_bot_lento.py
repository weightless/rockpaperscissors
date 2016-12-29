import random

class RAM:
	def __init__(self, size, bleaching):
		self.size = size
		self.bleaching = bleaching
		self.ram = {}

	def train(self, position, value):
		if(self.bleaching and position in self.ram):
			self.ram[position] += value
		else:
			self.ram[position] = 1

	def classify(self, position, bleaching_value):
		if(position not in self.ram):
			return 0
		elif(self.bleaching):
			return 1 if self.ram[position] >= bleaching_value else 0
		else:
			return self.ram[position]

	def forget(self, value):
		for index in range(self.size):
			if(index in self.ram):
				self.ram[index] -= value

				if(self.ram[index] <= 0):
					del self.ram[index]

class Discriminator:
	def __init__(self, name, address_size, entry_size, bleaching):
		self.name = name
		self.address_size = address_size
		self.entry_size = entry_size
		self.bleaching = bleaching
		self.rams = []
		self.map = []

		qty_rams = entry_size/address_size
		qty_rams += 0 if(entry_size%address_size==0) else 1

		for i in range(qty_rams):
			self.rams.append(RAM(pow(2,entry_size), bleaching))

		addresses = range(entry_size)
		for index, r in enumerate(self.rams):
			positions = []
			for i in range(address_size):
				if(len(addresses) == 0):
					positions.append(-1)
				else:
					p = random.choice(addresses)
					addresses.remove(p)
					positions.append(p)

			self.map.append(positions)

	def get_ram_access(self, X, ram_index):
		address = ''
		for i in self.map[ram_index]:
			address += '0' if i == -1 else str(X[i])
		final_position = int(address, 2)
		return final_position

	def train(self, X):
		for index, r in enumerate(self.rams):
			final_position = self.get_ram_access(X, index)

			r.train(final_position, 1)

	def classify(self, X, bleaching_value):
		score = 0
		for index, r in enumerate(self.rams):
			final_position = self.get_ram_access(X, index)
			value = r.classify(final_position, bleaching_value)
			score += value
		return score

	def forget(self, value):
		for r in self.rams:
			r.forget(value)

class WiSARD:
	def __init__(self,entry_size,address_size=2,classes=[],bleaching_value=0,forget_value=1,forget_trains=0):
		if(address_size < 2): address_size = 2
		if(bleaching_value < 0): bleaching_value = 0
		if(len(classes) < 2): classes = [0, 1]

		self.address_size = address_size
		self.bleaching_value = bleaching_value
		self.entry_size = entry_size
		self.classes = classes
		self.discriminators = {}
		self.trained = {}
		self.forget_trains = forget_trains
		self.forget_value = forget_value

		for c in self.classes:
			self.discriminators[c] = Discriminator(c, address_size, entry_size, bleaching_value>0)
			self.trained[c] = 0

	def assert_test(self, expected, real, msg=''):
		if(expected != real):
			msg = 'assertion failed: ' + msg + ' (Expected: ' + str(expected) + str(type(expected)) + ' | Real: ' + str(real) + str(type(real)) + ')'
			raise Exception(msg)

	def train(self, X, y):
		self.assert_test(len(X), self.entry_size)
		self.assert_test(True, y in self.classes)
		self.discriminators[y].train(X)

		self.trained[y] += 1
		if(self.forget_trains > 0 and self.trained[y] > self.forget_trains):
			self.discriminators[y].forget(self.forget_value)

	def classify(self, X):
		self.assert_test(len(X), self.entry_size)
		result = {}
		last_result = None

		for d in self.discriminators:
			result[d] = self.discriminators[d].classify(X, self.bleaching_value)

		if self.bleaching_value > 0:
			actual_bleaching = self.bleaching_value

			while True:
				ambiguity = False
				max_score = 0

				for r in result:
					if(result[r] > max_score):
						max_score = result[r]
						ambiguity = False
					elif(result[r] == max_score):
						ambiguity = True

				if(ambiguity and max_score > 1):
					actual_bleaching += 1
					last_result = result
					result[d] = self.discriminators[d].classify(X, actual_bleaching)
				else:
					if(ambiguity and last_result is not None) : result = last_result
					break

		for r in result:
			result[r] /= float(len(self.discriminators[r].rams))

		return result

def get_x(history, target):
    x = []
    
    if(type(target) == type('')):
    	target = char2num[target]

    for i in history:
    	if(i == target):
    		x.append(1)
    	else:
    		x.append(0)

    return x

def get_x_two_code(history, target=''):
    x = []
    
    for i in history:
        if(i == "R"):
            x.extend([1,0])
        elif(i == "P"):
            x.extend([0,1])
        else:
            x.extend([1,1])

    return x

def get_x_three_code(history, target=''):
    x = []
    
    for i in history:
        if(i == "R"):
            x.extend([1,0,0])
        elif(i == "P"):
            x.extend([0,1,0])
        else:
            x.extend([0,0,1])

    return x


if input == "":
    turn = 0
    history = []
    last_prediction = ''
    aux = 0

    # hyperparameters
    history_size = 8
    min_random_turns = 0
    final_random_turns = 0
    address_size=4
    bleaching_value=1
    get_x_function=get_x
    get_x_code_size=1
    forget_trains=10
    # ****************
    wisard_is_rock = WiSARD(entry_size=get_x_code_size*history_size,address_size=address_size,
    						bleaching_value=bleaching_value,classes=["R", "PS"],forget_trains=forget_trains)
    wisard_is_paper = WiSARD(entry_size=get_x_code_size*history_size,address_size=address_size,
    						bleaching_value=bleaching_value,classes=["P", "RS"],forget_trains=forget_trains)
    wisard_is_scissor = WiSARD(entry_size=get_x_code_size*history_size,address_size=address_size,
    						bleaching_value=bleaching_value,classes=["S", "RP"],forget_trains=forget_trains)

    char2num = {"R":0, "P":1, "S":2}
    num2char = {0:"R", 1:"P", 2:"S"}
    defeated_by = {"R":"P", "P":"S", "S":"R"}

    prediction = random.choice(["R","P","S"])
    output = defeated_by[prediction]

elif len(history) < history_size or turn < min_random_turns or turn > 1000 - final_random_turns:
    prediction = random.choice(["R","P","S"])
    output = defeated_by[prediction]
    history.append(char2num[input])
    if(len(history) > history_size) : history.pop(0)
else:
	x_R = get_x_function(history, "R")
	x_P = get_x_function(history, "P")
	x_S = get_x_function(history, "S")

	# training
	if(input == "R"):
		wisard_is_rock.train(x_R, "R")

		wisard_is_paper.train(x_P, "RS")
		wisard_is_scissor.train(x_S, "RP")
	elif(input == "P"):
		wisard_is_paper.train(x_P, "P")

		wisard_is_rock.train(x_R, "PS")
		wisard_is_scissor.train(x_S, "RP")
	else:
		wisard_is_scissor.train(x_S, "S")

		wisard_is_rock.train(x_R, "PS")
		wisard_is_paper.train(x_P, "RS")


	# updating history
	history.append(char2num[input])
	history.pop(0)

	x_R = get_x_function(history, "R")
	x_P = get_x_function(history, "P")
	x_S = get_x_function(history, "S")

	# classifying
	result_R = wisard_is_rock.classify(x_R)
	result_P = wisard_is_paper.classify(x_P)
	result_S = wisard_is_scissor.classify(x_S)

	possibilities = []
	if(result_R['R'] > result_R['PS']):
		possibilities.append('R')
	if(result_P['P'] > result_P['RS']):
		possibilities.append('P')
	if(result_S['S'] > result_S['RP']):
		possibilities.append('S')

	# print(str(result_R) + str(result_P) + str(result_S))
	if(len(possibilities) > 0):
		if(len(possibilities) == 3) : aux += 1
		prediction = random.choice(possibilities)
	else:
		aux += 1
		prediction = random.choice(["R","P","S"])

	output = defeated_by[prediction]

last_prediction = prediction
turn += 1
if(turn == 1000) : print aux