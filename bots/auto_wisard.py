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
                index += e*pow(3,i)
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


if input == "":
    count = -1
    history = []
    prediction = {}
    history_sizes = [5, 16, 30]
    wisards = {}
    wisard_hits = {}
    min_random_turns = 10

    for hs in history_sizes:
        wisards[hs] = WiSARD(addressSize=5,sizeOfEntry=hs,verbose=False,decay=Decay(),up=Up())
        wisard_hits[hs] = []

    char2num = {"R":0, "P":1, "S":2}
    num2char = {0:"R", 1:"P", 2:"S"}
    defeated_by = {"R":"P", "P":"S", "S":"R"}

    output = random.choice(["R","P","S"])

elif len(history) < history_sizes[0] or count < min_random_turns:
    output = random.choice(["R","P","S"])
    history.append(char2num[input])
else:
    # training
    for hs in history_sizes:
        if(len(history) < hs):
            continue

        hs_history = history[len(history)-hs:len(history)]
        wisards[hs].train([hs_history], [char2num[input]])

    # updating history
    history.append(char2num[input])
    prediction = {}

    # classifying
    for hs in history_sizes:
        if(len(history) < hs):
            continue

        hs_history = history[len(history)-hs:len(history)]
        result = wisards[hs].classifyEntry(hs_history)
        max_value = 0.0
        for r in result:
            if(r[1] >= max_value):
                prediction[hs] = int(r[0])
                max_value = r[1]

        if(hs in last_prediction):
            wisard_hits[hs].append(1 if last_prediction[hs] == input else 0)

    # updating history
    if(len(history) > history_sizes[len(history_sizes)-1]):
        history.pop(0)

    best_sum = 0
    # choosing the actual best wisard
    for hs in history_sizes:
        if(hs not in prediction):
            continue
        if(sum(wisard_hits[hs]) >= best_sum):
            best_sum = sum(wisard_hits[hs])
            output = defeated_by[num2char[prediction[hs]]]

    if(count % 10 == 0):
        output = random.choice(["R","P","S"])


last_prediction = prediction
count += 1