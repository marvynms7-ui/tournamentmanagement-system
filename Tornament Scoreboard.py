import json
import os
import random
import tkinter as tk
from tkinter import messagebox, simpledialog


class Tournament:
    def __init__(self, filename="tournament_data.json"):
        self.filename = filename
        self.teams = {}
        self.individuals = {}
        self.load_data()

    def register_team(self, team_name, members):
        if len(members) < 1:
            raise ValueError("Team must have at least 1 member.")
        if team_name in self.teams:
            raise ValueError("Team already registered.")
        self.teams[team_name] = {
            "members": [{"name": m, "score": 0} for m in members],
            "total_score": 0
        }

    def register_individual(self, name):
        if name in self.individuals:
            raise ValueError("This individual is already registered.")
        self.individuals[name] = 0

    def get_scores(self):
        output = "Team Rankings:\n"
        sorted_teams = sorted(self.teams.items(), key=lambda x: x[1]["total_score"], reverse=True)
        for team, info in sorted_teams:
            output += f"  {team}: {info['total_score']} points\n"

        output += "\nIndividual Rankings:\n"
        sorted_inds = sorted(self.individuals.items(), key=lambda x: x[1], reverse=True)
        for name, score in sorted_inds:
            output += f"  {name}: {score} points\n"

        return output.strip()

    def save_data(self):
        for team_name, team_info in self.teams.items():
            total = sum(m.get("score", 0) for m in team_info["members"])
            team_info["total_score"] = total

        data = {
            "teams": self.teams,
            "individuals": self.individuals
        }
        with open(self.filename, "w") as f:
            json.dump(data, f, indent=4)

    def load_data(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                data = json.load(f)
                self.teams = data.get("teams", {})
                self.individuals = data.get("individuals", {})


class TournamentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tournament Management System")
        self.tourney = Tournament()

        tk.Label(root, text="Tournament Management", font=("Arial", 16)).pack(pady=10)

        tk.Button(root, text="Register Team", command=self.register_team).pack(pady=5)
        tk.Button(root, text="Register Individual", command=self.register_individual).pack(pady=5)
        tk.Button(root, text="Start Match", command=self.start_match).pack(pady=5)
        tk.Button(root, text="Display Scores", command=self.display_scores).pack(pady=5)
        tk.Button(root, text="Save and Exit", command=self.save_and_exit).pack(pady=10)

    def register_team(self):
        try:
            name = simpledialog.askstring("Team Registration", "Enter team name:")
            if not name:
                return
            members_input = simpledialog.askstring("Team Registration", "Enter members (comma-separated):")
            if not members_input:
                return
            members = [m.strip() for m in members_input.split(",") if m.strip()]
            self.tourney.register_team(name.strip(), members)
            messagebox.showinfo("Success", f"Team '{name}' registered.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def register_individual(self):
        try:
            name = simpledialog.askstring("Individual Registration", "Enter name:")
            if not name:
                return
            self.tourney.register_individual(name.strip())
            messagebox.showinfo("Success", f"Individual '{name}' registered.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def generate_question(self):
        """Generate a random math question with +, -, *, /"""
        operators = ["+", "-", "*", "/"]
        op = random.choice(operators)

        if op == "+":
            a, b = random.randint(1, 20), random.randint(1, 20)
            return f"{a} + {b}", a + b
        elif op == "-":
            a, b = random.randint(1, 20), random.randint(1, 20)
            if b > a:
                a, b = b, a
            return f"{a} - {b}", a - b
        elif op == "*":
            a, b = random.randint(1, 12), random.randint(1, 12)
            return f"{a} × {b}", a * b
        else:  # division
            b = random.randint(1, 12)
            answer = random.randint(1, 12)
            a = b * answer
            return f"{a} ÷ {b}", answer

    def start_match(self):
        """Each side (individual or team) answers 5 questions, alternating turns"""
        try:
            p1 = simpledialog.askstring("Match Setup", "Enter first participant (team or individual):")
            p2 = simpledialog.askstring("Match Setup", "Enter second participant (team or individual):")
            if not p1 or not p2:
                return

            # Prevent team vs individual
            if (p1 in self.tourney.teams and p2 in self.tourney.individuals) or \
               (p2 in self.tourney.teams and p1 in self.tourney.individuals):
                messagebox.showerror("Error", "Team vs Individual matches are not allowed.")
                return

            if (p1 not in self.tourney.teams and p1 not in self.tourney.individuals) or \
               (p2 not in self.tourney.teams and p2 not in self.tourney.individuals):
                messagebox.showerror("Error", "One or both participants not found.")
                return

            num_questions_per_side = 5
            total_rounds = num_questions_per_side * 2  # because two sides alternate

            team_indices = {p1: 0, p2: 0}  # track member rotation

            for i in range(total_rounds):
                current = p1 if i % 2 == 0 else p2
                question, correct = self.generate_question()

                # If it's a team
                if current in self.tourney.teams:
                    team = self.tourney.teams[current]
                    members = team["members"]
                    member = members[team_indices[current] % len(members)]
                    team_indices[current] += 1

                    ans = simpledialog.askinteger("Quiz", f"{member['name']} ({current}), Q{i+1}: {question} = ?")
                    if ans == correct:
                        member["score"] += 10
                        team["total_score"] += 10
                        messagebox.showinfo("Correct!", f"{member['name']} ({current}): Correct! +10 points")
                    else:
                        messagebox.showinfo("Incorrect", f"{member['name']} ({current}): Wrong! The correct answer was {correct}")

                # If it's an individual
                else:
                    ans = simpledialog.askinteger("Quiz", f"{current}, Q{i+1}: {question} = ?")
                    if ans == correct:
                        self.tourney.individuals[current] += 10
                        messagebox.showinfo("Correct!", f"{current}: Correct! +10 points")
                    else:
                        messagebox.showinfo("Incorrect", f"{current}: Wrong! The correct answer was {correct}")

            # Show updated scores
            self.display_scores()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def display_scores(self):
        scores = self.tourney.get_scores()
        messagebox.showinfo("Current Scores", scores)

    def save_and_exit(self):
        self.tourney.save_data()
        messagebox.showinfo("Saved", "Tournament data saved.")
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = TournamentApp(root)
    root.mainloop()
