# import joblib

def generate(answers):
    difficulty_weights = {'Beginner': 3, 'Intermediate': 5, 'Advanced': 8}
    time_thresholds = {'Beginner': 10, 'Intermediate': 20, 'Advanced': 30}
    penalty_factor = 1

    proficiency_levels = ['Beginner', 'Intermediate', 'Advanced']
    min_scores = [0, 30, 60]

    total_score = 0
    elapsed_time = 0
    correct_ans = 0
    wrong_questions_tags = []
    reports = []

    for answer in answers:

        if answer.question.correct_answer.upper() != answer.answered.upper():
            wrong_questions_tags.append({
                'id': answer.id,
                'tag': answer.question.tags.title,
                'userAnswered': answer.answered,
                'status': answer.status
            })

        reports.append({'questionIndex': answer.id,
                        'correct': True if answer.question.correct_answer.upper() == answer.answered.upper() else False})

        if answer.question.correct_answer.upper() == answer.answered.upper():
            weight = difficulty_weights[answer.question.difficulty_level]
            time_threshold = time_thresholds[answer.question.difficulty_level]
            penalty = penalty_factor * max(0, answer.time_taken - time_threshold)
            bonus = 1 if answer.time_taken < time_threshold else 0
            score = (weight * (1 + bonus)) - penalty

        else:
            score = 0

        total_score += score
        elapsed_time += answer.time_taken

    level_index = -1
    for i in range(len(proficiency_levels)):
        if total_score >= min_scores[i]:
            level_index = i

    if level_index == -1:
        proficiency_level = 'No proficiency level'
    else:
        proficiency_level = proficiency_levels[level_index]

    return {'totalScore': total_score, 'proficiencyLevel': proficiency_level, 'elapsedTime': elapsed_time,
            'wrong': wrong_questions_tags, 'reports': reports}


def generate_roadmap(answers):
    difficulty_weights = {'Beginner': 3, 'Intermediate': 5, 'Advanced': 8}
    time_thresholds = {'Beginner': 10, 'Intermediate': 20, 'Advanced': 30}
    penalty_factor = 1

    proficiency_levels = ['Beginner', 'Intermediate', 'Advanced']
    age_levels = ['young','middle','old','very_old']
    gender_levels = ['male','female','other']
    education_levels = ['Primary School','Middle School','High School','Undergraduate','Graduate','Doctorate']
    min_scores = [0, 30, 60]

    total_score = 0
    elapsed_time = 0
    correct_ans = 0
    wrong_questions_tags = []
    correct_answer_tags = []
    reports = []

    for answer in answers:

        if answer.question.correct_answer.upper() != answer.answered.upper():
            wrong_questions_tags.append({
                'id': answer.id,
                'tag': answer.question.tags.title,
                'level': answer.question.difficulty_level,
                'userAnswered': answer.answered,
                'status': answer.status
            })

        reports.append({'questionIndex': answer.id,
                        'correct': True if answer.question.correct_answer.upper() == answer.answered.upper() else False})

        if answer.question.correct_answer.upper() == answer.answered.upper():
            weight = difficulty_weights[answer.question.difficulty_level]
            time_threshold = time_thresholds[answer.question.difficulty_level]
            penalty = penalty_factor * max(0, answer.time_taken - time_threshold)
            bonus = 1 if answer.time_taken < time_threshold else 0
            score = (weight * (1 + bonus)) - penalty
            correct_answer_tags.append({
                'id': answer.id,
                'tag': answer.question.tags.title,
                'level': answer.question.difficulty_level,
                'markAsCompleted': answer.status,
                'userAnswered': answer.answered,
                'status': answer.status
            })

        else:
            score = 0

        total_score += score
        elapsed_time += answer.time_taken

    level_index = -1
    for i in range(len(proficiency_levels)):
        if total_score >= min_scores[i]:
            level_index = i

    if level_index == -1:
        proficiency_level = 'No proficiency level'
    else:
        proficiency_level = proficiency_levels[level_index]


    """
    !important
    # - uncomment

    """

    features = ['total_score', 'Elapsed time', 'correct_answers', 'correct_big', 'Correct_int', 'correct_adv','Age','Gender', 'Educational Background']


    ###added code for model prediction

    ### Load the trained model

    # model = joblib.load('../data/trained_model.joblib')

    ### Make predictions using the loaded model



    """
    !important
    structure of new_student = [[total_score , Elapsed time , correct_answers , correct_begginner_count , Correct_intermediate_count , correct_advanced_count , Age in number , Gender in number , Educational Background in number ]]
    1. mele age_levels , gender_levels , education_levels enn paranj 3 array und.
    2. nee aadyam usernte age-le data edth athin matching ayittulla age_levelsile index edukuka.
    3. ath edth athinte *index of age_levels* edukua. ennt ath venam Age in number akki kodukkan.
    4. athpole genderum education um cheyyanam.
    5. ennit new_student ulla avide ee array kodukkuka.

    example: 
    predictions = model.predict([[100, 14, 4, 2, 2, 0,3, 0,3 ]])


    """
    # predictions = model.predict(new_student)
    # joblib_prediction = proficiency_levels[predictions[0]]

    # print(f"Predicted Proficiency Level for the new student: {joblib_prediction}")

    ###replace proficiency_level with joblib_prediction
    return {'totalScore': total_score, 'proficiencyLevel': proficiency_level, 'elapsedTime': elapsed_time,
            'wrong': wrong_questions_tags, 'correct_answer': correct_answer_tags, 'reports': reports}
