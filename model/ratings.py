from model.entities import Match


class ELORater:
    @staticmethod
    def calculate_goal_index(goal_difference: int) -> float:
        if abs(goal_difference) <= 1:
            return 1
        elif abs(goal_difference) == 2:
            return 1.5
        else:
            return (11 + abs(goal_difference)) / 8

    @staticmethod
    def calculate_expected_result(ratings_difference: int) -> float:
        return 1 / (10 ** (-ratings_difference / 400) + 1)

    @staticmethod
    def get_result(goal_difference):
        if goal_difference > 0:
            return 1
        elif goal_difference < 0:
            return 0
        else:
            return 0.5

    def calculate_points_change(self, match: Match) -> float:
        goal_difference = match.home_score - match.away_score
        home_rating = match.home_team.get_rating(match.date)
        away_rating = match.away_team.get_rating(match.date)

        G = self.calculate_goal_index(goal_difference)
        K = match.type.value
        We = self.calculate_expected_result(home_rating - away_rating)
        W = self.get_result(goal_difference)

        return K * G * (W - We)
