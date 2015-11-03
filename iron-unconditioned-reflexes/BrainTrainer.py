from NeuralNetwork.NeuralNetwork import NeuralNetwork


global cbrain
cbrain = None

def get_new_brain(sensor_count):
    global cbrain
    if cbrain is None:
        brain = NeuralNetwork([sensor_count, 2, 2])
        database = []

        for line in open('memory.txt','r'):
            line = [float(x) for x in line.split()]
            database.append((line[:-2], line[-2:]))

        for _ in range(15):
            err = brain.teach_by_sample(database)
            print(err)
        cbrain = brain
    return cbrain



def algorythm(sensors):
    forward = 1.0 - (sum(sensors) / len(sensors))
    half_len = len(sensors) / 2
    l = sum(sensors[:half_len])/half_len
    r = sum(sensors[half_len:])/half_len
    if l==0 and r==0:
        l=0.005
    rotate = (l-r)*2.0
    return forward, rotate
