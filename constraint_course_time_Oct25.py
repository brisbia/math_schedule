#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# from docplex.mp.priority import Priority


# In[ ]:


def constraint_course_time(df_course_time_constraints,df_assigned,mdl):
    """
    inputs:
        df_course_time_constraints - dataframe containing columns:
            'Course'
            'Time'
            'Type' containing strings "Require" or "Avoid"
        df_assigned - containing columns:
            'all_courses'
            'assigned' - with cplex assignment variables
        mdl -  a cplex model
        
    returns an updated cplex model (mdl in input plus some more constraints). This function appears to work inplace.
    Created by Theodore 2025-10-6
    """
    for idx in range(df_course_time_constraints.shape[0]):
        ind_course_df = df_course_time_constraints.iloc[idx]
        df_assigned_ind_course = df_assigned.loc[df_assigned['all_courses']==ind_course_df['Course']].loc[df_assigned['all_times']==ind_course_df['Time']]
        if ind_course_df['Type'] == "Require":
            mdl.add_constraint(mdl.sum(df_assigned_ind_course['assigned']) >= 1)
        elif ind_course_df['Type'] == "Avoid":
            mdl.add_constraint(mdl.sum(df_assigned_ind_course['assigned']) ==0)
    
    return mdl

