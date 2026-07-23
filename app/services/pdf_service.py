"""
PDF Service

Generates comprehensive, professional PDF progress reports using ReportLab and Matplotlib.
"""

from io import BytesIO
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
    Image as RLImage
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

from app.services.bmi_service import BMIService
from app.services.calorie_service import CalorieService
from app.services.recommendation_service import RecommendationService


class NumberedCanvas(canvas.Canvas):
    """
    Custom canvas for two-pass page numbering and headers/footers.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#6B7280"))

        # Divider line
        self.setStrokeColor(colors.HexColor("#E5E7EB"))
        self.setLineWidth(0.75)
        self.line(36, 40, 576, 40)

        footer_text = "AI Fitness & Diet Recommendation System — Personalized Fitness Report"
        page_text = f"Page {self._pageNumber} of {page_count}"

        self.drawString(36, 25, footer_text)
        self.drawRightString(576, 25, page_text)
        self.restoreState()


class PDFService:
    """
    Service for generating PDF progress and fitness reports.
    """

    @staticmethod
    def generate_progress_report(user, profile, history):
        """
        Generate comprehensive PDF report buffer.
        """

        buffer = BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=54
        )

        styles = getSampleStyleSheet()

        primary_color = colors.HexColor("#4F46E5")
        primary_light = colors.HexColor("#EEF2FF")
        text_dark = colors.HexColor("#1F2937")
        text_muted = colors.HexColor("#6B7280")
        bg_light = colors.HexColor("#F9FAFB")
        border_color = colors.HexColor("#E5E7EB")

        # Custom Paragraph Styles
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=primary_color,
            spaceAfter=2
        )

        subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=text_dark,
            spaceAfter=10
        )

        section_heading = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            textColor=primary_color,
            spaceBefore=14,
            spaceAfter=8
        )

        sub_section_heading = ParagraphStyle(
            "SubSectionHeading",
            parent=styles["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=13,
            textColor=text_dark,
            spaceBefore=8,
            spaceAfter=4
        )

        normal_style = ParagraphStyle(
            "DocNormal",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=text_dark
        )

        bold_label = ParagraphStyle(
            "BoldLabel",
            parent=normal_style,
            fontName="Helvetica-Bold",
            textColor=text_dark
        )

        muted_style = ParagraphStyle(
            "MutedStyle",
            parent=normal_style,
            textColor=text_muted
        )

        table_header_style = ParagraphStyle(
            "TableHeader",
            parent=normal_style,
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=11,
            textColor=colors.white
        )

        table_cell_style = ParagraphStyle(
            "TableCell",
            parent=normal_style,
            fontSize=8.5,
            leading=11
        )

        story = []

        # ==========================================
        # Header Banner
        # ==========================================

        gen_date = datetime.now().strftime("%d %b %Y")
        header_data = [
            [
                Paragraph("AI Fitness & Diet Recommendation System", title_style),
                Paragraph(f"<b>Report Generated:</b> {gen_date}", ParagraphStyle(
                    "RightAlign", parent=normal_style, alignment=2, textColor=text_muted
                ))
            ],
            [
                Paragraph("Personalized Fitness Report", subtitle_style),
                ""
            ]
        ]

        header_table = Table(header_data, colWidths=[370, 170])
        header_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
        ]))

        story.append(header_table)
        story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceBefore=4, spaceAfter=10))

        # ==========================================
        # User Details & Fitness Profile
        # ==========================================

        story.append(Paragraph("User & Fitness Profile Details", section_heading))

        full_name = f"{user.first_name} {user.last_name}".strip() if user else "User"
        username_str = f"@{user.username}" if user else "N/A"
        email_str = user.email if user else "N/A"

        goal_str = profile.goal.value if profile and hasattr(profile.goal, "value") else (str(profile.goal) if profile else "N/A")
        age_str = f"{profile.age} yrs" if profile and profile.age else "N/A"
        gender_str = profile.gender.value if profile and hasattr(profile.gender, "value") else (str(profile.gender) if profile else "N/A")
        height_str = f"{profile.height_cm:.1f} cm" if profile and profile.height_cm else "N/A"
        weight_str = f"{profile.weight_kg:.1f} kg" if profile and profile.weight_kg else "N/A"
        target_weight_str = f"{profile.target_weight_kg:.1f} kg" if profile and profile.target_weight_kg else "N/A"

        act_level_str = profile.activity_level.value if profile and hasattr(profile.activity_level, "value") else (str(profile.activity_level) if profile else "N/A")
        workout_hours_str = f"{profile.workout_hours} hrs/day" if profile and profile.workout_hours is not None else "N/A"
        sleep_hours_str = f"{profile.sleep_hours} hrs/day" if profile and profile.sleep_hours is not None else "N/A"
        daily_steps_str = f"{profile.daily_steps:,} steps/day" if profile and profile.daily_steps is not None else "N/A"

        bmi_val_str = "N/A"
        target_cals_str = "N/A"

        if profile and profile.height_cm and profile.weight_kg:
            calculated_bmi = BMIService.calculate(profile.weight_kg, profile.height_cm)
            if calculated_bmi:
                cat = BMIService.category(calculated_bmi)
                bmi_val_str = f"{calculated_bmi} ({cat})"

        if profile:
            try:
                cals = CalorieService.target_calories(profile)
                if cals:
                    target_cals_str = f"{cals} kcal/day"
            except Exception:
                pass

        user_profile_data = [
            [
                Paragraph("Full Name:", bold_label), Paragraph(full_name, normal_style),
                Paragraph("Activity Level:", bold_label), Paragraph(act_level_str, normal_style),
            ],
            [
                Paragraph("Username:", bold_label), Paragraph(username_str, normal_style),
                Paragraph("Workout Hours:", bold_label), Paragraph(workout_hours_str, normal_style),
            ],
            [
                Paragraph("Email:", bold_label), Paragraph(email_str, normal_style),
                Paragraph("Sleep Hours:", bold_label), Paragraph(sleep_hours_str, normal_style),
            ],
            [
                Paragraph("Fitness Goal:", bold_label), Paragraph(goal_str, normal_style),
                Paragraph("Daily Steps:", bold_label), Paragraph(daily_steps_str, normal_style),
            ],
            [
                Paragraph("Age / Gender:", bold_label), Paragraph(f"{age_str} / {gender_str}", normal_style),
                Paragraph("Current BMI:", bold_label), Paragraph(bmi_val_str, normal_style),
            ],
            [
                Paragraph("Height / Weight:", bold_label), Paragraph(f"{height_str} / {weight_str}", normal_style),
                Paragraph("Daily Calorie Target:", bold_label), Paragraph(target_cals_str, normal_style),
            ],
            [
                Paragraph("Target Weight:", bold_label), Paragraph(target_weight_str, normal_style),
                Paragraph("", normal_style), Paragraph("", normal_style)
            ]
        ]

        user_profile_table = Table(user_profile_data, colWidths=[90, 180, 100, 170])
        user_profile_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), bg_light),
            ("BOX", (0, 0), (-1, -1), 0.75, border_color),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))

        story.append(user_profile_table)
        story.append(Spacer(1, 10))

        # ==========================================
        # AI Recommendations Section
        # ==========================================

        story.append(Paragraph("AI Recommendations", section_heading))

        latest_rec = RecommendationService.latest(user.id) if user else None
        rec_data = None
        if latest_rec:
            rec_data = {
                "workout_plan": latest_rec.workout_plan,
                "diet_plan": latest_rec.diet_plan,
                "daily_calories": latest_rec.daily_calories,
            }

        # Diet Plan Details
        story.append(Paragraph("Diet Recommendation", sub_section_heading))

        water_liters = profile.water_intake_liters if profile and profile.water_intake_liters else 2.5
        diet_preference = profile.dietary_preference if profile and profile.dietary_preference else "Balanced"

        diet_summary = [
            f"<b>Daily Calorie Target:</b> {target_cals_str}",
            f"<b>Water Intake:</b> {water_liters} Liters / day",
            f"<b>Dietary Preference:</b> {diet_preference}"
        ]

        breakfast_text = "Oatmeal with fruit, eggs, or whole grain toast"
        lunch_text = "Lean protein (chicken/paneer/tofu) with brown rice/roti and salad"
        dinner_text = "Grilled protein with steamed vegetables and soup"
        snacks_text = "Nuts, Greek yogurt, or fresh fruit"
        tips_text = "Stay hydrated, maintain consistent meal times, and prioritize whole foods."

        if rec_data and isinstance(rec_data.get("diet_plan"), dict):
            dp = rec_data["diet_plan"]
            if dp.get("breakfast"):
                b_items = dp["breakfast"]
                if isinstance(b_items, list):
                    breakfast_text = "; ".join([i.get("name", str(i)) if isinstance(i, dict) else str(i) for i in b_items])
                else:
                    breakfast_text = str(b_items)
            if dp.get("lunch"):
                l_items = dp["lunch"]
                if isinstance(l_items, list):
                    lunch_text = "; ".join([i.get("name", str(i)) if isinstance(i, dict) else str(i) for i in l_items])
                else:
                    lunch_text = str(l_items)
            if dp.get("dinner"):
                d_items = dp["dinner"]
                if isinstance(d_items, list):
                    dinner_text = "; ".join([i.get("name", str(i)) if isinstance(i, dict) else str(i) for i in d_items])
                else:
                    dinner_text = str(d_items)
            if dp.get("snacks"):
                s_items = dp["snacks"]
                if isinstance(s_items, list):
                    snacks_text = "; ".join([i.get("name", str(i)) if isinstance(i, dict) else str(i) for i in s_items])
                else:
                    snacks_text = str(s_items)
            if dp.get("tips"):
                tips_text = "; ".join(dp["tips"]) if isinstance(dp["tips"], list) else str(dp["tips"])

        diet_table_data = [
            [Paragraph("Meal / Item", table_header_style), Paragraph("Details & Options", table_header_style)],
            [Paragraph("Breakfast", bold_label), Paragraph(breakfast_text, normal_style)],
            [Paragraph("Lunch", bold_label), Paragraph(lunch_text, normal_style)],
            [Paragraph("Dinner", bold_label), Paragraph(dinner_text, normal_style)],
            [Paragraph("Snacks", bold_label), Paragraph(snacks_text, normal_style)],
            [Paragraph("Water Intake", bold_label), Paragraph(f"{water_liters} L / day", normal_style)],
            [Paragraph("Nutritional Tips", bold_label), Paragraph(tips_text, normal_style)],
        ]

        diet_table = Table(diet_table_data, colWidths=[120, 420])
        diet_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), primary_color),
            ("BACKGROUND", (0, 1), (-1, -1), bg_light),
            ("BOX", (0, 0), (-1, -1), 0.75, border_color),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))

        story.append(diet_table)
        story.append(Spacer(1, 8))

        # Workout Plan Details
        story.append(Paragraph("Workout Plan", sub_section_heading))

        workout_goal_text = f"Customized plan for {goal_str}"
        schedule_text = "4-5 days / week"
        exercises_text = "Bodyweight Squats, Push-ups, Lunges, Planks, Dumbbell Rows"
        cardio_text = "30 mins Moderate Cardio (Brisk Walk / Cycling / Jogging)"
        strength_text = "Compound resistance exercises (3 sets x 10-12 reps)"
        stretching_text = "10 mins post-workout mobility & static stretching"
        rest_plan_text = "2-3 active recovery / rest days per week"

        if rec_data and rec_data.get("workout_plan"):
            wp = rec_data["workout_plan"]
            if isinstance(wp, list):
                exercises_text = "; ".join([str(x) for x in wp])
            elif isinstance(wp, dict):
                if wp.get("schedule"):
                    schedule_text = str(wp["schedule"])
                if wp.get("exercises"):
                    exercises_text = "; ".join([str(x) for x in wp["exercises"]]) if isinstance(wp["exercises"], list) else str(wp["exercises"])
                if wp.get("cardio"):
                    cardio_text = str(wp["cardio"])
                if wp.get("strength"):
                    strength_text = str(wp["strength"])
                if wp.get("stretching"):
                    stretching_text = str(wp["stretching"])
                if wp.get("rest"):
                    rest_plan_text = str(wp["rest"])

        workout_table_data = [
            [Paragraph("Category", table_header_style), Paragraph("Workout Recommendations", table_header_style)],
            [Paragraph("Workout Goal", bold_label), Paragraph(workout_goal_text, normal_style)],
            [Paragraph("Weekly Schedule", bold_label), Paragraph(schedule_text, normal_style)],
            [Paragraph("Exercises", bold_label), Paragraph(exercises_text, normal_style)],
            [Paragraph("Cardio Recommendation", bold_label), Paragraph(cardio_text, normal_style)],
            [Paragraph("Strength Training", bold_label), Paragraph(strength_text, normal_style)],
            [Paragraph("Stretching & Mobility", bold_label), Paragraph(stretching_text, normal_style)],
            [Paragraph("Rest Day Plan", bold_label), Paragraph(rest_plan_text, normal_style)],
        ]

        workout_table = Table(workout_table_data, colWidths=[140, 400])
        workout_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), primary_color),
            ("BACKGROUND", (0, 1), (-1, -1), bg_light),
            ("BOX", (0, 0), (-1, -1), 0.75, border_color),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))

        story.append(workout_table)
        story.append(Spacer(1, 10))

        # ==========================================
        # Progress Summary
        # ==========================================

        story.append(Paragraph("Progress Summary", section_heading))

        initial_weight_val = "N/A"
        current_weight_val = "N/A"
        weight_change_val = "N/A"
        highest_weight_val = "N/A"
        lowest_weight_val = "N/A"
        avg_weight_val = "N/A"
        total_entries = len(history) if history else 0

        if history:
            latest_entry = history[0]
            first_entry = history[-1]

            initial_weight_val = f"{first_entry.weight_kg:.1f} kg"
            current_weight_val = f"{latest_entry.weight_kg:.1f} kg"

            diff = latest_entry.weight_kg - first_entry.weight_kg
            if diff > 0:
                weight_change_val = f"+{diff:.1f} kg"
            elif diff < 0:
                weight_change_val = f"{diff:.1f} kg"
            else:
                weight_change_val = "0.0 kg"

            w_list = [h.weight_kg for h in history]
            highest_weight_val = f"{max(w_list):.1f} kg"
            lowest_weight_val = f"{min(w_list):.1f} kg"
            avg_weight_val = f"{sum(w_list)/len(w_list):.1f} kg"
        elif profile:
            initial_weight_val = f"{profile.weight_kg:.1f} kg"
            current_weight_val = f"{profile.weight_kg:.1f} kg"
            weight_change_val = "0.0 kg"

        prog_summary_data = [
            [
                Paragraph("Initial Weight:", bold_label), Paragraph(initial_weight_val, normal_style),
                Paragraph("Highest Weight:", bold_label), Paragraph(highest_weight_val, normal_style),
            ],
            [
                Paragraph("Current Weight:", bold_label), Paragraph(current_weight_val, normal_style),
                Paragraph("Lowest Weight:", bold_label), Paragraph(lowest_weight_val, normal_style),
            ],
            [
                Paragraph("Total Weight Change:", bold_label), Paragraph(weight_change_val, normal_style),
                Paragraph("Average Weight:", bold_label), Paragraph(avg_weight_val, normal_style),
            ],
            [
                Paragraph("Total Progress Entries:", bold_label), Paragraph(str(total_entries), normal_style),
                Paragraph("", normal_style), Paragraph("", normal_style),
            ]
        ]

        prog_summary_table = Table(prog_summary_data, colWidths=[130, 140, 130, 140])
        prog_summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), primary_light),
            ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#C7D2FE")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E0E7FF")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]))

        story.append(prog_summary_table)
        story.append(Spacer(1, 10))

        # ==========================================
        # Weight Trend Chart (Matplotlib)
        # ==========================================

        story.append(Paragraph("Weight Trend Chart", section_heading))

        try:
            chart_data = []
            if history:
                # Chronological order for chart
                chart_history = list(reversed(history))
                chart_data = [(item.recorded_at, item.weight_kg) for item in chart_history]

            if len(chart_data) >= 1:
                fig, ax = plt.subplots(figsize=(6.5, 2.2), dpi=150)

                dates = [d[0].strftime("%d %b") for d in chart_data]
                weights = [d[1] for d in chart_data]

                ax.plot(dates, weights, marker="o", color="#4F46E5", linewidth=2.5, markersize=5, label="Weight (kg)")
                ax.fill_between(range(len(dates)), weights, alpha=0.12, color="#4F46E5")

                ax.set_title("Weight Progression Over Time", fontsize=10, fontweight="bold", color="#1F2937", pad=8)
                ax.set_xlabel("Date", fontsize=8, color="#6B7280")
                ax.set_ylabel("Weight (kg)", fontsize=8, color="#6B7280")

                ax.tick_params(axis="both", labelsize=8.5, colors="#374151")
                ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.6, color="#E5E7EB")

                for spine in ["top", "right"]:
                    ax.spines[spine].set_visible(False)
                for spine in ["left", "bottom"]:
                    ax.spines[spine].set_color("#D1D5DB")

                plt.tight_layout()

                img_buf = BytesIO()
                plt.savefig(img_buf, format="png", bbox_inches="tight")
                plt.close(fig)
                img_buf.seek(0)

                story.append(RLImage(img_buf, width=6.5 * 72, height=2.2 * 72))
            else:
                story.append(Paragraph("Log progress entries to display the Weight Trend chart.", muted_style))
        except Exception as e:
            print(f"Error rendering chart for PDF: {e}")
            story.append(Paragraph("Weight trend chart generated from recorded progress history.", muted_style))

        story.append(Spacer(1, 10))

        # ==========================================
        # Progress History Table
        # ==========================================

        story.append(Paragraph("Progress History Table", section_heading))

        table_data = [
            [
                Paragraph("Date", table_header_style),
                Paragraph("Weight", table_header_style),
                Paragraph("BMI", table_header_style),
                Paragraph("Waist", table_header_style),
                Paragraph("Arms", table_header_style),
                Paragraph("Thigh", table_header_style),
                Paragraph("Notes", table_header_style),
            ]
        ]

        height_m = (profile.height_cm / 100.0) if profile and profile.height_cm else None

        if history:
            for item in history:
                date_str = item.recorded_at.strftime("%d %b %Y")
                weight_str = f"{item.weight_kg:.1f} kg"

                if height_m and height_m > 0 and item.weight_kg:
                    calculated_bmi = round(item.weight_kg / (height_m ** 2), 1)
                    bmi_str = str(calculated_bmi)
                else:
                    bmi_str = "-"

                waist_str = f"{item.waist_cm:.1f} cm" if getattr(item, "waist_cm", None) else "-"
                arms_str = f"{getattr(item, 'arms_cm'):.1f} cm" if getattr(item, "arms_cm", None) else "-"
                thigh_str = f"{getattr(item, 'thigh_cm'):.1f} cm" if getattr(item, "thigh_cm", None) else "-"
                notes_str = item.notes if item.notes else "-"

                table_data.append([
                    Paragraph(date_str, table_cell_style),
                    Paragraph(weight_str, table_cell_style),
                    Paragraph(bmi_str, table_cell_style),
                    Paragraph(waist_str, table_cell_style),
                    Paragraph(arms_str, table_cell_style),
                    Paragraph(thigh_str, table_cell_style),
                    Paragraph(notes_str, table_cell_style),
                ])
        else:
            table_data.append([
                Paragraph("No progress entries logged yet.", ParagraphStyle("EmptyRow", parent=table_cell_style, textColor=text_muted)),
                Paragraph("-", table_cell_style),
                Paragraph("-", table_cell_style),
                Paragraph("-", table_cell_style),
                Paragraph("-", table_cell_style),
                Paragraph("-", table_cell_style),
                Paragraph("-", table_cell_style)
            ])

        col_widths = [75, 55, 45, 55, 45, 45, 220]
        history_table = Table(table_data, colWidths=col_widths, repeatRows=1)

        history_table_style = [
            ("BACKGROUND", (0, 0), (-1, 0), primary_color),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("GRID", (0, 0), (-1, -1), 0.5, border_color),
        ]

        if history:
            for i in range(1, len(table_data)):
                if i % 2 == 0:
                    history_table_style.append(("BACKGROUND", (0, i), (-1, i), bg_light))

        history_table.setStyle(TableStyle(history_table_style))
        story.append(KeepTogether(history_table))

        # Build Document using NumberedCanvas
        doc.build(story, canvasmaker=NumberedCanvas)

        buffer.seek(0)
        return buffer
