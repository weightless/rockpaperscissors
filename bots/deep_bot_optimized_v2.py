import random
import math
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
        self.makeBleaching = makeBleaching

        if sizeOfEntry is not None:
            for aclass in classes:
                self.discriminators[aclass] = Discriminator(
                    aclass, sizeOfEntry, self.addressSize,
                    self.addressing, self.numberOfRAMS, decay=self.decay, up=self.up)

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
        return max(discriminatorsoutput, key=lambda x: discriminatorsoutput[x][1])


    def classify(self, entries):
        output=[]
        for i,entry in enumerate(entries):
            aclass = self.classifyEntry(entry)[0][0]
            output.append((entry, aclass))
        return output

    def decayRate(self, value):
        if self.decay is not None:
            self.decay.rate = value

    def upRate(self, value):
        if self.up is not None:
            self.up.rate = value

basefunc = lambda x: 1.0/(math.exp(-x)+1.0)

class Decay:
    rate = 0.63

    def __call__(self, **kwargs):
        if kwargs['index'] in kwargs['ram']:
            x = kwargs['ram'][kwargs['index']]
            kwargs['ram'][kwargs['index']] = self.rate*x-0.243

class Up:
    rate = 0.4

    def __call__(self, **kwargs):
        if kwargs['index'] not in kwargs['ram']:
            kwargs['ram'][kwargs['index']] = 1
        else:
            x = kwargs['ram'][kwargs['index']]
            kwargs['ram'][kwargs['index']] = self.rate*x+1

class MakeBleaching:

    def __call__(self, discriminatorsoutput):
        for key in discriminatorsoutput:
            ramsoutput = discriminatorsoutput[key][0]
            discriminatorsoutput[key][1] = sum(map(basefunc,ramsoutput))
        return discriminatorsoutput


if input == "":
    history = []
    correctly_predictions = []
    ai = WiSARD(4, classes=['R','P','S'], sizeOfEntry=16, decay=Decay(), up=Up(), makeBleaching=MakeBleaching())
    char2num = {"R":0, "P":1, "S":2}
    num2char = {0:"R", 1:"P", 2:"S"}
    defeat = {"R":"P", "P":"S", "S":"R"}
    output = random.choice(["R","P","S"])
    prediction = output

elif len(history) < 16:
    output = random.choice(["R","P","S"])
    prediction = output
    history.append(char2num[last])
    history.append(char2num[input])
    correctly_predictions.append(1 if last_prediction == input else 0)

else:
    correctly_predictions.append(1 if last_prediction == input else 0)
    if len(correctly_predictions) > 50: correctly_predictions.pop(0)

    ai.train([history], [input])

    history.append(char2num[last])
    history.append(char2num[input])
    history.pop(0)
    history.pop(0)

    prediction = ai.classify([history])[0][1]

    if sum(correctly_predictions) > 35:
        blefe_rate = 0
    elif sum(correctly_predictions) > 25:
        blefe_rate = 0.3
    else:
        blefe_rate = 0.45

    if random.random() < blefe_rate: output = prediction
    else: output = defeat[prediction]

last = output
last_prediction = prediction
