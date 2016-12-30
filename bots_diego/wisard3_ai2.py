import random

class RAM3:
  
  def __init__(self, pattern_decay, time_decay, bit_depth, positions):
    # print "Criando ram com pattern_decay=%f time_decay=%f bit_depth=%d positions=%s" % (pattern_decay, time_decay, bit_depth, positions)
    self.pattern_decay = pattern_decay
    self.time_decay = time_decay
    self.bit_depth = bit_depth
    self.positions = positions
    self.memory = [0] * bit_depth**len(self.positions)
    self.timestamps = [0] * bit_depth**len(self.positions)
    self.current_time = 0
  
  def predict(self, signature):
    index = self.extract_memory_position(signature)
    return self.memory[index]
  
  def train(self, signature, energy):
    self.current_time += 1
    index = self.extract_memory_position(signature)
    age = self.current_time - self.timestamps[index]
    self.memory[index] = energy + self.pattern_decay * self.time_decay ** age * self.memory[index]
  
  def extract_memory_position(self, signature):
    ram_signature = [0] * len(self.positions)
    for i in xrange(0,len(self.positions)):
      ram_signature[i] = signature[self.positions[i]]
    ram_signature.reverse()
    
    index = 0
    for i in xrange(0,len(ram_signature)):
      index += self.bit_depth ** i * ram_signature[i]
    
    return index

class DISCRIMINANT3:
  
  def __init__(self, bits, pattern_decay, time_decay, signature_size, bit_depth):
    self.rams = []
    rams = int(signature_size / bits)
    
    # print "Criando %d rams" % rams
    for i in xrange(0,rams):
      positions = [i for i in xrange(i*bits, (i+1)*bits)]
      self.rams.append(RAM3(pattern_decay, time_decay, bit_depth, positions))
    # print
  
  def predict(self, signature):
    energy = 0
    
    for r in self.rams:
      energy += r.predict(signature)
    
    return energy
  
  def train(self, signature, energy):
    for r in self.rams:
      r.train(signature, energy)

# Uma variante da rede WISARD com decaimento do conhecimento conforme novas 
# informacoes sao coletadas
class WISARD3:
  
  # discriminants: Classes de saida distintas
  # bits: Bits de entrada em cada ram
  # decay: Taxa de decaimento do conhecimento antigo a cada novo conhecimento que chega
  # signature_size: Tamanho do padrao de entrada
  # bit_depth: Numero de estados que um bit do padrao pode assumir
  def __init__(self, discriminants, bits, pattern_decay, time_decay, signature_size, bit_depth):
    self.discriminants = []
    
    # print "Criando %d discriminantes" % discriminants
    for i in xrange(0,discriminants):
      self.discriminants.append(DISCRIMINANT3(bits, pattern_decay, time_decay, signature_size, bit_depth))
  
  # Retorna qual a classe esperada dado um padrao de entrada (signature)
  def predict(self, signature):
    max = -1
    # print "Making prediction --"
    for i in xrange(0,len(self.discriminants)):
      energy = self.discriminants[i].predict(signature)
      # print "Discriminant %d returned %f" % (i, energy)
      if energy > max or max == -1:
        max = energy
        result = i
    
    return result
  
  # Treina a rede para responder com determinado discriminante (classificacao)
  # dado um exemplo de entrada(signature)
  def train(self, signature, discriminant):
    for i in xrange(0,len(self.discriminants)):
      self.discriminants[i].train(signature, 1 if i == discriminant else 0)

if input == "":
  history = []
  correctly_predictions = []
  ai = WISARD3(3, 2, 0.45, 0.99, 8, 3)
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