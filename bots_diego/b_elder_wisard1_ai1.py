import random

class RAM:
  
  def __init__(self, oblivion_rate, bit_depth, positions):
    self.oblivion_rate = oblivion_rate
    self.bit_depth = bit_depth
    self.positions = positions
    self.memory = [0] * bit_depth**len(self.positions)
  
  def predict(self, signature, current_time):
    index = self.extract_memory_position(signature)
    return self.memory[index]*(self.oblivion_rate**current_time)
  
  def train(self, signature, current_time, energy):
    index = self.extract_memory_position(signature)
    self.memory[index] = (energy + self.memory[index])*(self.oblivion_rate**current_time)
  
  def extract_memory_position(self, signature):
    ram_signature = [0] * len(self.positions)
    for i in xrange(0,len(self.positions)):
      ram_signature[i] = signature[self.positions[i]]
    ram_signature.reverse()
    
    index = 0
    for i in xrange(0,len(ram_signature)):
      index += self.bit_depth ** i * ram_signature[i]
    
    return index

class DISCRIMINANT:
  
  def __init__(self, bits, oblivion_rate, signature_size, bit_depth):
    self.rams = []
    rams = int(signature_size / bits)
    
    for i in xrange(0,rams):
      positions = [i for i in xrange(i*bits, (i+1)*bits)]
      self.rams.append(RAM(oblivion_rate, bit_depth, positions))
  
  def predict(self, signature, current_time):
    energy = 0
    
    for r in self.rams:
      energy += r.predict(signature, current_time)
    
    return energy
  
  def train(self, signature, current_time, energy):
    for r in self.rams:
      r.train(signature, current_time, energy)

class WISARD:
  
  def __init__(self, discriminants, bits, oblivion_rate, signature_size, bit_depth):
    self.discriminants = []
    self.current_time = 0
    
    for i in xrange(0,discriminants):
      self.discriminants.append(DISCRIMINANT(bits, oblivion_rate, signature_size, bit_depth))
  
  def predict(self, signature):
    max = -1
    for i in xrange(0,len(self.discriminants)):
      energy = self.discriminants[i].predict(signature, self.current_time)
      if energy > max or max == -1:
        max = energy
        result = i
    
    return result
  
  def train(self, signature, discriminant):
    self.current_time += 1
    for i in xrange(0,len(self.discriminants)):
      self.discriminants[i].train(signature, self.current_time, 1 if i == discriminant else -1)

if input == "":
  history = []
  correctly_predictions = []
  ai = WISARD(3, 2, 0.97, 8, 3)
  char2num = {"R":0, "P":1, "S":2}
  num2char = {0:"R", 1:"P", 2:"S"}
  defeat = {"R":"P", "P":"S", "S":"R"}
  output = random.choice(["R","P","S"])
  prediction = output
elif len(history) < 8:
  output = random.choice(["R","P","S"])
  prediction = output
  history.append(char2num[last])
  history.append(char2num[input])
  correctly_predictions.append(1 if last_prediction == input else 0)
else:
  correctly_predictions.append(1 if last_prediction == input else 0)
  if len(correctly_predictions) > 50: correctly_predictions.pop(0)
  
  ai.train(history, char2num[input])
  
  history.append(char2num[last])
  history.append(char2num[input])
  history.pop(0)
  history.pop(0)
  
  prediction = num2char[ai.predict(history)]
  
  if sum(correctly_predictions) > 35: blefe_rate = 0
  elif sum(correctly_predictions) > 25: blefe_rate = 0.3
  else: blefe_rate = 0.45
  
  if random.random() < blefe_rate: output = prediction
  else: output = defeat[prediction]

last = output
last_prediction = prediction