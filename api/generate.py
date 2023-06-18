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
                'tag': answer.question.tags,
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
