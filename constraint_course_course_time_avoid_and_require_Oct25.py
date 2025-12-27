#!/usr/bin/env python
# coding: utf-8

# # Avoid

# In[ ]:

from docplex.mp.priority import Priority


def constraint_course_course_time_avoid (df_course_course_time_constraints, df_time_assigned, mdl):
    """
    inputs:
        df_course_course_time_constraints - a dataframe containing columns "Type" with values of either 'Avoid' or 'Require', 'Course_1' & 'Course_2' containing the names of courses that are being constrained with/against each other, 'Priority_level' of either "MEDIUM" "LOW" "VERY_LOW" or "MANDATORY" ("HIGH" and "VERY_HIGH" do not work in this version of the code)
        df_time_assigned -  a dataframe containing columns 'all_courses' with the name of every course, 'all_times', and the assignment variables created by Cplex
        mdl - a cplex model
        
    returns an updated cplex model (mdl in input plus some more constraints). This function appears to work inplace.
    Created by Theodore 2025-10-6
    """
    
    df_2_course_time_avoid_constraint = df_course_course_time_constraints.loc[df_course_course_time_constraints['Type']=="Avoid"].reset_index()
    for idx in range(df_2_course_time_avoid_constraint.shape[0]):
        course_pairs = df_2_course_time_avoid_constraint.iloc[idx]
        df_assigned_course_1 = df_time_assigned.loc[df_time_assigned['all_courses']==course_pairs['Course_1']]
        df_assigned_course_2 = df_time_assigned.loc[df_time_assigned['all_courses']==course_pairs['Course_2']]
        if df_assigned_course_1.shape[0] >0  and df_assigned_course_2.shape[0]>0:
            for time in df_assigned_course_1['all_times'].unique():
                df_1_by_time = df_assigned_course_1.loc[df_assigned_course_1['all_times'] == time].reset_index()
                df_overlaps = df_assigned_course_2.loc[df_assigned_course_2['all_times'].isin(df_1_by_time['overlap_times'][0])]
                if df_overlaps.shape[0] > 0:
                    if df_2_course_time_avoid_constraint.loc[idx, 'Priority_level'] == 'MEDIUM':
                        mdl.add_if_then(mdl.sum(df_1_by_time['assigned'])>=1, mdl.sum(df_overlaps['assigned']) == 0).priority = Priority.MEDIUM
                        mdl.add_if_then(mdl.sum(df_overlaps['assigned'])>=1, mdl.sum(df_1_by_time['assigned']) == 0).priority = Priority.MEDIUM
                    elif df_2_course_time_avoid_constraint.loc[idx, 'Priority_level'] == 'LOW':
                        mdl.add_if_then(mdl.sum(df_1_by_time['assigned'])>=1, mdl.sum(df_overlaps['assigned']) == 0).priority = Priority.LOW
                        mdl.add_if_then(mdl.sum(df_overlaps['assigned'])>=1, mdl.sum(df_1_by_time['assigned']) == 0).priority = Priority.LOW
                    elif df_2_course_time_avoid_constraint.loc[idx, 'Priority_level'] == 'VERY_LOW':
                        mdl.add_if_then(mdl.sum(df_1_by_time['assigned'])>=1, mdl.sum(df_overlaps['assigned']) == 0).priority = Priority.VERY_LOW
                        mdl.add_if_then(mdl.sum(df_overlaps['assigned'])>=1, mdl.sum(df_1_by_time['assigned']) == 0).priority = Priority.VERY_LOW
    #              HIGH and VERY_HIGH produce some weird behavior because they're higher than the current priority that professors keep classes
    #              This should probably be fixed by constraining it so that it's a higher priority that professors teach classes
    #              But I've commented these out so they'll default to medium, which mostly works I think?
    #                 elif df_2_course_time_avoid_constraint.loc[idx, 'Priority_level'] == 'HIGH':
    #                     mdl.add_if_then(mdl.sum(df_1_by_time['assigned'])>=1, mdl.sum(df_overlaps['assigned']) == 0).priority = Priority.HIGH
    #                     mdl.add_if_then(mdl.sum(df_overlaps['assigned'])>=1, mdl.sum(df_1_by_time['assigned']) == 0).priority = Priority.HIGH
    #                 elif df_2_course_time_avoid_constraint.loc[idx, 'Priority_level'] == 'VERY_HIGH':
    #                     mdl.add_if_then(mdl.sum(df_1_by_time['assigned'])>=1, mdl.sum(df_overlaps['assigned']) == 0).priority = Priority.VERY_HIGH
    #                     mdl.add_if_then(mdl.sum(df_overlaps['assigned'])>=1, mdl.sum(df_1_by_time['assigned']) == 0).priority = Priority.VERY_HIGH
                    elif df_2_course_time_avoid_constraint.loc[idx, 'Priority_level'] == 'MANDATORY':
                        mdl.add_if_then(mdl.sum(df_1_by_time['assigned'])>=1, mdl.sum(df_overlaps['assigned']) == 0).priority = Priority.MANDATORY
                        mdl.add_if_then(mdl.sum(df_overlaps['assigned'])>=1, mdl.sum(df_1_by_time['assigned']) == 0).priority = Priority.MANDATORY
                    else:
                        mdl.add_if_then(mdl.sum(df_1_by_time['assigned'])>=1, mdl.sum(df_overlaps['assigned']) == 0)
                        mdl.add_if_then(mdl.sum(df_overlaps['assigned'])>=1, mdl.sum(df_1_by_time['assigned']) == 0)

    
    
    return mdl


