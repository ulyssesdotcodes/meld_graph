#ico class
import os
import numpy as np
import nibabel as nb
import copy
import time
from scipy import sparse 
import meld_classifier.mesh_tools as mt
import torch
from math import pi 




#loads in all icosphere
class IcoSpheres():
    """Class to define cohort-level parameters such as subject ids, mesh"""
    def __init__(self, icosphere_path='../data/icospheres/'):
        """icosphere class
        icospheres at each level are stored in self.icospheres[1:7]
        autoloads & calculates:
        'coords': spherical coordinates
        'faces': triangle faces
        'polar_coords': theta & phi spherical coords
        'edges': all edges
        'adj_mat': sparse adjacency matrix"""
        self.icosphere_path = icosphere_path
        self.icospheres={}
        self.load_all_levels()
        
        
    def load_all_levels(self):
        for level in np.arange(7)+1:
            print(level)
            self.load_one_level(level=level)
            
        return
    
    def load_one_level(self,level=7):
        self.load_icosphere(level = level)
        self.calculate_neighbours(level = level)
        self.spherical_coords(level = level)
        t1=time.time()
        self.get_exact_edge_attrs(level=level)
        t2=time.time()
        print(t2-t1)
        self.calculate_adj_mat(level=level)
        
        return
        
    def load_icosphere(self,level=7):
        surf_nb = nb.load(os.path.join(self.icosphere_path,f'ico{level}.surf.gii'))
        self.icospheres[level]={'coords':surf_nb.darrays[0].data,
              'faces':surf_nb.darrays[1].data}
        return 
    
    def calculate_adj_mat(self,level=7):
        surf=self.icospheres[level]
        
        surf['adj_mat'] = sparse.coo_matrix(
                (np.ones(len(surf['edges']), np.uint8), (surf['edges'][:, 0], surf['edges'][:, 1])),
                shape=(len(surf["coords"]), len(surf["coords"])),
            ).tocsr()
        return
    
    def calculate_neighbours(self,level=7):
        file_path = os.path.join(self.icosphere_path,f'ico{level}.neighbours.npy')
        if os.path.isfile(file_path):
            self.icospheres[level]['neighbours'] = np.load(file_path,allow_pickle=True)
        else:            
            self.icospheres[level]['neighbours'] = np.array(self.get_neighbours_from_tris(self.icospheres[level]['faces']),
                                                        dtype=object)
            np.save(file_path,self.icospheres[level]['neighbours'],allow_pickle=True)
        
        return

    def spherical_coords(self,level=7):
        self.icospheres[level]['spherical_coords'] = mt.spherical_np(self.icospheres[level]['coords'])[:,1:]
        self.icospheres[level]['spherical_coords'][:,0] = self.icospheres[level]['spherical_coords'][:,0] - pi/2
        return
    
    def calculate_pseudo_edge_attrs(self,level=7):
        """pseudo edge attributes, difference between latitude and longitude"""
        col = self.icospheres[level]['edges'][:,0]
        row = self.icospheres[level]['edges'][:,1]
        pos = self.icospheres[level]['spherical_coords']
        pseudo = pos[col] - pos[row]
        alpha = pseudo[:,1]
        
        tmp = (alpha == 0).nonzero()[0]
        alpha[tmp] = 1e-15
        tmp = (alpha < 0).nonzero()[0]
        alpha[tmp] = np.pi + alpha[tmp]

        alpha = 2*np.pi + alpha
        alpha = np.remainder(alpha, 2*np.pi)
        pseudo[:,1]=alpha
        
        self.icospheres[level]['pseudo_edge_attr'] = pseudo
        return
    
   
        
    #helper functions
    def get_edges(self,level=7):
        
        return self.icospheres[level]['edges']
    
    def get_edge_vectors(self,level=7,dist_dtype ='exact_edge_attr'):
        if dist_dtype == 'pseudo':
            self.calculate_pseudo_edge_attrs(level = level)
            return self.icospheres[level]['pseudo_edge_attr']
        elif dist_dtype == 'exact':
            return self.icospheres[level]['exact_edge_attr']


    
    def get_neighbours_from_tris(self,tris):
        """Get surface neighbours from tris
        Input: tris
        Returns Nested list. Each list corresponds
        to the ordered neighbours for the given vertex"""
        n_vert = np.max(tris) + 1
        neighbours = [[] for i in range(n_vert)]
        for tri in tris:
            neighbours[tri[0]].append([tri[1], tri[2]])
            neighbours[tri[2]].append([tri[0], tri[1]])
            neighbours[tri[1]].append([tri[2], tri[0]])
        # Get unique neighbours
        for k in range(len(neighbours)):
            neighbours[k] = self.sort_neighbours(neighbours[k])
        return neighbours
    
    def sort_neighbours(self,edges):
        edges=np.vstack(edges)
        n0=edges[0][0]
        sorted_neighbours=np.zeros(len(edges),dtype=int)
        for e_i in np.arange(len(edges)):
            n0 =  edges[:,1][edges[:,0]==n0][0]
            sorted_neighbours[e_i]=n0
        return sorted_neighbours

    
    def findAnglesBetweenTwoVectors1(self,v1s, v2s):
        dot = np.einsum('ijk,ijk->ij',[v1s,v1s,v2s],[v2s,v1s,v2s])
        return np.arccos(dot[0,:]/(np.sqrt(dot[1,:])*np.sqrt(dot[2,:])))

    def calculate_angles_and_dists(self,vertex,neighbours,coords):
        angles=np.zeros(len(neighbours))
        v1=coords[neighbours] - coords[vertex]
        v2=coords[np.roll(neighbours,1)]-coords[vertex]
        angles=findAnglesBetweenTwoVectors1(v1,v2)
        total_angle=angles.sum()
        angles_flattened = 2*pi*angles.cumsum()/total_angle
        return angles_flattened, np.linalg.norm(v1,axis=1)

    def vertex_attributes(self,surf,vertex):
        neighbours=surf['neighbours'][vertex]
        edges = neighbours_to_edges(vertex,neighbours)
        angles,dists = calculate_angles_and_dists(vertex,neighbours,surf['coords'])
        #add self edge with almost zero vals
        edge_attrs=np.vstack([[1e-15,1e-15],np.vstack([angles,dists]).T])
        combined=np.hstack([edges,edge_attrs])
        return combined

    def neighbours_to_edges(self,vertex,neighbours):
        """generate paired ordered list of vertex to neighbours, including self edge"""
        edges=np.vstack([[vertex,vertex],np.vstack([np.repeat(vertex,len(neighbours)),neighbours]).T])
        return edges
    
    def get_exact_edge_attrs(self,level=7):
        file_path = os.path.join(self.icosphere_path,f'ico{level}.edges_and_attrs.npy')
        if os.path.isfile(file_path):
            edges_attrs = np.load(file_path)
        else:            
            edges_attrs = self.calculate_exact_edge_attrs(level=level)
            np.save(file_path,edges_attrs)
        self.icospheres[level]['edges'] = edges_attrs[:,:2]
        self.icospheres[level]['exact_edge_attr'] = edges_attrs[:,2:]
        return
    
    def calculate_exact_edge_attrs(self,level=7):
        surf = self.icospheres[level]
        n_vert = len(surf['coords'])
        all_edge_attrs=[]
        for v in np.arange(n_vert):
            edge_attrs=self.vertex_attributes(surf,v)
            all_edge_attrs.append(edge_attrs)
        all_edge_attrs = np.vstack(all_edge_attrs)
        return all_edge_attrs