
if input == "":

    import random
    import math
    from random import randint

    class CompactedRAM:

        def __init__(self):
            self.ram = {}

        def __contains__(self, index):
            return index in self.ram

        def __getitem__(self, index):
            if index in self.ram:
                return self.ram[index]
            return 0

        def __setitem__(self, index, item):
            if item == 0:
                del self.ram[index]
            else:
                self.ram[index] = item

    class AddressControl:

        def __init__(self, addressSize, entrySize, addressing):
            self.addressing = addressing
            self.address = [ randint(0, entrySize-1) for x in range(addressSize) ]

        def __getitem__(self, entry):
            binCode = []
            for i in self.address:
                binCode.append(entry[i])
            return self.addressing(binCode)

    class RAM:

        def __init__(self, addressSize, entrySize, controls):
            self.controls = controls
            self.ram = CompactedRAM()
            self.address = AddressControl(addressSize, entrySize, controls.addressing)

        def train(self, entry, negative=False):
            index = self.address[entry]
            if not negative:
                self.controls.increase(entry=entry, ram=self.ram, address=self.address, index=index)
            else:
                self.controls.decay(entry=entry, ram=self.ram, address=self.address, index=index)

        def classify(self, entry):
            index = self.address[entry]
            return self.ram[index]

    class Discriminator:

        def __init__(self, name, entrySize, addressSize, ramcontrols, numberOfRAMS=None):
            self.name = name
            if numberOfRAMS is None:
                numberOfRAMS = int(entrySize/addressSize)
            self.rams = [ RAM(addressSize, entrySize, ramcontrols) for x in range(numberOfRAMS) ]

        def train(self, entry, negative=False):
            for ram in self.rams:
                ram.train(entry, negative)

        def classify(self, entry):
            return [ ram.classify(entry) for ram in self.rams ]

    class DeepDiscriminator:

        def __init__(self, name, entrySize, addressSize, ramcontrols, numberOfDiscriminators=10, numberOfRAMS=None):
            self.name = name
            self.discriminators = []
            for x in xrange(0,numberOfDiscriminators):
                discriminator = Discriminator(name, entrySize, addressSize, ramcontrols, numberOfRAMS)
                self.discriminators.append(discriminator)

        def train(self, entry, negative=False):
            for discriminator in self.discriminators:
                discriminator.train(entry, negative)

        def classify(self, entry):
            return [ d.classify(entry) for d in self.discriminators ]


    class BinarizationAverage:

        def __init__(self, base=2):
            self.base=base-1

        def code(self, x, mean, dp):
            if dp == 0:
                dp = 1
            out = (((x - mean)/dp) + 1.0)/2.0
            if out > 1:
                return self.base
            else:
                return round(self.base*out)

        def __call__(self, entry):
            average = float(sum(entry))/len(entry)
            dp = 0
            for x in entry:
                dp += math.pow(x - average, 2)
            dp = math.sqrt(dp/len(entry))

            for i in xrange(len(entry)):
                entry[i] = self.code(entry[i], average, dp)
            return entry

    class ConnectLayersBase:

        def __init__(self, bin=BinarizationAverage()):
            self.bin = bin

        def join(self, matrix):
            out = []
            for line in matrix:
                for element in line:
                    out.append(element)
            return out

        def training(self, featureVector):
            return self.transform(featureVector)

        def classifying(self, entry):
            output = {}
            for aclass in entry:
                output[aclass] = self.transform(entry[aclass])
            return output

        def transform(self, featureVector):
            pass

    class ConnectLayersDefault(ConnectLayersBase):

        def transform(self, featureVector):
            return self.bin(self.join(featureVector))

    class BaseLayer:

        def __init__(self, deep=None, connectLayers=None):
            if isinstance(deep, BaseLayer):
                self.deep = deep
            else:
                self.deep = None

            if isinstance(connectLayers, ConnectLayersBase):
                self.connectLayers = connectLayers
            else:
                self.connectLayers = None

        def train(self, entry, aclass):
            if self.deep is not None and self.connectLayers is not None:
                self.deep.train(entry, aclass)
                featureVector = self.deep.classify(entry, aclass)
                entry = self.connectLayers.training(featureVector)
            self._train(entry, aclass)

        def classify(self, entry, aclass=None): # if aclass is not None then is the fase of trainning otherwise is the fase of classification
            if aclass is None:
                if self.deep is not None and self.connectLayers is not None:
                    featuresVectors = self.deep.classify(entry)
                    entry = self.connectLayers.classifying(featuresVectors)
                return self._classify(entry)
            else:
                return self._classifyTrain(entry, aclass)

        def _train(self, entry, aclass):
            pass

        def _classifyTrain(self, entry, aclass):
            pass

        def _classify(self, entry):
            pass

    class LayerClassWisard(BaseLayer):

        def __init__(self,
                addressSize = 3,
                numberOfRAMS = None,
                sizeOfEntry = None,
                classes = [],
                numberOfDiscriminators = 10, # number of discriminators for each class
                seed = random.randint(0, 1000000),
                ramcontrols = None,
                deep = None,
                connectLayers = ConnectLayersDefault()):

            BaseLayer.__init__(self, deep=deep, connectLayers=connectLayers)

            self.seed = seed
            random.seed(seed)

            if addressSize < 3:
                self.addressSize = 3
            else:
                self.addressSize = addressSize

            self.numberOfRAMS = numberOfRAMS
            self.discriminators = {}
            self.numberOfDiscriminators = numberOfDiscriminators

            self.ramcontrols = ramcontrols

            if sizeOfEntry is not None:
                for aclass in classes:
                    self._createDiscriminator(aclass, sizeOfEntry)

        def _createDiscriminator(self, aclass, sizeOfEntry):
            self.discriminators[str(aclass)] = DeepDiscriminator(
                str(aclass), sizeOfEntry, self.addressSize,
                self.ramcontrols, self.numberOfDiscriminators, self.numberOfRAMS)

        def _train(self, entry, aclass):
            if aclass not in self.discriminators:
                self._createDiscriminator(aclass, len(entry))
            self.discriminators[aclass].train(entry)
            if self.ramcontrols.decayActivated:
                for key in self.discriminators:
                    if key != aclass:
                        self.discriminators[key].train(entry, negative=True)

        def _classifyTrain(self, entry, aclass):
            return self.discriminators[aclass].classify(entry)

        def _classify(self, entry):
            out = {}
            for key in self.discriminators:
                if isinstance(entry, dict):
                    out[key] = self.discriminators[key].classify(entry[key])
                else:
                    out[key] = self.discriminators[key].classify(entry)

            return out

    class Wisard(BaseLayer):

        def __init__(self,
                addressSize = 3,
                numberOfRAMS = None,
                bleachingActivated = True,
                sizeOfEntry = None,
                classes = [],
                seed = random.randint(0, 1000000),
                makeBleaching = None,
                ramcontrols = None,
                deep = None,
                connectLayers = ConnectLayersDefault()):

            BaseLayer.__init__(self, deep=deep, connectLayers=connectLayers)

            self.seed = seed
            random.seed(seed)

            self.ramcontrols = ramcontrols
            self.makeBleaching = makeBleaching
            self.discriminators = {}

            if addressSize < 3:
                self.addressSize = 3
            else:
                self.addressSize = addressSize
            self.numberOfRAMS = numberOfRAMS

            if sizeOfEntry is not None:
                for aclass in classes:
                    self._createDiscriminator(aclass, sizeOfEntry)

        def _createDiscriminator(self, aclass, sizeOfEntry):
            self.discriminators[str(aclass)] = Discriminator(
                str(aclass), sizeOfEntry, self.addressSize,
                self.ramcontrols, self.numberOfRAMS)

        def _train(self, entry, aclass):
            if aclass not in self.discriminators:
                self._createDiscriminator(aclass, len(entry))
            self.discriminators[aclass].train(entry)
            if self.ramcontrols.decayActivated:
                for key in self.discriminators:
                    if key != aclass:
                        self.discriminators[key].train(entry, negative=True)

        def getDiscriminatorsOutput(self, entry):
            discriminatorsoutput = {}
            if isinstance(entry,dict):
                for keyClass in entry:
                    discriminatorsoutput[keyClass] = [self.discriminators[keyClass].classify(entry[keyClass]),0]
            else:
                for keyClass in self.discriminators:
                    discriminatorsoutput[keyClass] = [self.discriminators[keyClass].classify(entry),0]
            return discriminatorsoutput


        def _classify(self, entry):
            discriminatorsoutput = self.getDiscriminatorsOutput(entry)
            discriminatorsoutput = self.makeBleaching(discriminatorsoutput)
            classe = max(discriminatorsoutput, key=lambda x: discriminatorsoutput[x][1])
            return classe



    class RAMControls:

        def __init__(self, base=2, decayActivated=True, alfa=lambda x: x + 1.0, beta=lambda x: x*0.1):
            self.decayActivated = decayActivated
            self.base = base
            self.alfa = alfa
            self.beta = beta

        def addressing(self, binCode):
            index = 0
            for i,e in enumerate(binCode):
                if e < self.base:
                    index += e*pow(self.base,i)
                else:
                    index += (self.base-1)*pow(self.base,i)
            return index

        def increase(self, **kwargs):
            index = kwargs['index']
            ram = kwargs['ram']
            value = ram[index]
            ram[index] = self.alfa(value)

        def decay(self, **kwargs):
            index = kwargs['index']
            ram = kwargs['ram']
            if index in ram:
                value = ram[index]
                ram[index] = self.beta(value)

    class MakeBleachingSum:

        def __call__(self, discriminatorsoutput):
            for key in discriminatorsoutput:
                ramsoutput = discriminatorsoutput[key][0]
                discriminatorsoutput[key][1] = sum(ramsoutput)
            return discriminatorsoutput


    # AI instantiation
    nd = 1
    ad = 4
    se = 16
    alfa1 = lambda x: abs(1.0/(math.exp(-x)+1)) + 1
    beta1 = lambda x: -abs(1.0/(math.exp(-x)+1))
    l1 = LayerClassWisard(ad, classes=['R','P','S'], sizeOfEntry=se, ramcontrols=RAMControls(base=3, alfa=alfa1, beta=beta1), numberOfDiscriminators=nd)

    sizeOfEntry = nd * (se/ad)
    ad2 = int(math.sqrt(sizeOfEntry))
    alfa2 = lambda x: abs(math.tanh(x)) + 1
    beta2 = lambda x: -abs(math.tanh(x))
    base = 7
    connect = ConnectLayersDefault(bin=BinarizationAverage(base=base))
    ai = Wisard(ad2, classes=['R','P','S'], sizeOfEntry=sizeOfEntry, ramcontrols=RAMControls(base=base, alfa=alfa2, beta=beta2), makeBleaching=MakeBleachingSum(), deep=l1, connectLayers=connect)

    history = []
    correctly_predictions = []
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

    ai.train(history, input)

    history.append(char2num[last])
    history.append(char2num[input])
    history.pop(0)
    history.pop(0)

    prediction = ai.classify(history)

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
