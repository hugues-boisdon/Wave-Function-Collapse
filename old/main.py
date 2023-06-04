import wfc

INPUT_FOLDER   = './inputs/'
PATTERNS_FOLDER = './patterns/'
OUTPUT_FOLDER  = './outputs/'

model = wfc.Model()
model.set(path=INPUT_FOLDER+'001.png', N=3)
model.savePatterns(PATTERNS_FOLDER)

model.generate()
