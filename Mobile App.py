from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
import sqlite3
from kivy.graphics import Color, Rectangle


class WorkoutApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = sqlite3.connect("workouts.db")
        self.c = self.db.cursor()

    def grab_exercises(self, selected_exercises):
        # Exercises categories
        array = ["Chest_Exercises", "Shoulder_Exercises", "Bicep_Exercises", "Triceps_Exercises", 
                 "Leg_Exercises", "Back_Exercises", "Glute_Exercises", "Ab_Exercises", 
                 "Calves_Exercises", "Grip_Exercises", "Cardio_Exercises"]

        exercises = []

        for i in array:
            if selected_exercises == i:
                self.c.execute(f"SELECT * FROM {i}")
                data = self.c.fetchall()
                exercises = [row[1] for row in data]  # Assuming exercise names are in the second column
                break

        return exercises

    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=5)

        with self.layout.canvas.before:
            Color(0.9, 0.9, 0.9, 1)  # Light gray background color
            self.rect = Rectangle(size=self.layout.size, pos=self.layout.pos)
        self.layout.bind(size=self._update_rect, pos=self._update_rect)

        # "Create Workout" button
        create_button = Button(text="Create Workout", size_hint=(1, None), height=40)
        create_button.bind(on_press=self.create_workout_screen)
        self.layout.add_widget(create_button)

        # "View Workouts" button
        view_button = Button(text="View Workouts", size_hint=(1, None), height=40)
        view_button.bind(on_press=self.view_workouts_screen)
        self.layout.add_widget(view_button)

        return self.layout
    
    def _update_rect(self, instance, value):
        # This method ensures the background rectangle resizes when the layout size changes
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def create_workout_screen(self, instance):
        self.layout.clear_widgets()

        # List to store the input fields for the 5 exercises
        self.exercise_inputs = []

        # Create a ScrollView for the exercise inputs
        scroll_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        scroll_layout.bind(minimum_height=scroll_layout.setter('height'))

        # Create 5 sections for exercises
        for i in range(5):
            exercise_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=180, spacing=5)

            # Spinner for selecting exercise category
            category_spinner = Spinner(
                text="Select Category",
                values=("Chest", "Shoulders", "Biceps", "Triceps", "Leg", "Back", "Glutes", "Ab", "Calves", "Grip", "Cardio"),
                size_hint=(1, None),
                height=40
            )
            category_spinner.bind(text=lambda spinner, text, i=i: self.update_exercises_spinner(i, text))
            exercise_layout.add_widget(category_spinner)

            # Spinner for selecting exercise
            exercise_spinner = Spinner(
                text="Select Exercise",
                values=[],
                size_hint=(1, None),
                height=40
            )
            exercise_layout.add_widget(exercise_spinner)

            # Input fields for sets and reps
            sets_input = TextInput(hint_text="Sets", multiline=False, size_hint=(1, None), height=40)
            reps_input = TextInput(hint_text="Reps", multiline=False, size_hint=(1, None), height=40)

            exercise_layout.add_widget(sets_input)
            exercise_layout.add_widget(reps_input)

            # Store the inputs for later use
            self.exercise_inputs.append((category_spinner, exercise_spinner, sets_input, reps_input))

            scroll_layout.add_widget(exercise_layout)

        # Add the scroll layout to the main layout
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(scroll_layout)
        self.layout.add_widget(scroll_view)

        # Save button
        save_button = Button(text="Save Workout", size_hint=(1, None), height=40)
        save_button.bind(on_press=self.save_workout)
        self.layout.add_widget(save_button)

        # Back button to return to the main screen
        back_button = Button(text="Back to Main Menu", size_hint=(1, None), height=40)
        back_button.bind(on_press=self.return_to_main_screen)
        self.layout.add_widget(back_button)

    def update_exercises_spinner(self, i, text):
        # Use the selected category to fetch exercises and update the exercises spinner
        exercises = self.grab_exercises(f"{text}_Exercises")
        self.exercise_inputs[i][1].values = exercises if exercises else ["No exercises available"]

    def save_workout(self, instance):
    # Get input data for each exercise
        exercises_data = []

        for category_spinner, exercise_spinner, sets_input, reps_input in self.exercise_inputs:
            exercise_name = exercise_spinner.text
            sets = sets_input.text
            reps = reps_input.text

            # Check if exercise, sets, and reps are filled
            if not exercise_name or not sets or not reps:
                self.show_error("All fields must be filled!")
                return

            # Check if sets and reps are numbers
            if not sets.isdigit() or not reps.isdigit():
                self.show_error("Sets and Reps must be numbers!")
                return

            # Append valid data
            exercises_data.append((exercise_name, int(sets), int(reps)))

        # If all fields are valid, save to the database
        if exercises_data:
            #for exercise_name, sets, reps in exercises_data:
            self.c.execute("""INSERT INTO workouts (exercise_name1, sets1, reps1,
                           exercise_name2, sets2, reps2,
                           exercise_name3, sets3, reps3,
                           exercise_name4, sets4, reps4,
                           exercise_name5, sets5, reps5) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,? ,?)""",
                            (exercises_data[0][0], exercises_data[0][1], exercises_data[0][2],
                            exercises_data[1][0], exercises_data[1][1], exercises_data[1][2],
                            exercises_data[2][0], exercises_data[2][1], exercises_data[2][2],
                            exercises_data[3][0], exercises_data[3][1], exercises_data[3][2],
                            exercises_data[4][0], exercises_data[4][1], exercises_data[4][2],))
            
            self.db.commit()  # Commit the changes

            # Clear inputs after saving
            for category_spinner, exercise_spinner, sets_input, reps_input in self.exercise_inputs:
                sets_input.text = ""
                reps_input.text = ""
                exercise_spinner.text = "Select Exercise"

            # Confirmation message
            self.show_error("Workout saved successfully!")

    def show_error(self, message):
        # Simple method to show a popup message for errors
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        error_popup = Popup(title="Error", content=Label(text=message),
                            size_hint=(None, None), size=(400, 200))
        error_popup.open()

    def view_workouts_screen(self, instance):
        # Clear the layout
        self.layout.clear_widgets()

        # ScrollView for displaying workouts
        self.workouts_display = ScrollView(size_hint=(1, 1))
        self.layout.add_widget(self.workouts_display)

        # Fetch workouts from database using the existing cursor (self.c)
        self.c.execute("SELECT * FROM workouts")
        workouts = self.c.fetchall()

        # Create a container layout for displaying multiple workouts
        workout_container = BoxLayout(orientation='vertical', size_hint_y=None)
        workout_container.bind(minimum_height=workout_container.setter('height'))

        # Display each workout in the ScrollView
        for workout in workouts:
            # Initialize display text for the current workout
            display_text = f"ID: {workout[0]}\n"
            
            # Assuming each workout contains: (id, exercise_name, sets, reps, and possibly more)
            for i in range(1, len(workout)):
                # Formatting the display text depending on the workout fields
                if ((i) % 3) == 0:  # Every 3rd field could be reps
                    display_text += f"Reps: {workout[i]}\n"
                elif ((i) % 2) == 0:  # Every 2nd field could be sets
                    display_text += f"Sets: {workout[i]} "
                else:
                    display_text += f"Exercise: {workout[i]} "
            
            # Create a label to display the formatted workout information
            display_label = Label(text=display_text, size_hint_y=None, height=200)
            workout_container.add_widget(display_label)

        # Add the workout container to the ScrollView
        self.workouts_display.add_widget(workout_container)

        # Back button to return to the main screen
        back_button = Button(text="Back to Main Menu", size_hint=(1, None), height=40)
        back_button.bind(on_press=self.return_to_main_screen)
        self.layout.add_widget(back_button)

    def return_to_main_screen(self, instance):
        # Returning to main menu (clear screen and show the main options again)
        self.layout.clear_widgets()
        self.layout.add_widget(Button(text="Create Workout", size_hint=(1, None), height=40, on_press=self.create_workout_screen))
        self.layout.add_widget(Button(text="View Workouts", size_hint=(1, None), height=40, on_press=self.view_workouts_screen))


    def on_stop(self):
        # Commit and close the database connection when the app is exited
        self.db.commit()
        self.db.close()


# Run the app
if __name__ == "__main__":
    WorkoutApp().run()
