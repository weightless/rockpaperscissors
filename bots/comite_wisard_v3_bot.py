import random

class Addressing:
    def __call__(self, binCode): # binCode is a list of values of selected points of entry
        index = 0
        for i,e in enumerate(binCode):
            if e > 0:
                index += e * pow(3,i)
        return index

class RAM:

    def __init__(self, addressSize, entrySize, addressing):
        self.addressing = addressing
        self.ram = {}
        self.address = [ random.randint(0, entrySize-1) for x in range(addressSize) ]

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

    def train(self, entry):
        index = self._addressToIndex(entry)
        self._acumulateRam(index)

    def classify(self, entry):
        index = self._addressToIndex(entry)
        return self._getValue(index)

class Discriminator:

    def __init__(self, name, entrySize, addressSize, addressing, numberOfRAMS=None):
        if numberOfRAMS is None:
            numberOfRAMS = int(entrySize/addressSize)
        self.rams = [ RAM(addressSize, entrySize, addressing) for x in range(numberOfRAMS) ]

    def train(self, entry):
        for ram in self.rams:
            ram.train(entry)

    def classify(self, entry):
        return [ ram.classify(entry) for ram in self.rams ]

class WiSARD:

    def __init__(self,
            addressSize = 3,
            numberOfRAMS = None,
            bleachingActivated = True,
            seed = random.randint(0, 1000000),
            verbose = True,
            addressing=Addressing()):

        self.seed = seed
        self.verbose = verbose
        random.seed(seed)

        if addressSize < 3:
            self.addressSize = 3
        else:
            self.addressSize = addressSize
        self.numberOfRAMS = numberOfRAMS
        self.discriminators = {}
        self.bleachingActivated = bleachingActivated
        self.addressing = addressing

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

            if self.verbose:
                print("\rtraining "+str(i+1)+" of "+str(len(entries)))

            aclass = str(classes[i])
            if aclass not in self.discriminators:
                self.discriminators[aclass] = Discriminator(aclass, sizeOfEntry, self.addressSize, self.addressing, self.numberOfRAMS)

            self.discriminators[aclass].train(entry)
        if self.verbose:
            print("\r")

    def classifyEntry(self, entry):
        discriminatorsoutput = {}
        for keyClass in self.discriminators:
            discriminatorsoutput[keyClass] = [self.discriminators[keyClass].classify(entry),0]

        discriminatorsoutput = self._makeBleaching(discriminatorsoutput)

        calc = lambda key: (key, float(discriminatorsoutput[key][1])/len(discriminatorsoutput[key][0]))
        classes = list(map(calc,discriminatorsoutput))
        classes.sort(key=lambda x: x[1], reverse=True)

        return classes


    def classify(self, entries):
        output=[]
        for i,entry in enumerate(entries):
            if self.verbose:
                print("\rclassifying "+str(i+1)+" of "+str(len(entries)))

            aclass = self.classifyEntry(entry)[0][0]
            output.append((entry, aclass))

        if self.verbose:
            print("\r")
        return output



if input == "":
    count = -1
    history = []
    correctly_predictions = {}
    last_prediction = {}
    prediction = {}
    memorizes = [15, 20, 30, 50]
    max_win_memorize=50
    win = 0
    losses = 0
    draw = 0
    win_net = {}
    losses_net = {}
    draw_net = {}

    net_wisard = {}

    for m in memorizes:
        net_wisard[m] = WiSARD(addressSize=5,verbose=False)
        correctly_predictions[m] = []
        win_net[m] = 0
        draw_net[m] = 0
        losses_net[m] = 0

    char2num = {"R":0, "P":1, "S":2}
    num2char = {0:"R", 1:"P", 2:"S"}
    defeated_by = {"R":"P", "P":"S", "S":"R"}

    output = random.choice(["R","P","S"])
    prediction[memorizes[0]] = output

elif len(history) < memorizes[0] or count < 100:
    output = random.choice(["R","P","S"])
    prediction[memorizes[0]] = output
    history.append(char2num[last])
    history.append(char2num[input])
    correctly_predictions[memorizes[0]].append(1 if last_prediction == input else 0)
else:
    # training
    for m in memorizes:
        if(len(history) < m):
            continue

        if(m in last_prediction):
            correctly_predictions[m].append(1 if last_prediction[m] == input else 0)

        if len(correctly_predictions[m]) > max_win_memorize: correctly_predictions[m].pop(0)

        net_wisard[m].train([history[len(history)-m:len(history)]], [char2num[input]])

    # updating history
    history.append(char2num[last])
    history.append(char2num[input])
    prediction = {}

    # classifying
    for m in memorizes:
        if(len(history) < m):
            continue

        result = net_wisard[m].classifyEntry(history[len(history)-m:len(history)])
        max_value = 0.0
        for r in result:
            if(r[1] >= max_value):
                prediction[m] = int(r[0])
                max_value = r[1]


    # updating history
    if(len(history) > memorizes[len(memorizes)-1]):
        history.pop(0)
        history.pop(0)

    # voting
    vote = [0,0,0]
    for p in prediction:
        vote[prediction[p]] += 1


    max_vote = 0
    for i,v in enumerate(vote):
        if(v > max_vote):
            max_vote = v
            output = num2char[i]

    if(count%10 == 0):
        output = random.choice(["R","S","P"])

    output = defeated_by[output]

    if(last == input):
        win += 1
    elif(last == defeated_by[input]):
        losses += 1
    else:
        draw += 1

    # for m in memorizes:
    #     if(last_prediction[m] == defeated_by[input]):
    #         win_net[m] += 1

    # if(count%200 == 0):
    #     print(str((win)) + "/" + str((losses)) + " de " + str(count))

last = output
last_prediction = prediction
count += 1
