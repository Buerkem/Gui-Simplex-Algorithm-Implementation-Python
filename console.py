#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 13 17:25:56 2018

@author: infinity
"""

import sympy 
import augment 
import simplex as sp
M = sympy.Symbol('M', positive=True)
#maximization problem sample
#original problem in textbook
#Maximize Z=20x1+10x2
#x1+x2=150
#x1<=40
#x2>=20
#x1,x2>=0 #ignore this part in the matrix representation
#representation for the python simplex algorithm
#format = [[0,coeff of x1 in obj fxn, coeff of x2 in obj fxn],
#          [RHS value,coeff of x1, coeff of x2],
#          [RHS value,coeff of x1, coeff of x2]....] 
#orig_matrix = [[0,20,10],
#               [150,1,1],
#               [40,1,0],
#               [20,0,1]
#               ]
#constraint_equality_signs = ["=",u"\u2264",u"\u2265"] #[<=,>=] in unicode
######################################################################################
#original problem in textbook
#Minimize Z=4x1+3x2
#Constraints: 2x1+4x2>=16
#             3x1+2x2>=12
#Non negativity constraints: x1,x2>=0 #ignore this part in the matrix representation
#representation for the python simplex algorithm to solve
orig_matrix = [[0,4,3],
               [16,2,4],
               [12,3,2]
               ]

constraint_equality_signs = [u"\u2265",u"\u2265"] #[>=,>=] in unicode
command = "minimize" #maximize for maximization problem
command=command.lower() #just in case someone doesn't notice its in lower cases and writes it in some other case
##############################################################################

augment_matrix = augment.get_augment_matrix(constraint_equality_signs,command)
tableau=augment.get_tableau(orig_matrix,augment_matrix)

#tableau = np.array([[0,20,10,0,0,-1*M,-1*M],
#                   [150,1,1,0,0,1,0],
#                   [40,1,0,1,0,0,0],
#                   [20,0,1,0,-1,0,1],
#                   [0,0,0,0,0,0,0],
#                   [0,0,0,0,0,0,0]])
added_variables = augment.get_added_variables(augment_matrix)
all_variables= augment.get_all_variables(orig_matrix,added_variables)
basis_variables=augment.get_basis_variables(added_variables)
print("basis variables: ",basis_variables)

basis = augment.get_bi_values(basis_variables,all_variables,tableau)
#all_variables=["bi","x1","x2","s1","s2","A1","A2"]
#basis_variables=["A1","s1","A2"]
ite_num=1

sp.calculate_zj(tableau,basis)    
sp.calculate_cj_zj(tableau,basis,command)
print(all_variables)
print(tableau)
hir =sp.get_greatest_increase_in_cj_zj_function(tableau)
hir=sp.get_comparable_expression_of(hir)    

while hir>0: # while hir > 0, we can increase our z value
        print("------------------------",ite_num,"---------------------------------------------")
        pivot_col_index=sp.get_pivot_col_index(tableau)
        pivot_row_index=sp.get_pivot_row_index(tableau,pivot_col_index)
        sp.get_new_rows(tableau,basis,all_variables, basis_variables,pivot_row_index,pivot_col_index)
        sp.calculate_zj(tableau,basis)
        sp.calculate_cj_zj(tableau,basis,command)
        
        hir = sp.get_greatest_increase_in_cj_zj_function(tableau)
        
        hir=sp.get_comparable_expression_of(hir)
        
        print(tableau)
        
        ite_num+=1
    

print("End of iteration")
print(sp.display_answer_variables_and_values(tableau, basis_variables))