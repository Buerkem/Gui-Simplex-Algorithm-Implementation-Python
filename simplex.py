#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 10 23:33:24 2018

@author: infinity
"""
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

import numpy as np
import sympy

M = sympy.Symbol('M', positive=True)
LARGE_VALUE=99999999

def get_comparable_expression_of(value):
    """NOTE: Since we can't directly check whether an expression such as 2M+1 is greater
    than say 2, we have to substitute a value into M then compare and get back our original
    expression. get_comparable_expression_of substitutes a large number into M so that it can 
    be compared with another value in terms of whether it is greater than etc
    """
    
    if type(value) == np.float64 or type(value)==int or type(value)==float:
            comparable_value=value
    else:
        comparable_value=value.subs({M:LARGE_VALUE})  
        
    return comparable_value

def get_maximum_positive_number(row):
    #Make sure first row of tableau is left with only non basic and basic variables
    #by removing RHS value(last element) and coefficient of Z(first element)
    #row = row[1:]#remove first element from row
    coeffs_of_basic_and_non_basic_variables= row[1:]#remove first element from row
    
    #iterate through first row and find the maximum negative number
    current_max_pos_num=0 #set intial maximum negative number to zero so that it can be overriden
    for coeff in coeffs_of_basic_and_non_basic_variables:
        #store the original expressions

        original_value_of_coeff=coeff
        original_value_of_current_max_pos_num=current_max_pos_num
        
        #check to see if the coeff is an integer or float. If it is, leave it as   
        #it is or else its an expression of M so substitute a large value into it
        coeff=get_comparable_expression_of(coeff)
        
        #check to see if the current maximum negative number is an integer or float.If it is,   
        #leave it as it is or else its an expression of M so substitute a large value into it
        current_max_pos_num =get_comparable_expression_of(current_max_pos_num)
        
        #compare the coeff to the current max negative number to see which is more negative
        #and set the current maximum negative number to the more negative one's original
        #expression (set to original expression to retrieve any expression of M after 
        # substituting)
        if coeff > current_max_pos_num:
            current_max_pos_num = original_value_of_coeff
        else:
            current_max_pos_num=original_value_of_current_max_pos_num
            
    return current_max_pos_num

def calculate_zj(tableau,basis):
    #remove objective function
    constraint_tableau = np.delete(tableau,0,0)
    #remove cj-zj and zj
    constraint_tableau = np.delete(constraint_tableau,-1,0)
    constraint_tableau = np.delete(constraint_tableau,-1,0)
    
    numof_constraint_tableau_rows,numof_constraint_tableau_columns = constraint_tableau.shape
    zj_row = np.zeros((1,numof_constraint_tableau_columns), dtype=sympy.Symbol)
    
    for i in range(numof_constraint_tableau_rows):
        zj_row = zj_row + basis[i]*constraint_tableau[i]
    
    tableau[-2]=zj_row
    
    return zj_row

def calculate_cj_zj(tableau,basis,cmd="maximize"):
    #remove objective function
    zj=calculate_zj(tableau,basis)
    objective_function = tableau[0]
    if cmd=="maximize":
        cj_zj = objective_function - zj
    else:
        cj_zj = zj-objective_function
    tableau[-1]=cj_zj 
    
    return cj_zj

def get_greatest_increase_in_cj_zj_function(tableau):
    cj_zj_row = tableau[-1]
    #hir= highest increase rate
    hir= get_maximum_positive_number(cj_zj_row )
    return hir

#determine the pivot column
def get_pivot_col_index(tableau):
    cj_zj_row =tableau[-1] #converted to list because numpy has no index property
    #hir= highest increase rate
    hir= get_maximum_positive_number(cj_zj_row )
    pivot_col_index = list(cj_zj_row).index(hir)
    return pivot_col_index

def get_pivot_row_index(tableau,pivot_col):
    """Now that we have the pivot column, how do we determine the pivot row?
    Divide each row's Right Hand Side column by corresponding pivot value in column
    Find out which row has the minimum non negative number and return that row
    """
    nonneg_nums_after_RHS_division=[]
    
    #remove objective function
    constraint_tableau = np.delete(tableau,0,0)
    #remove cj-zj and zj
    constraint_tableau = np.delete(constraint_tableau,-1,0)
    constraint_tableau = np.delete(constraint_tableau,-1,0)
    
    #get the row and index of the tableau
    last_row_on_constraint_tableau_index,last_col_on_constraint_tableau_index=constraint_tableau.shape
    first_col_on_constraint_tableau_index=0#subtract 1 to get correct index since array numbering starts from zero
    
    #iterate through the table by performing num_in_bi_on_row_i/numinpivotcol_on_row_i and
    #store output of all non negative numbers in a list since we want min non negative num
    for i in range(last_row_on_constraint_tableau_index):
        num_in_bi_on_row_i=constraint_tableau[i,first_col_on_constraint_tableau_index]
        orig_num_in_bi_on_row_i = num_in_bi_on_row_i
        num_in_bi_on_row_i=get_comparable_expression_of(num_in_bi_on_row_i)
        
        numinpivotcol_on_row_i = constraint_tableau[i,pivot_col]
        orig_numinpivotcol_on_row_i = numinpivotcol_on_row_i 
        numinpivotcol_on_row_i = get_comparable_expression_of(numinpivotcol_on_row_i )
        try:
            num_after_pivot_div = num_in_bi_on_row_i/numinpivotcol_on_row_i
        except ZeroDivisionError:
            continue
        #if num is positive, add to non negative numbers after pivot division
        if num_after_pivot_div > 0:
            num_in_bi_on_row_i = orig_num_in_bi_on_row_i  
            numinpivotcol_on_row_i = orig_numinpivotcol_on_row_i 
            num_after_pivot_div = num_in_bi_on_row_i/numinpivotcol_on_row_i
            
            nonneg_nums_after_RHS_division.append(num_after_pivot_div)
    
    #determine the mininimum non negative from the list of stored non negative numbers
    try:
        min_non_neg_num=min(nonneg_nums_after_RHS_division)
    except ValueError:
        return None

    #iterate again to find the mininimum non negative number's row by performing 
    #num_in_bi_on_row_i/numinpivotcol_on_row_i to see which row will give us the minimum 
    #non negative number we just determined. When you find it, return it
    for i in range(last_row_on_constraint_tableau_index):
        num_in_bi_on_row_i=constraint_tableau[i,first_col_on_constraint_tableau_index]
        numinpivotcol_on_row_i = constraint_tableau[i,pivot_col]
        try:
            num_after_pivot_div = num_in_bi_on_row_i/numinpivotcol_on_row_i
        except ZeroDivisionError:
            continue
        #if num is positive, add to non negative numbers after pivot division
        if num_after_pivot_div == min_non_neg_num :
            min_non_neg_num_row_index = i+1#1 is added because we deleted the objective fxn
            #which caused its index in the original tableau to decrease
            break
        
    return min_non_neg_num_row_index

def get_new_pivot_row(tableau,pivot_row_index,pivot_col_index):
    pivot_row = tableau[pivot_row_index]
    pivot_num = tableau[pivot_row_index, pivot_col_index]
    new_pivot_row = pivot_row/pivot_num 
    
    return new_pivot_row

#perform gaussian elimination on the rows
def get_new_rows(tableau,basis,all_variables, basic_variables,pivot_row_index,pivot_col_index):
    new_pivot_row = get_new_pivot_row(tableau,pivot_row_index,pivot_col_index)
    obj_fxn=tableau[0]
    #remove objective function
    constraint_tableau = np.delete(tableau,0,0)
    #remove cj-zj and zj
    constraint_tableau = np.delete(constraint_tableau,-1,0)
    constraint_tableau = np.delete(constraint_tableau,-1,0)
    last_row_on_tableau_index,last_col_on_tableau_index=constraint_tableau.shape
    last_col_on_tableau_index-=1#subtract 1 since array numbering starts from zero
    #enter an entering basic variable and remove a leaving basic variable
    #basic_variables[pivot_row_index] = all_variables[pivot_col_index ]
    
    #enter an entering basic variable and remove a leaving basic variable
    basic_variables[pivot_row_index-1] = all_variables[pivot_col_index ]
    #subtract 1 because basis row does not include objective fxn row
    basis[pivot_row_index-1]=obj_fxn[pivot_col_index]
    
    for i in range(1,last_row_on_tableau_index+1):
        row_to_be_changed = tableau[i]
        num_in_pivot_col_for_row_i = tableau[i,pivot_col_index]
        #multiply the negative of num_in_pivot_col_for_row_i by pivot_num and add
        #idea: make sure coefficients of pivot num in other locations apart
        #from pivot col are zero
        gauss_pivot_row = num_in_pivot_col_for_row_i*-1*new_pivot_row
        new_row = gauss_pivot_row + row_to_be_changed
        #replace the old tableau row with its corresponding new row
        tableau[i]=new_row
    
    #performing gaussian elimination sets all pivot row numbers to zero
    #hence we need to replace it with the new pivot row
    tableau[pivot_row_index]=new_pivot_row 
    return tableau

def display_answer_variables_and_values(final_tableau, basic_variables):
    answer_variable_and_values=" "
    for i in range(len(basic_variables)):
        #1 is added to i because first row contains objective function
        print(basic_variables[i],"=",final_tableau[i+1][0])
        answer_variable_and_values += basic_variables[i]+"= "+str(final_tableau[i+1][0]) + "    "
    #print("Z = ", final_tableau[-2][0])
    answer_variable_and_values+="Z= "+str(final_tableau[-2][0])
    return answer_variable_and_values

