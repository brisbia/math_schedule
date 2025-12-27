#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from docplex.mp.priority import Priority

def constraint_each_class_taught_correct_number_of_times (all_courses, df_assigned, df_goals, mdl):
    '''
    all_courses - a variable (object) containing only course names, and every course name
    df_assigned - a dataframe containing the row 'assigned' with binary variables in the form Math_101_0_with_prof_JohnDoe. Recall that the assignment variables will be set to either 0 or 1 (true or false) by the optimization process of the cplex model to generate a valid schedule    
    df_goals - a dataframe containing the rows 'all_courses' containing strings of course names, 'Goal_number_min' containing integers, and 'Goal_number_max' containing integers
    mdl - a cplex model that will have constraints added to it by this function
    
    returns an updated cplex model (mdl in input plus some more constraints)
    
    This adds constraints such that the sum of all the assignment variables for each course can not exceed the Goal_number_max, nor be less than the Goal_number_min
    
    Created by Theodore 2025-09-25
    
    If you get "Error: Adding trivially infeasible linear constraint: '0 >= 1'", double-check that all courses that should be in Meeting_Patterns_large.xlsx, are there. Don't think we need to re-run Overlapping_times_version_1.ipynb unless the class has a new "type" of meeting pattern.
    Another possible cause of this error is if two rows in Meeting_Patterns have the same Time_Index when they shouldn't (or, more specifically, if all meeting patterns for a class' Time_Group have the same Time_Index as the rows for a different Time_Group).
    '''
    #summing all of a class assigment variables and saying that it has to be less than and greater than the min and max number of sections per that class
    for class_name in all_courses:
        #print(class_name)
        #print(df_goals.loc[lambda df: df["all_courses"] == class_name, "Goal_number_min"].iloc[0])
        mdl.add_constraint(mdl.sum(df_assigned.loc[lambda df: df["all_courses"] == class_name, "assigned"]) <= (df_goals.loc[lambda df: df["all_courses"] == class_name, "Goal_number_max"].iloc[0]), ctname = f"max number of {class_name} sections").priority = Priority.MEDIUM
        mdl.add_constraint(mdl.sum(df_assigned.loc[lambda df: df["all_courses"] == class_name, "assigned"]) >= (df_goals.loc[lambda df: df["all_courses"] == class_name, "Goal_number_min"].iloc[0]), ctname = f"min number of {class_name} sections").priority = Priority.MEDIUM
    return mdl

