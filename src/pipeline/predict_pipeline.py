import pandas as pd
import numpy as np

class PredictPipeline:
    def __init__(self):
        self.subjects = ['math_score','reading_score','writing_score',
                         'english_score','computer_score','science_score','social_score']

    def predict(self, df: pd.DataFrame):
        results = []
        for idx, row in df.iterrows():
            scores = {sub: int(row[sub]) for sub in self.subjects}
            strongest = max(scores, key=scores.get)
            weakest = min(scores, key=scores.get)
            overall = round(np.mean(list(scores.values())),2)
            badge = self.assign_badge(overall)
            recommendation = f"Focus on improving {weakest.replace('_score','').title()}"
            results.append({
                "roll": row.get('roll_number', idx+1),
                "name": row.get('name', f"Student {idx+1}"),
                "scores": scores,
                "strongest": strongest.replace('_score','').title(),
                "weakest": weakest.replace('_score','').title(),
                "overall": overall,
                "badge": badge,
                "recommendation": recommendation
            })
        return results

    def assign_badge(self, overall):
        if overall >= 90:
            return "🏆 Star Performer"
        elif overall >= 75:
            return "🥈 Good Performer"
        elif overall >= 60:
            return "🥉 Average Performer"
        else:
            return "⚠️ Needs Improvement"

    def class_statistics(self, df: pd.DataFrame):
        stats = {}
        for sub in self.subjects:
            stats[sub] = {
                "average": round(df[sub].mean(),2),
                "median": round(df[sub].median(),2),
                "max": df[sub].max(),
                "min": df[sub].min()
            }
        return stats
