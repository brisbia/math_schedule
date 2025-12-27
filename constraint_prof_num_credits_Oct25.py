

from docplex.mp.priority import Priority

def constraint_prof_num_credits(df_assigned, df_credits_per_prof, df_credits, mdl):

    """
    Creates constraint for the model for the number of credits a professor can teach.

    Inputs:
    + df_assigned: pandas dataframe containing the binary assignment variables, professors, and courses. Needs columns: 'all_profs', 'assigned', 'all_courses'
    + df_credits_per_prof: pandas dataframe containing range of credits a professor would want to teach. Needs columns: 'all_profs', 'num_credits_max', and 'num_credits_min'
    + df_credits: pandas dataframe containing the number of credits a course is assigned. Needs columns: 'course_name', 'number_of_credits'
    + mdl: cplex model

    Outputs:
    + mdl: cplex model with the added constraints of how many credits a professor can teach.

    By Brynn Oct 2025

    """

    df_assigned_credits = df_assigned.merge(df_credits, on=['all_courses'])
    for prof, course_assignments in df_assigned_credits.groupby(by='all_profs'):
        mdl.add_constraint(mdl.sum(course_assignments['assigned']*course_assignments['number_of_credits']) <= (df_credits_per_prof.loc[lambda df:df['all_profs'] == prof, 'num_credits_max'].values[0]), ctname = f"max credits per {prof}").priority = Priority.MEDIUM 
        mdl.add_constraint(mdl.sum(course_assignments['assigned']*course_assignments['number_of_credits']) >= (df_credits_per_prof.loc[lambda df:df['all_profs'] == prof, 'num_credits_min'].values[0]), ctname = f"min credits per {prof}").priority = Priority.MEDIUM
    return mdl