# In[ ]:

def constraint_course_course_time_require(df_course_course_time_constraints, df_time_assigned, mdl):
    """
    inputs:
        df_course_course_time_constraints - a dataframe containing columns "Type" with values of either 'Avoid' or 'Require', 'Course_1' & 'Course_2' containing the names of courses that are being constrained with/against each other, 'Priority_level' of either "MEDIUM" "LOW" "VERY_LOW" or "MANDATORY" ("HIGH" and "VERY_HIGH" do not work in this version of the code)
        df_time_assigned -  a dataframe containing columns 'all_courses' with the name of every course, 'all_times', and the assignment variables created by Cplex
        mdl - a cplex model
        
    returns an updated cplex model (mdl in input plus some more constraints). This function appears to work inplace.
    Created by Theodore 2025-10-6
    """
    df_2_course_time_require_constraint = df_course_course_time_constraints.loc[df_course_course_time_constraints['Type']=="Require"].reset_index()
    for idx in range(df_2_course_time_require_constraint.shape[0]):
        course_pair = df_2_course_time_require_constraint.iloc[idx]
        df_course_1 = df_time_assigned.loc[df_time_assigned['all_courses'] == course_pair['Course_1']]
        df_course_2 = df_time_assigned.loc[df_time_assigned['all_courses'] == course_pair['Course_2']]
        list_of_overlapped_times_accounted_for = []
        if df_course_1.shape[0] >0 and df_course_2.shape[0] >0:
            for times in df_course_1['all_times'].unique():
                df_time_1 = df_course_1.loc[df_course_1['all_times']==times].reset_index()
                if df_time_1.shape[0]>0:
                    if times not in list_of_overlapped_times_accounted_for:
                        list_of_overlapped_times_accounted_for += df_time_1['overlap_times'].iloc[0]
                        df_time_2 = df_course_2.loc[df_course_2['all_times'].isin(df_time_1['overlap_times'].iloc[0])] # change .isin(df_time_1['overlap_times']) to == times, if same timeslot required
                        if df_time_2.shape[0]>0:
                            if df_2_course_time_require_constraint.loc[idx, 'Priority_level'] == 'MEDIUM':
                                mdl.add_if_then(mdl.sum(df_time_1['assigned']) >= 1, mdl.sum(df_time_2['assigned'])>=1).priority = Priority.MEDIUM
                                mdl.add_if_then(mdl.sum(df_time_2['assigned'])>=1,  mdl.sum(df_time_1['assigned'])>=1).priority = Priority.MEDIUM # this might be redundant 
                            elif df_2_course_time_require_constraint.loc[idx, 'Priority_level'] == 'LOW':
                                mdl.add_if_then(mdl.sum(df_time_1['assigned']) >= 1, mdl.sum(df_time_2['assigned'])>=1).priority = Priority.LOW
                                mdl.add_if_then(mdl.sum(df_time_2['assigned'])>=1,  mdl.sum(df_time_1['assigned'])>=1).priority = Priority.LOW
                            elif df_2_course_time_require_constraint.loc[idx, 'Priority_level'] == 'VERY_LOW':
                                mdl.add_if_then(mdl.sum(df_time_1['assigned']) >= 1, mdl.sum(df_time_2['assigned'])>=1).priority = Priority.VERY_LOW
                                mdl.add_if_then(mdl.sum(df_time_2['assigned'])>=1,  mdl.sum(df_time_1['assigned'])>=1).priority = Priority.VERY_LOW
    #                       As with above code block, HIGH and VERY_HIGH act weird, so I've commented them out so they default to medium
    #                         elif df_2_course_time_require_constraint.loc[idx, 'Priority_level'] == 'HIGH':
    #                             mdl.add_if_then(mdl.sum(df_time_1['assigned']) >= 1, mdl.sum(df_time_2['assigned'])>=1).priority = Priority.HIGH
    #                             mdl.add_if_then(mdl.sum(df_time_2['assigned'])>=1,  mdl.sum(df_time_1['assigned'])>=1).priority = Priority.HIGH
    #                         elif df_2_course_time_require_constraint.loc[idx, 'Priority_level'] == 'VERY_HIGH':
                                mdl.add_if_then(mdl.sum(df_time_1['assigned']) >= 1, mdl.sum(df_time_2['assigned'])>=1).priority = Priority.VERY_HIGH
    #                             mdl.add_if_then(mdl.sum(df_time_2['assigned'])>=1,  mdl.sum(df_time_1['assigned'])>=1).priority = Priority.VERY_HIGH
                            elif df_2_course_time_require_constraint.loc[idx, 'Priority_level'] == 'MANDATORY':
                                mdl.add_if_then(mdl.sum(df_time_1['assigned']) >= 1, mdl.sum(df_time_2['assigned'])>=1).priority = Priority.MANDATORY
                                mdl.add_if_then(mdl.sum(df_time_2['assigned'])>=1,  mdl.sum(df_time_1['assigned'])>=1).priority = Priority.MANDATORY
                            else:
                                mdl.add_if_then(mdl.sum(df_time_1['assigned']) >= 1, mdl.sum(df_time_2['assigned'])>=1)
                                mdl.add_if_then(mdl.sum(df_time_2['assigned'])>=1,  mdl.sum(df_time_1['assigned'])>=1)
    return mdl
