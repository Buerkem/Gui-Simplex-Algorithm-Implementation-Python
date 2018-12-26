#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 13 16:57:23 2018

@author: infinity
"""


import numpy as np
import sympy 

M=sympy.Symbol('M', positive=True)

basis_variables = [] #holds all the basic variables

basis_variable_column=[] #holds the column of the basic variable in the augment matrix
#the augment matrix is the part of the tableau that contains only slack and artificial variables
#the augment matrix is then joined to the original matrix to form the tableau
def get_columns_to_add(constraint_equality_signs):
    """determine the size of the augment matrix ie how many columns will be 
    needed for all the slack and artificial variables that are going to be introduced
    """
    columns_to_add=0 #initial column to add is set to zero
    #iterate through the constraint equality signs, If it is a <= sign, a slack variable will be
    #introduced so add one variable for the slack. If it is a >= sign, a surplus and artificial 
    #variable will be introduced so add two columns for the surplus and artificial variables 
    #if its an equal to sign, a slack and artificial variable will be introduced, so also add two 
    #columns
    for equality_symbol_index in range(len(constraint_equality_signs)):
        if constraint_equality_signs[equality_symbol_index] == u"\u2264": #<=
            #add a slack variable
            columns_to_add+=1
            
        elif constraint_equality_signs[equality_symbol_index] == u"\u2265": # >=
            #add a slack variable and an artificial variable
            columns_to_add+=2
        
        else:#if it's an equal to sign
            columns_to_add+=1

    return columns_to_add

def get_augment_matrix(constraint_equality_signs,cmd="maximize"):
    """
    gets the augment matrix which is the augment matrix is the part of the tableau that contains only slack and
    artificial variables the augment matrix is then joined to the original matrix to form the tableau. 
    Note: Two rows will be added in the get_tableau function to hold the zj and cj-zj values
    """
    columns_to_add=get_columns_to_add(constraint_equality_signs)
    numof_rows_augment_matrix=len(constraint_equality_signs)+1 #+1 because of the objective fxn
    augment_matrix = np.zeros((numof_rows_augment_matrix,columns_to_add), dtype=sympy.Symbol)
    #the objective fxn will occupy the first column of the augmented matrix
    introduced_variable_index=0#stores the column number that the introduced slack,artificial or 
    #surplus variable will possess in the augmented matrix
    #iterate through the constraint equality signs, if it's <= add a slack, if  it's 
    #>= subtract a surplus and add an art ificial variable multiplied by -M. If its =,
    #introduce a slack and multiply it by M
    for equality_symbol_index in range(len(constraint_equality_signs)):
        if constraint_equality_signs[equality_symbol_index] == u"\u2264":
            #add a slack variable
            augment_matrix[equality_symbol_index+1,introduced_variable_index]=1
            introduced_variable_index+=1
            basis_variable_column.append(introduced_variable_index)
            
        elif constraint_equality_signs[equality_symbol_index] == u"\u2265":
            #subtract a surplus variable and add/subtract an artificial variable
            #subtract a surplus variable
            augment_matrix[equality_symbol_index+1,introduced_variable_index]=-1
            introduced_variable_index+=1
            if cmd == "maximize":
                #subtract an artificial variable if its a maximization problem
                augment_matrix[0,introduced_variable_index]=-1*M
            else:
                #add an artificial variable if its a minimization problem
                augment_matrix[0,introduced_variable_index]=1*M
                
            augment_matrix[equality_symbol_index+1,introduced_variable_index]=1
            introduced_variable_index+=1
            basis_variable_column.append(introduced_variable_index)
        
        else:
            #if the constraint is an equality, subtract artficial variable if its maximization and 
            #add artificial variable if its minimization
            if cmd == "maximize":
                augment_matrix[0,introduced_variable_index]=-1*M
            else:
                augment_matrix[0,introduced_variable_index]=1*M
                
            augment_matrix[equality_symbol_index+1,introduced_variable_index]=1
            introduced_variable_index+=1
            basis_variable_column.append(introduced_variable_index)
    return augment_matrix

def get_tableau(orig_matrix,augment_matrix):
    #augment_matrix = get_augment_matrix(constraint_equality_signs)
    tableau=np.concatenate((np.array(orig_matrix), augment_matrix),axis=1)

    #add two empty rows to hold zj and cj-zj values
    numof_tableau_rows,numof_tableau_cols = tableau.shape
    two_empty_rows = np.zeros((2,numof_tableau_cols), dtype=sympy.Symbol)
    tableau=np.concatenate((tableau,two_empty_rows),axis=0)
    
    return tableau

def get_non_basis_variables(orig_matrix):
    """
    gets the non basic variables in a list such as [x1,x2]
    """
    non_basis_variables=[]
    orig_matrix = np.array(orig_matrix)
    orig_matrix_rows,orig_matrix_cols = orig_matrix.shape
    for i in range(orig_matrix_cols-1):
        non_basis_variables.append(str("x"+str(i+1)))
    return non_basis_variables

def get_added_variables(augment_matrix):
    """
    gets whether a variable added was a slack or artificial variable 
    and returns it as a list such as [s1,s2,a1,a2]
    """
    first_row = augment_matrix[0]
    ite=1
    added_variables=[]
    artificial_ite=1
    slack_ite = 1
    for i in range(len(first_row)):
        if first_row[i]== -M or first_row[i]== M:
            ite=artificial_ite
            added_variables.append(str("a"+str(ite)))
            artificial_ite+=1
        else: 
            ite=slack_ite
            added_variables.append(str("s"+str(ite)))
            slack_ite+=1
    
    return added_variables

def get_all_variables(orig_matrix,added_variables):
    #add the bi column first before adding the columns for other variables
    all_variables =["bi"]
    non_basis_variables=get_non_basis_variables(orig_matrix)
    all_variables+=non_basis_variables
    all_variables+=added_variables
    return all_variables

def get_basis_variables(added_variables):
    basis_variables=[]
    for i in range(len(basis_variable_column)):
        basis_variables.append(added_variables[basis_variable_column[i]-1])
    return basis_variables

def get_bi_values(basis_variables,all_variables,tableau):
    cj_value = tableau[0]
    bi_values=[]
    for basis_variable in basis_variables:
        bi_index = all_variables.index(basis_variable)
        bi_value = cj_value[bi_index]
        bi_values.append(bi_value)
    return bi_values
        
def clear_basis_variable_column():
    global basis_variable_column
    basis_variable_column=[]