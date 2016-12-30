import random


class RAM:
  
  def __init__(self, discriminants, pattern_decay, time_decay, bit_depth, positions, initial_value):
    self.discriminants = discriminants
    self.pattern_decay = pattern_decay
    self.time_decay = time_decay
    self.bit_depth = bit_depth
    self.positions = positions
    self.memory = [0] * (discriminants * bit_depth**len(self.positions))
    self.timestamps = [0] * bit_depth**len(self.positions)
    
    for i in xrange(0, bit_depth**len(self.positions)):
      for j in xrange(0, discriminants):
        self.memory[i*discriminants+j] = initial_value[j]
  
  def predict(self, current_time, signature, answers):
    self.predict2(current_time, signature, answers, 0, 0, 1)
  
  def predict2(self, current_time, signature, answers, sig_index, index, energy):
    
    if sig_index == len(self.positions):
      age = current_time - self.timestamps[index]
      for i in xrange(0, self.discriminants):
        answers[i] += self.memory[index*self.discriminants + i] * (self.time_decay ** age) * energy
    
    elif signature[self.positions[sig_index]] == self.bit_depth:
      energy = energy / self.bit_depth
      for i in xrange(0, self.bit_depth):
        new_index = index * self.bit_depth + i
        self.predict2(current_time, signature, answers, sig_index+1, new_index, energy)
    
    else:
      new_index = index * self.bit_depth + signature[self.positions[sig_index]]
      self.predict2(current_time, signature, answers, sig_index+1, new_index, energy)
  
  def train(self, current_time, signature, answers):
    self.train2(current_time, signature, answers, 0, 0, 1.0)
  
  def train2(self, current_time, signature, answers, sig_index, index, energy):
    
    if sig_index == len(self.positions):
      age = current_time - self.timestamps[index]
      
      for i in xrange(0,self.discriminants):
        old_value = self.memory[index*self.discriminants+i]
        new_value = answers[i] + self.pattern_decay * (self.time_decay ** age) * old_value
        self.memory[index*self.discriminants+i] = (new_value) * (energy) + (old_value) * (1-energy)
      
      self.timestamps[index] = (current_time) * (energy) + (self.timestamps[index]) * (1-energy)
    
    elif signature[self.positions[sig_index]] == self.bit_depth:
      energy /= self.bit_depth
      for i in xrange(0,self.bit_depth):
        new_index = index * self.bit_depth + i
        self.train2(current_time, signature, answers, sig_index+1, new_index, energy)
    
    else:
      new_index = index * self.bit_depth + signature[self.positions[sig_index]]
      self.train2(current_time, signature, answers, sig_index+1, new_index, energy)


class WISARD:
  
  def __init__(self, discriminants, bits, pattern_decay, time_decay, signature_size, bit_depth, default_answer = -1):
    self.rams = []
    self.current_time = 0
    self.answers = [0] * discriminants
    self.discriminants = discriminants
    rams = int(signature_size / bits)
    
    if default_answer == -1:
      for i in xrange(0, discriminants):
        self.answers[i] = 0
    else:
      for i in xrange(0, discriminants):
        self.answers[i] = 1 if default_answer == i else -1
    
    for i in xrange(0,rams):
      positions = [i for i in xrange(i*bits, (i+1)*bits)]
      self.rams.append(RAM(discriminants, pattern_decay, time_decay, bit_depth, positions, self.answers))
  
  def predict(self, signature):
    for i in xrange(0,self.discriminants):
      self.answers[i] = 0
    
    for r in self.rams:
      r.predict(self.current_time, signature, self.answers)
    
    result = 0
    maximum = -1
    for i in xrange(0,self.discriminants):
      if maximum == -1 or self.answers[i] > maximum:
        maximum = self.answers[i]
        result = i
    
    return result
  
  def train(self, signature, discriminant):
    self.current_time += 1
    
    for i in xrange(0,self.discriminants):
      self.answers[i] = -1
    self.answers[discriminant] = 1
    
    for r in self.rams:
      r.train(self.current_time, signature, self.answers)


if input == "":
  input_length = 8
  
  history = []
  rps = ["R","P","S"]
  correctly_predictions = []
  
  ai1 = WISARD(4, 2, 0, 1, input_length, 3, 3)
  ai2 = WISARD(4, 2, 0, 1, input_length, 3, 3)
  ai3 = WISARD(3, 2, 0.25, 0.97, input_length+2, 3)
  
  char2num = {"R":0, "P":1, "S":2}
  num2char = {0:"R", 1:"P", 2:"S"}
  
  defeat = {"R":"P", "P":"S", "S":"R"}
  
  output = random.choice(rps)
  prediction = output
  
  last_prediction_ai1 = 3
  last_prediction_ai2 = 3
  
elif len(history) < input_length:
  output = random.choice(rps)
  prediction = output
  history.append(char2num[last])
  history.append(char2num[input])
  correctly_predictions.append(1 if last_prediction == input else 0)
  
else:
  correctly_predictions.append(1 if last_prediction == input else 0)
  if len(correctly_predictions) > 50: correctly_predictions.pop(0)
  
  history.append(last_prediction_ai2)
  history.append(last_prediction_ai1)
  
  ai3.train(history, char2num[input])
  
  history.pop()
  history.pop()
  
  ai1.train(history, char2num[input])
  ai2.train(history, char2num[last])
  
  history.pop(0)
  history.pop(0)
  history.append(char2num[last])
  history.append(char2num[input])
  
  last_prediction_ai2 = ai2.predict(history)
  last_prediction_ai1 = ai1.predict(history)
  
  history.append(last_prediction_ai2)
  history.append(last_prediction_ai1)
  
  prediction = num2char[ai3.predict(history)]
  
  history.pop()
  history.pop()
  
  if sum(correctly_predictions) > 35: blefe_rate = 0
  elif sum(correctly_predictions) > 25: blefe_rate = 0.3
  else: blefe_rate = 0.45
  
  if random.random() < blefe_rate: output = prediction
  else: output = defeat[prediction]


last = output
last_prediction = prediction