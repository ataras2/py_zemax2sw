# -*- coding: utf-8 -*-
"""
Created on Fri Sep  2 16:35:26 2022

@author: Adam
"""

from Prescription_Reader import Prescription_Reader
from Prescription_Writer import Prescription_Writer

import numpy as np

class Prescription2swTxt:
    """ 
        'Fine, I'll do it myself'
        
        A python interface to run the workflow 
        
        Zemax (prescription data) -> txt -> AT_ZOS -> txt -> Solidworks
    """
    
    def __init__(self, in_fnames, out_fname, **kwargs):        
        self.readers = []
        for i in range(len(in_fnames)):
            self.readers.append(Prescription_Reader(in_fnames[i], config=i+1)) 
        
        self.writer = Prescription_Writer(out_fname)

        self.all_surfs = self.filter_surfs(**kwargs)

    def filter_surfs(self, filter_names = None, manual_surfs = None):
        all_surfs = []
        for reader in self.readers:
            for surf in reader.objs:
                if filter_names is None:
                    all_surfs.append(surf)
                elif surf.name is not None:
                    if surf.name in filter_names:
                        all_surfs.append(surf)

        if manual_surfs is not None:
            assert len(manual_surfs) > 0
            for surf in manual_surfs:
                all_surfs.append(surf)

        # sort by surface index
        all_surfs.sort(key = lambda x: int(x.surf_idx))
        return all_surfs

    def transform_surfs(self, R=np.eye(3), T=np.zeros(3), surf_subset=[], exclude=[]):
        """
            apply transforms to all of the surfaces

            inputs
                R: rotation matrix
                T: translation vector
                surf_subset: a list of names of the surfaces to be transformed
                exclude: a list of names of surfaces to exclude

            output
                None
        """
        if surf_subset != [] and exclude != []:
            raise ValueError("Cannot take both a surface subset and exclusion")
        elif surf_subset != [] or exclude != []:
            use_name = True
        else:
            use_name = False

        # deal with input into a single list
        if surf_subset != []:
            surfs_to_transform = [x for x in self.all_surfs if x.name in surf_subset]
        elif exclude != []:
            surfs_to_transform = [x for x in self.all_surfs if x.name not in exclude]


        if use_name:
            for surf in surfs_to_transform:
                surf.apply_transform(R,T)
        else:
            for surf in self.all_surfs:
                surf.apply_transform(R,T)

    def write_out(self, **kwargs):
        self.writer.write_sw_txt(self.all_surfs, **kwargs)

if __name__ == "__main__":
    
    in_fnames = [
            "data/coords_small_c1.txt",
            "data/coords_small_c2.txt"
        ]
    
    import os


    # Check whether the specified path exists or not
    if not os.path.exists('outputs'):
        os.makedirs('outputs')

    out_fname = "outputs/coords_small_sw.txt"
    
    
    zos = Prescription2swTxt(in_fnames, out_fname)
    
    T = np.array([-510,200,150])
    
    R = np.array([[0, 0, 1],
                  [0, 1, 0],
                  [-1, 0, 0]])
    
    zos.transform_surfs(T=T, R=R)
    zos.write_out(key_subset="xyzAng")
    