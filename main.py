import wfc

w = wfc.WFC_IMG()
w.fit("pattern.png")

m = w.execute((10,10))


