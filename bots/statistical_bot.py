import random
from random import randint

class RAM:

    def __init__(self, addressSize, entrySize, addressing, decay=None, up=None):
        self.addressing = addressing
        self.decay = decay
        self.up = up
        self.ram = {}
        self.address = [ randint(0, entrySize-1) for x in range(addressSize) ]

    def _addressToIndex(self, entry):
        binCode = []
        for i in self.address:
            binCode.append(entry[i])
        return self.addressing(binCode)

    def _acumulateRam(self, index):
        if index not in self.ram:
            self.ram[index] = 0
        self.ram[index] += 1

    def _getValue(self, index):
        if index not in self.ram:
            return 0
        else:
            return self.ram[index]

    def train(self, entry, negative=False):
        index = self._addressToIndex(entry)
        if not negative:
            if self.up is None:
                self._acumulateRam(index)
            else:
                self.up(entry=entry, ram=self.ram, address=self.address, index=index)
        else:
            self.decay(entry=entry, ram=self.ram, address=self.address, index=index)

    def classify(self, entry):
        index = self._addressToIndex(entry)
        return self._getValue(index)


class Discriminator:

    def __init__(self, name, entrySize, addressSize, addressing, numberOfRAMS=None, decay=None, up=None):
        if numberOfRAMS is None:
            numberOfRAMS = int(entrySize/addressSize)
        self.rams = [ RAM(addressSize, entrySize, addressing, decay=decay, up=up) for x in range(numberOfRAMS) ]

    def train(self, entry, negative=False):
        for ram in self.rams:
            ram.train(entry, negative)

    def classify(self, entry):
        return [ ram.classify(entry) for ram in self.rams ]

class Addressing:
    def __call__(self, binCode): # binCode is a list of values of selected points of entry
        index = 0
        for i,e in enumerate(binCode):
            if e > 0:
                index += pow(2,i)
        return index


class WiSARD:
    def __init__(self,
            addressSize = 3,
            numberOfRAMS = None,
            bleachingActivated = True,
            seed = random.randint(0, 1000000),
            sizeOfEntry = None,
            classes = [],
            verbose = True,
            addressing = Addressing(),
            makeBleaching = None,
            decay = None,
            up = None):

        self.seed = seed
        self.decay = decay
        self.up = up
        random.seed(seed)

        if addressSize < 3:
            self.addressSize = 3
        else:
            self.addressSize = addressSize
        self.numberOfRAMS = numberOfRAMS
        self.discriminators = {}
        self.bleachingActivated = bleachingActivated
        self.addressing = addressing
        if makeBleaching is None:
            self.makeBleaching = self._makeBleaching
        else:
            self.makeBleaching = makeBleaching

        if sizeOfEntry is not None:
            for aclass in classes:
                self.discriminators[aclass] = Discriminator(
                    aclass, sizeOfEntry, self.addressSize,
                    self.addressing, self.numberOfRAMS, decay=self.decay, up=self.up)

    def _makeBleaching(self, discriminatorsoutput):
        bleaching = 0
        ambiguity = True
        biggestVote = 2
        while ambiguity and biggestVote > 1:
            bleaching += 1
            biggestVote = None
            ambiguity = False
            for key in discriminatorsoutput:
                discriminator = discriminatorsoutput[key]
                limit = lambda x: 1 if x >= bleaching else 0
                discriminator[1] = sum(map(limit, discriminator[0]))
                if biggestVote is None or discriminator[1] > biggestVote:
                    biggestVote = discriminator[1]
                    ambiguity = False
                elif discriminator[1] == biggestVote:
                    ambiguity = True
            if self.bleachingActivated:
                break

        return discriminatorsoutput

    def train(self, entries, classes):
        sizeOfEntry = len(entries[0])
        for i,entry in enumerate(entries):
            aclass = str(classes[i])
            if aclass not in self.discriminators:
                self.discriminators[aclass] = Discriminator(
                    aclass, sizeOfEntry, self.addressSize,
                    self.addressing, self.numberOfRAMS, decay=self.decay, up= self.up)
            self.discriminators[aclass].train(entry)
            if self.decay is not None:
                for key in self.discriminators:
                    if key != aclass:
                        self.discriminators[key].train(entry, negative=True)

    def classifyEntry(self, entry):
        discriminatorsoutput = {}
        for keyClass in self.discriminators:
            discriminatorsoutput[keyClass] = [self.discriminators[keyClass].classify(entry),0]

        discriminatorsoutput = self.makeBleaching(discriminatorsoutput)

        calc = lambda key: (key, float(discriminatorsoutput[key][1])/len(discriminatorsoutput[key][0]))
        classes = list(map(calc,discriminatorsoutput))
        classes.sort(key=lambda x: x[1], reverse=True)

        return classes


    def classify(self, entries):
        output=[]
        for i,entry in enumerate(entries):
            aclass = self.classifyEntry(entry)[0][0]
            output.append((entry, aclass))
        return output

class Decay:

    def __call__(self, **kwargs):
        if kwargs['index'] in kwargs['ram']:
            value = kwargs['ram'][kwargs['index']]
            kwargs['ram'][kwargs['index']] = 0.5*value - 0.1

class Up:

    def __call__(self, **kwargs):
        if kwargs['index'] not in kwargs['ram']:
            kwargs['ram'][kwargs['index']] = 1
        else:
            value = kwargs['ram'][kwargs['index']]
            kwargs['ram'][kwargs['index']] = 0.5*value + 1

class MakeBleaching:

    def __call__(self, discriminatorsoutput):
        for key in discriminatorsoutput:
            ramsoutput = discriminatorsoutput[key][0]
            discriminatorsoutput[key][1] = sum(ramsoutput)
        return discriminatorsoutput

def get_x(total, scale):
    x = []
    turns = sum(total)

    for t in total:
        filled = 0 if turns == 0 else ((float(t)/turns) * scale)
        for i in range(scale):
            x.append(1 if filled > i else 0)

    return x

if input == "":
    turn = 0
    total = [0,0,0]
    history = []

    # hyperparameters
    doubt_value = 0.3
    history_size = 25
    thermometer_scale = 10
    min_random_turns = 0
    final_random_turns = 0
    address_size=8
    # ****************

    count = 0

    wisard = WiSARD(addressSize=address_size,sizeOfEntry=3*thermometer_scale,verbose=False,seed=42,decay=Decay(),up=Up())

    char2num = {"R":0, "P":1, "S":2}
    num2char = {0:"R", 1:"P", 2:"S"}
    defeated_by = {"R":"P", "P":"S", "S":"R"}

    output = random.choice(["R","P","S"])

elif turn < min_random_turns or turn > 1000 - final_random_turns:
    output = random.choice(["R","P","S"])
    total[char2num[input]] += 1
    history.append(char2num[input])
else:
    # using thermometer method to Binarize input
    x = get_x(total, thermometer_scale)
    # training
    wisard.train([x], [input])

    total[char2num[input]] += 1
    history.append(char2num[input])

    new_x = get_x(total, thermometer_scale)

    # classifying
    result = wisard.classifyEntry(new_x)
    output = defeated_by[result[0][0]]

    if(turn % 10 == 0 or result[0][1] < doubt_value):
        count += 1
        output = random.choice(["R","P","S"])

if(len(history) > history_size):
    total[history[0]] -= 0 if total[history[0]] == 0 else 1
    history.pop(0)

last_prediction = output
turn += 1