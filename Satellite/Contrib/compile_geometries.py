'''
Created on 18 Sep 2019

@author: Tyler

Read all the geometries files for each tile into a data structure that can be saved, loaded, and searched
'''


import sentinel.geometry_list as geometry_list

gl = geometry_list("geometries")

print("Printing geometries")
gl.listGeometries()

print("Finished!")