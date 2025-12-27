
from docplex.mp.priority import Priority

def constraint_dist_throughout_day( df_times, df_assigned, df_goals, max_number_sections_to_be_at_diff_times, mdl):

    """

Adds constraints so that courses have their maximum sections less than or equal to 'max_number_sections_to_be_at_diff_times' to not be overlapping for any professor.

Inputs:
+ df_times: pandas dataframe of all the possible times (meeting patterns) which a course can be offered
+ df_assigned: pandas dataframe containing all of the binary assignment variables 
+ df_goals: pandas dataframe containing the goal number of sections for a course to have
+ max_number_sections_to_be_at_diff_times: the distinguishing number of sections that determines if either the courses are constrained or preferred to be nonoverlapping
+ mdl: cplex model

Outputs:
+ mdl: cplex model with added contraints from function

Created by Brynn Oct 2025

"""

    df_time_assigned = df_times.loc[df_times['all_times'].isin(df_assigned['all_times'])].copy()
    df_time_assigned.drop(columns = ['Day','Start_Time','End_Time','Time_Group'], inplace=True)
    df_time_assigned = df_assigned.merge(df_times, on='all_times')

    for times in df_time_assigned['all_times'].unique():
        df_time_seperate = df_time_assigned.loc[df_time_assigned['all_times']==times].copy().reset_index().dropna()

        if not df_time_seperate['overlap_times'].empty: # so no asych courses
            df_time_overlap_options = df_time_assigned.loc[df_time_assigned['all_times'].isin(df_time_seperate['overlap_times'][0])]

            for course in df_time_assigned['all_courses'].unique():

                 if df_goals.loc[df_goals['all_courses'] == course]['Goal_number_max'].unique()[0] <= max_number_sections_to_be_at_diff_times:
                    df_time_assigned_course_diff = df_time_assigned.loc[df_time_assigned['all_courses'] == course]
                    df_overlap_course = df_time_overlap_options.loc[df_time_overlap_options['all_courses'] == course]
                    df_overlap_course = df_overlap_course.drop_duplicates(["all_courses_and_times"])   
                    mdl.add_constraint(mdl.sum(df_overlap_course.loc[df_overlap_course['all_times']==times]['assigned'])<=1).priority = Priority.MEDIUM

                    if len(df_overlap_course['all_times'].unique()) >1:
                        mdl.add_if_then(mdl.sum(df_overlap_course.loc[df_overlap_course['all_times']==times]['assigned'])<=max_number_sections_to_be_at_diff_times, mdl.sum(df_overlap_course.loc[df_overlap_course['all_times']!=times]['assigned'])==0).priority = Priority.MEDIUM

    return mdl





