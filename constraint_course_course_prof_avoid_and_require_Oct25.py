#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from docplex.mp.priority import Priority


# In[ ]:


def constraint_course_course_prof_avoid_and_require(df_course_course_prof_constraints, df_assigned, df_goals, all_profs, mdl):
    '''
    inputs:
        df_course_course_prof_constraints -> needs two columns of courses and type, either avoid or require
        df_assigned -> dataframe containing assignment variables
        df_goals -> needs goal numbers for how many credits you're going to teach of eachc class
        all_profs -> pandas series containing the name of all professors
        mdl -> docplex model, constraints will be added
        
    outputs:
        returns mdl but with more constraints. This function should work inplace.
        
    some courses can't be/have to be taught by the same prof
    Avoid = If a prof teaches a section of course_1, they cannot teach any of course_2, and vice versa

    Require = If a prof teaches x sections of course_1, they must teach exactly x sections of course_2, and vice versa. This assumes that the same number of sections of course_1 and course_2 are running
    '''
    #I want to write a feasibility check for the sake of my sanity so I need them before that cell
    #TS 11/18/24
    df_course_course_prof_cts_avoid = df_course_course_prof_constraints.loc[df_course_course_prof_constraints['Type'] == "Avoid"]
    df_course_course_prof_cts_require = df_course_course_prof_constraints.loc[df_course_course_prof_constraints['Type'] == "Require"]

    df_course_1_assigned_avoid = df_course_course_prof_cts_avoid.copy().rename(columns = {"Course_1":"all_courses"}).merge(df_assigned)
    df_course_2_assigned_avoid = df_course_course_prof_cts_avoid.copy().rename(columns = {"Course_2":"all_courses"}).merge(df_assigned)

    df_course_1_assigned_require = df_course_course_prof_cts_require.copy().rename(columns = {"Course_1":"all_courses"}).merge(df_assigned)
    df_course_2_assigned_require = df_course_course_prof_cts_require.copy().rename(columns = {"Course_2":"all_courses"}).merge(df_assigned)

    #Following code not in shared drive

    df_course_course_prof_cts_require = df_course_course_prof_cts_require.copy().drop(["Type"], axis = 1)
    # df_course_course_prof_cts_require
    df_goals_class_index = df_goals.set_index(df_goals['all_courses'])
    # df_course_course_prof_cts_require.at[1,'Course_2'] = 'Math 246'
    # print(df_course_course_prof_cts_require)
    for index, row in df_course_course_prof_cts_require.iterrows():
        goals_slice = df_goals_class_index.loc[[row.iloc[0], row.iloc[1]]]
        #print(goals_slice)
        if (goals_slice.iloc[0]["Goal_number_min"] > goals_slice.iloc[1]["Goal_number_max"]) or (goals_slice.iloc[1]["Goal_number_min"] > goals_slice.iloc[0]["Goal_number_max"]):
            raise ValueError(f'check to ensure the same number of sections are running for each set of courses required to be taught by the same professor')
    #     print(row.iloc[1])
    
    if not df_course_1_assigned_avoid.empty:
        for prof in all_profs:
            #               if the sum of assignment variables for prof with course_1 is >= 1,
            #                       then the sum of assignment variables for prof with course_2 <= 0
            mdl.add_if_then(sum(df_course_1_assigned_avoid.loc[df_course_1_assigned_avoid['all_profs']==prof]['assigned'])>= 1, sum(df_course_2_assigned_avoid.loc[df_course_2_assigned_avoid['all_profs']==prof]['assigned']) <= 0).priority = Priority.LOW
            mdl.add_if_then(sum(df_course_2_assigned_avoid.loc[df_course_2_assigned_avoid['all_profs']==prof]['assigned'])>= 1, sum(df_course_1_assigned_avoid.loc[df_course_1_assigned_avoid['all_profs']==prof]['assigned']) <= 0).priority = Priority.LOW
    if not df_course_1_assigned_require.empty:
        for prof in all_profs:
            mdl.add_constraint(sum(df_course_1_assigned_require.loc[df_course_1_assigned_require['all_profs']==prof]['assigned']) == sum(df_course_2_assigned_require.loc[df_course_2_assigned_require['all_profs']==prof]['assigned']), ctname = f'required_to_teach_both_courses_for_{prof}').priority = Priority.HIGH
    return mdl

