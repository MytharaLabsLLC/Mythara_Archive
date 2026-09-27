# Copyright © 2025 Herbert Velez Jr. All rights reserved.

"""
MytharaTutor - Age-Appropriate STEAM Syllabi
Complete Curriculum Framework for All Age Groups

Includes:
- Structured lesson plans for Elementary, Middle School, High School, College, Adult
- Video learning integration (YouTube Kids, PBS, Khan Academy, TED-Ed, etc.)
- Leadership development activities
- Innovation projects
- STEAM focus with real-world applications
- Guidance-informed age-appropriate content (not medical advice)
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta


class MytharaSyllabus:
    """
    Age-appropriate STEAM syllabi with video learning integration
    
    Focus: Developing future leaders and creative innovators
    """
    
    @staticmethod
    def get_elementary_syllabus() -> Dict[str, Any]:
        """
        ELEMENTARY (Ages 8-12) - Foundation Building
        
        Session Time: 45 minutes max (medical guidelines)
        Video Learning: 15-20 minutes per session
        Interactive Practice: 15-20 minutes
        Projects: 10 minutes
        
        Focus: Wonder, curiosity, hands-on exploration
        """
        return {
            "age_group": "Elementary (Ages 8-12)",
            "session_duration_minutes": 45,
            "video_time_minutes": "15-20",
            "sessions_per_week": "3-4",
            "course_duration_weeks": 12,
            
            "learning_objectives": [
                "Develop curiosity about how the world works",
                "Build foundational STEAM concepts through play",
                "Learn basic problem-solving and critical thinking",
                "Create simple projects to express ideas",
                "Develop collaboration and communication skills"
            ],
            
            "week_by_week_plan": [
                {
                    "week": 1,
                    "theme": "Introduction to STEAM - What is Science?",
                    "video_resources": [
                        {
                            "platform": "PBS Kids",
                            "title": "What is Science? - SciGirls",
                            "duration_min": 12,
                            "learning_goal": "Understand scientific method basics"
                        },
                        {
                            "platform": "YouTube Kids",
                            "title": "Science for Kids - Observable Universe",
                            "duration_min": 8,
                            "learning_goal": "Explore curiosity about nature"
                        }
                    ],
                    "interactive_activities": [
                        "Simple observation experiment (plant growth)",
                        "Draw what you learned from videos",
                        "Ask 3 questions about science"
                    ],
                    "leadership_skill": "Curiosity",
                    "homework": "Find 5 examples of science in your home"
                },
                {
                    "week": 2,
                    "theme": "Technology Around Us - How Computers Think",
                    "video_resources": [
                        {
                            "platform": "Code.org",
                            "title": "How Computers Work: Circuits & Logic",
                            "duration_min": 10,
                            "learning_goal": "Understand binary and basic computing"
                        },
                        {
                            "platform": "Khan Academy Kids",
                            "title": "Introduction to Coding",
                            "duration_min": 15,
                            "learning_goal": "Learn sequencing and algorithms"
                        }
                    ],
                    "interactive_activities": [
                        "Scratch Jr coding blocks (simple animation)",
                        "Binary number game (0s and 1s)",
                        "Algorithm for making a sandwich"
                    ],
                    "leadership_skill": "Problem Solving",
                    "homework": "Create a simple Scratch story"
                },
                {
                    "week": 3,
                    "theme": "Engineering - Building Strong Structures",
                    "video_resources": [
                        {
                            "platform": "PBS LearningMedia",
                            "title": "Design Squad: Bridge Challenge",
                            "duration_min": 12,
                            "learning_goal": "Learn about structural engineering"
                        },
                        {
                            "platform": "YouTube Kids",
                            "title": "How Bridges Are Built",
                            "duration_min": 8,
                            "learning_goal": "Understand forces and structures"
                        }
                    ],
                    "interactive_activities": [
                        "Build a bridge with popsicle sticks",
                        "Test bridge strength with weights",
                        "Redesign to make it stronger"
                    ],
                    "leadership_skill": "Resilience",
                    "innovation_project": "Design a treehouse with drawings"
                },
                {
                    "week": 4,
                    "theme": "Arts - Creative Expression & Design",
                    "video_resources": [
                        {
                            "platform": "PBS Kids",
                            "title": "Art Explorers: Color Theory",
                            "duration_min": 10,
                            "learning_goal": "Understand primary and secondary colors"
                        },
                        {
                            "platform": "YouTube Kids",
                            "title": "How Animation Works",
                            "duration_min": 12,
                            "learning_goal": "Learn about visual storytelling"
                        }
                    ],
                    "interactive_activities": [
                        "Create a color wheel",
                        "Draw a short comic strip",
                        "Design a poster about your favorite topic"
                    ],
                    "leadership_skill": "Creativity",
                    "homework": "Illustrate a story about solving a problem"
                },
                {
                    "week": 5,
                    "theme": "Mathematics - Patterns & Numbers in Nature",
                    "video_resources": [
                        {
                            "platform": "Khan Academy Kids",
                            "title": "Patterns in Math and Nature",
                            "duration_min": 10,
                            "learning_goal": "Recognize mathematical patterns"
                        },
                        {
                            "platform": "National Geographic Kids",
                            "title": "Fibonacci Sequence in Nature",
                            "duration_min": 8,
                            "learning_goal": "See math in the real world"
                        }
                    ],
                    "interactive_activities": [
                        "Find patterns in nature (leaves, flowers)",
                        "Create your own pattern with shapes",
                        "Practice skip counting (2s, 5s, 10s)"
                    ],
                    "leadership_skill": "Critical Thinking",
                    "homework": "Find 3 patterns at home and photograph them"
                },
                {
                    "week": 6,
                    "theme": "Environmental Science - Taking Care of Our Planet",
                    "video_resources": [
                        {
                            "platform": "PBS Kids",
                            "title": "Plum Landing: Habitat Exploration",
                            "duration_min": 12,
                            "learning_goal": "Understand ecosystems"
                        },
                        {
                            "platform": "National Geographic Kids",
                            "title": "Reducing Plastic Pollution",
                            "duration_min": 10,
                            "learning_goal": "Learn about environmental impact"
                        }
                    ],
                    "interactive_activities": [
                        "Create a recycling sorting game",
                        "Design an eco-friendly product",
                        "Start a small garden or care for a plant"
                    ],
                    "leadership_skill": "Global Citizenship",
                    "innovation_project": "Invent a solution to reduce waste at school"
                },
                {
                    "week": 7,
                    "theme": "Space Science - Exploring the Solar System",
                    "video_resources": [
                        {
                            "platform": "NASA Kids Club",
                            "title": "Tour of the Solar System",
                            "duration_min": 15,
                            "learning_goal": "Learn about planets and stars"
                        },
                        {
                            "platform": "YouTube Kids",
                            "title": "How Rockets Work",
                            "duration_min": 10,
                            "learning_goal": "Understand propulsion basics"
                        }
                    ],
                    "interactive_activities": [
                        "Build a model solar system",
                        "Paper rocket launch experiment",
                        "Draw an alien ecosystem on another planet"
                    ],
                    "leadership_skill": "Imagination",
                    "homework": "Research one planet and create a fact sheet"
                },
                {
                    "week": 8,
                    "theme": "Robotics - Introduction to Machines",
                    "video_resources": [
                        {
                            "platform": "PBS LearningMedia",
                            "title": "Simple Machines Explained",
                            "duration_min": 10,
                            "learning_goal": "Understand levers, pulleys, wheels"
                        },
                        {
                            "platform": "YouTube Kids",
                            "title": "How Robots Help People",
                            "duration_min": 12,
                            "learning_goal": "Learn about robotics applications"
                        }
                    ],
                    "interactive_activities": [
                        "Build a simple lever with household items",
                        "Design a robot that solves a problem",
                        "Program a virtual robot (Code.org)",
                    ],
                    "leadership_skill": "Innovation",
                    "homework": "Find 5 simple machines in your home"
                },
                {
                    "week": 9,
                    "theme": "Music & Sound - Science of Vibrations",
                    "video_resources": [
                        {
                            "platform": "PBS Kids",
                            "title": "Soundtastic: How Sound Works",
                            "duration_min": 10,
                            "learning_goal": "Understand sound waves and vibrations"
                        },
                        {
                            "platform": "YouTube Kids",
                            "title": "Making Music with Science",
                            "duration_min": 8,
                            "learning_goal": "Connect physics to music"
                        }
                    ],
                    "interactive_activities": [
                        "Build a simple instrument (rubber band guitar)",
                        "Experiment with pitch and volume",
                        "Compose a short melody"
                    ],
                    "leadership_skill": "Creativity",
                    "homework": "Record sounds from nature and identify patterns"
                },
                {
                    "week": 10,
                    "theme": "Biology - How Our Bodies Work",
                    "video_resources": [
                        {
                            "platform": "PBS Kids",
                            "title": "Sid the Science Kid: My Body",
                            "duration_min": 12,
                            "learning_goal": "Learn about human body systems"
                        },
                        {
                            "platform": "Khan Academy Kids",
                            "title": "How Your Heart Works",
                            "duration_min": 8,
                            "learning_goal": "Understand circulatory system"
                        }
                    ],
                    "interactive_activities": [
                        "Measure your heartbeat before/after exercise",
                        "Create a life-size body diagram",
                        "Learn about nutrition and healthy choices"
                    ],
                    "leadership_skill": "Self-Awareness",
                    "homework": "Track your healthy habits for a week"
                },
                {
                    "week": 11,
                    "theme": "Communication & Collaboration",
                    "video_resources": [
                        {
                            "platform": "PBS Kids",
                            "title": "Arthur: Working Together",
                            "duration_min": 12,
                            "learning_goal": "Learn teamwork skills"
                        },
                        {
                            "platform": "YouTube Kids",
                            "title": "How to Present Your Ideas",
                            "duration_min": 10,
                            "learning_goal": "Develop communication skills"
                        }
                    ],
                    "interactive_activities": [
                        "Team challenge: build tallest tower with limited materials",
                        "Practice explaining a concept to a friend",
                        "Create a presentation about your favorite topic"
                    ],
                    "leadership_skill": "Collaboration",
                    "homework": "Interview a family member about their job"
                },
                {
                    "week": 12,
                    "theme": "Final Innovation Project - Change the World!",
                    "video_resources": [
                        {
                            "platform": "TED-Ed",
                            "title": "Kid Inventors Who Changed the World",
                            "duration_min": 10,
                            "learning_goal": "Be inspired by young innovators"
                        },
                        {
                            "platform": "YouTube Kids",
                            "title": "Design Thinking for Kids",
                            "duration_min": 12,
                            "learning_goal": "Learn problem-solving process"
                        }
                    ],
                    "interactive_activities": [
                        "Identify a problem in your community",
                        "Design a solution (draw, prototype)",
                        "Present your invention to class/family"
                    ],
                    "leadership_skill": "Innovation",
                    "final_project": "Create and present a world-changing invention"
                }
            ],
            
            "video_platforms": [
                "PBS Kids",
                "YouTube Kids (filtered, age-appropriate)",
                "Khan Academy Kids",
                "National Geographic Kids",
                "NASA Kids Club",
                "Code.org",
                "Scratch Jr"
            ],
            
            "assessment_methods": [
                "Portfolio of projects and drawings",
                "Verbal explanations of concepts",
                "Collaborative project success",
                "Parent feedback on engagement",
                "Self-reflection: What did you learn? What was fun?"
            ],
            
            "parental_involvement": [
                "Weekly email summaries of topics covered",
                "Suggested family activities to reinforce learning",
                "Parent-child discussion prompts",
                "Monthly progress reports with video engagement metrics"
            ],
            
            "safety_guidelines": [
                "Maximum 45-minute sessions (mental health)",
                "Required breaks every 20 minutes",
                "Parent consent for all video content",
                "Filtered, age-appropriate platforms only",
                "Soul Cradle monitoring for frustration",
                "Immediate escalation if distress detected"
            ]
        }
    
    @staticmethod
    def get_middle_school_syllabus() -> Dict[str, Any]:
        """
        MIDDLE SCHOOL (Ages 13-14) - Skill Development
        
        Session Time: 60 minutes (medical guidelines)
        Video Learning: 20-25 minutes per session
        Interactive Practice: 25-30 minutes
        Projects: 10-15 minutes
        
        Focus: Critical thinking, deeper exploration, peer collaboration
        """
        return {
            "age_group": "Middle School (Ages 13-14)",
            "session_duration_minutes": 60,
            "video_time_minutes": "20-25",
            "sessions_per_week": "4-5",
            "course_duration_weeks": 16,
            
            "learning_objectives": [
                "Develop critical thinking and analytical skills",
                "Master foundational STEAM concepts",
                "Complete complex, multi-step projects",
                "Collaborate effectively in teams",
                "Begin exploring career interests in STEAM",
                "Develop leadership and communication skills"
            ],
            
            "semester_plan": [
                {
                    "unit": 1,
                    "weeks": "1-4",
                    "theme": "Computer Science & Coding Fundamentals",
                    "video_platforms": ["Khan Academy", "Code.org", "Crash Course Computer Science"],
                    "topics": [
                        "Week 1: Introduction to Python - Variables & Data Types",
                        "Week 2: Control Flow - If/Else, Loops",
                        "Week 3: Functions & Modular Programming",
                        "Week 4: Lists, Dictionaries, Basic Data Structures"
                    ],
                    "video_schedule": [
                        {"week": 1, "videos": ["Khan Academy: Python Basics (15min)", "Code.org: Why Programming Matters (10min)"]},
                        {"week": 2, "videos": ["Khan Academy: Conditionals (12min)", "Practical examples (10min)"]},
                        {"week": 3, "videos": ["Khan Academy: Functions (15min)", "Real-world coding examples (10min)"]},
                        {"week": 4, "videos": ["Data structures explained (15min)", "Python lists tutorial (10min)"]}
                    ],
                    "projects": [
                        "Week 2: Calculator program",
                        "Week 3: Mad Libs game with functions",
                        "Week 4: Contact list manager"
                    ],
                    "innovation_challenge": "Create an app idea that solves a school problem",
                    "leadership_skills": ["Problem Solving", "Critical Thinking", "Creativity"]
                },
                {
                    "unit": 2,
                    "weeks": "5-8",
                    "theme": "Biology & Life Sciences",
                    "video_platforms": ["PBS LearningMedia", "Crash Course Biology", "TED-Ed"],
                    "topics": [
                        "Week 5: Cell Structure & Function",
                        "Week 6: Genetics & DNA",
                        "Week 7: Ecosystems & Food Webs",
                        "Week 8: Evolution & Adaptation"
                    ],
                    "video_schedule": [
                        {"week": 5, "videos": ["Crash Course: Cell Biology (12min)", "3D cell animation (8min)"]},
                        {"week": 6, "videos": ["TED-Ed: How DNA Works (10min)", "CRISPR explained (12min)"]},
                        {"week": 7, "videos": ["PBS: Ecosystem dynamics (15min)", "Food chain visualization (8min)"]},
                        {"week": 8, "videos": ["Crash Course: Evolution (12min)", "Natural selection examples (10min)"]}
                    ],
                    "projects": [
                        "Week 5: 3D cell model",
                        "Week 6: DNA extraction lab (at home with strawberries)",
                        "Week 7: Design a sustainable ecosystem",
                        "Week 8: Research an endangered species adaptation"
                    ],
                    "innovation_challenge": "Design a biotechnology solution for conservation",
                    "leadership_skills": ["Global Citizenship", "Ethical Reasoning", "Systems Thinking"]
                },
                {
                    "unit": 3,
                    "weeks": "9-12",
                    "theme": "Physics & Engineering Design",
                    "video_platforms": ["Khan Academy", "Veritasium", "Physics Girl", "Mark Rober"],
                    "topics": [
                        "Week 9: Newton's Laws of Motion",
                        "Week 10: Energy, Work, & Power",
                        "Week 11: Simple Machines & Mechanical Advantage",
                        "Week 12: Engineering Design Process"
                    ],
                    "video_schedule": [
                        {"week": 9, "videos": ["Khan Academy: Newton's Laws (15min)", "Physics demos (10min)"]},
                        {"week": 10, "videos": ["Energy explained (12min)", "Renewable energy tour (12min)"]},
                        {"week": 11, "videos": ["Simple machines (10min)", "Real-world engineering (15min)"]},
                        {"week": 12, "videos": ["Mark Rober: Engineering process (15min)", "Design thinking for teens (10min)"]}
                    ],
                    "projects": [
                        "Week 9: Egg drop challenge (protect egg from fall)",
                        "Week 10: Build a solar oven",
                        "Week 11: Rube Goldberg machine",
                        "Week 12: Design & prototype a helpful device"
                    ],
                    "innovation_challenge": "Engineer a device to help people with disabilities",
                    "leadership_skills": ["Innovation", "Resilience", "Collaboration"]
                },
                {
                    "unit": 4,
                    "weeks": "13-16",
                    "theme": "Mathematics & Data Science",
                    "video_platforms": ["Khan Academy", "3Blue1Brown", "TED-Ed"],
                    "topics": [
                        "Week 13: Algebraic Thinking & Equations",
                        "Week 14: Geometry & Spatial Reasoning",
                        "Week 15: Statistics & Data Visualization",
                        "Week 16: Introduction to Data Science"
                    ],
                    "video_schedule": [
                        {"week": 13, "videos": ["Khan Academy: Algebra fundamentals (15min)", "Real-world equations (10min)"]},
                        {"week": 14, "videos": ["3Blue1Brown: Geometry intuition (12min)", "Architecture & geometry (10min)"]},
                        {"week": 15, "videos": ["Statistics basics (15min)", "How data tells stories (10min)"]},
                        {"week": 16, "videos": ["TED-Ed: Big Data (12min)", "Data science for social good (12min)"]}
                    ],
                    "projects": [
                        "Week 13: Solve real-world problems with algebra",
                        "Week 14: Design a building using geometric principles",
                        "Week 15: Survey classmates, analyze & visualize data",
                        "Week 16: Final project: Use data to solve community problem"
                    ],
                    "innovation_challenge": "Use data to identify and address a social issue",
                    "leadership_skills": ["Critical Thinking", "Communication", "Digital Literacy"]
                }
            ],
            
            "video_platforms": [
                "Khan Academy",
                "Code.org",
                "Crash Course (all subjects)",
                "TED-Ed",
                "PBS LearningMedia",
                "Veritasium",
                "3Blue1Brown",
                "Mark Rober",
                "Physics Girl",
                "National Geographic"
            ],
            
            "assessment_methods": [
                "Project-based assessments (70%)",
                "Quizzes on key concepts (20%)",
                "Peer collaboration evaluations (10%)",
                "Video comprehension checks",
                "Self-reflection journals",
                "Leadership skill development tracking"
            ],
            
            "leadership_development": [
                "Monthly team projects requiring role assignments",
                "Peer teaching opportunities (explain concepts to classmates)",
                "Public speaking practice (project presentations)",
                "Critical thinking debates on STEAM ethics",
                "Community service projects using STEAM skills"
            ],
            
            "parental_involvement": [
                "Bi-weekly progress reports",
                "Access to student project portfolio",
                "Video watch history and engagement metrics",
                "Parent-teacher virtual conferences (quarterly)",
                "Suggested family STEAM activities"
            ]
        }
    
    @staticmethod
    def get_high_school_syllabus() -> Dict[str, Any]:
        """
        HIGH SCHOOL (Ages 15-17) - Mastery & College Prep
        
        Session Time: 90 minutes (medical guidelines)
        Video Learning: 25-30 minutes per session
        Interactive Practice: 40-45 minutes
        Projects: 15-20 minutes
        
        Focus: Mastery, college prep, career exploration, world-changing projects
        """
        return {
            "age_group": "High School (Ages 15-17)",
            "session_duration_minutes": 90,
            "video_time_minutes": "25-30",
            "sessions_per_week": "5-6",
            "course_duration_weeks": 18,
            
            "learning_objectives": [
                "Achieve mastery in chosen STEAM domains",
                "Prepare for AP exams and standardized tests (SAT/ACT)",
                "Complete capstone innovation project with real-world impact",
                "Develop college-level research and writing skills",
                "Build professional portfolio for college applications",
                "Cultivate leadership through mentoring younger students"
            ],
            
            "semester_plan": [
                {
                    "track": "Computer Science & AI",
                    "weeks": "1-6",
                    "college_prep_focus": "AP Computer Science Principles",
                    "video_platforms": ["MIT OpenCourseWare", "Stanford Online", "TED", "Two Minute Papers"],
                    "curriculum": [
                        "Week 1-2: Advanced Python - OOP, Classes, Inheritance",
                        "Week 3-4: Data Structures & Algorithms",
                        "Week 5-6: Introduction to Machine Learning & AI Ethics"
                    ],
                    "video_integration": [
                        "MIT: Object-Oriented Programming (30min/week)",
                        "Stanford: Algorithms explained (25min/week)",
                        "TED: AI Ethics and Society (20min)",
                        "Two Minute Papers: Latest ML research (10min/week)"
                    ],
                    "projects": [
                        "Build a personal portfolio website",
                        "Create an AI chatbot for mental health support",
                        "Analyze social media data to identify trends"
                    ],
                    "innovation_project": "Develop an AI tool to address educational equity",
                    "college_prep": [
                        "SAT/ACT practice problems",
                        "College essay brainstorming: STEAM passion",
                        "Portfolio building for computer science programs"
                    ]
                },
                {
                    "track": "Engineering & Robotics",
                    "weeks": "7-12",
                    "college_prep_focus": "AP Physics + Engineering Portfolio",
                    "video_platforms": ["MIT OpenCourseWare", "Khan Academy", "Veritasium", "Simone Giertz"],
                    "curriculum": [
                        "Week 7-8: Advanced Physics - Mechanics & Dynamics",
                        "Week 9-10: Electronics & Circuit Design",
                        "Week 11-12: Robotics Programming & Control Systems"
                    ],
                    "video_integration": [
                        "MIT: Classical Mechanics (30min/week)",
                        "Khan Academy: AP Physics review (25min/week)",
                        "Veritasium: Engineering concepts (20min)",
                        "Robot competitions & innovation (15min)"
                    ],
                    "projects": [
                        "Design & build an Arduino-based robot",
                        "Create a renewable energy prototype",
                        "Engineer a solution for accessibility"
                    ],
                    "innovation_project": "Build a robot to assist elderly or disabled individuals",
                    "college_prep": [
                        "AP Physics practice exams",
                        "Engineering school essay prompts",
                        "Research university robotics labs"
                    ]
                },
                {
                    "track": "Biotechnology & Health Sciences",
                    "weeks": "13-18",
                    "college_prep_focus": "AP Biology + Pre-Med Track",
                    "video_platforms": ["Khan Academy", "NIH", "TED-Med", "Osmosis"],
                    "curriculum": [
                        "Week 13-14: Molecular Biology & Genetics",
                        "Week 15-16: Biochemistry & Cellular Processes",
                        "Week 17-18: Biomedical Engineering & Innovation"
                    ],
                    "video_integration": [
                        "Khan Academy: AP Biology (30min/week)",
                        "NIH: Cutting-edge research (20min/week)",
                        "TED-Med: Healthcare innovation (25min)",
                        "Osmosis: Medical concepts (15min/week)"
                    ],
                    "projects": [
                        "Gene expression lab (virtual simulation)",
                        "Design a public health intervention",
                        "Research paper on biotech ethics"
                    ],
                    "innovation_project": "Develop a low-cost medical device for developing countries",
                    "college_prep": [
                        "AP Biology practice tests",
                        "Pre-med essay writing",
                        "Volunteer at local health clinics"
                    ]
                }
            ],
            
            "college_prep_components": {
                "standardized_test_prep": {
                    "sat_prep": [
                        "Weekly practice sections (Math, Reading, Writing)",
                        "Video lessons from Khan Academy SAT prep",
                        "Full-length practice tests (monthly)",
                        "Personalized weak area focus"
                    ],
                    "act_prep": [
                        "Subject-specific practice",
                        "Timing strategies",
                        "Science reasoning skills"
                    ],
                    "ap_exam_prep": [
                        "AP Computer Science Principles",
                        "AP Biology",
                        "AP Physics",
                        "AP Calculus AB/BC",
                        "AP Statistics"
                    ]
                },
                "college_essay_coaching": {
                    "weeks": "Throughout semester",
                    "video_resources": [
                        "College Essay Guy tutorials",
                        "TED: How to tell your story",
                        "Admissions officers panel discussions"
                    ],
                    "activities": [
                        "Brainstorm unique STEAM experiences",
                        "Draft personal statement",
                        "Peer review workshops",
                        "Revision with mentor feedback"
                    ]
                },
                "portfolio_development": {
                    "components": [
                        "GitHub repository of coding projects",
                        "Research paper or capstone project",
                        "Leadership activities log",
                        "Community service documentation",
                        "Awards and recognition"
                    ]
                }
            },
            
            "leadership_development": [
                "Mentor elementary/middle school students",
                "Lead STEAM club or start new initiative",
                "Present research at science fairs",
                "Organize hackathon or STEAM competition",
                "Participate in Model UN or debate",
                "Intern at STEAM company or research lab"
            ],
            
            "innovation_capstone": {
                "description": "Year-long project to create world-changing innovation",
                "phases": [
                    "Identify global problem (UN SDGs alignment)",
                    "Research existing solutions",
                    "Design innovative approach",
                    "Build prototype or conduct research",
                    "Test with real users",
                    "Present findings at science fair/competition",
                    "Publish results or start non-profit"
                ],
                "video_documentation": [
                    "Pitch video (3 minutes)",
                    "Demo video (5 minutes)",
                    "Final presentation (10 minutes)"
                ],
                "examples": [
                    "AI-powered water quality monitoring system",
                    "Low-cost prosthetic limb using 3D printing",
                    "App connecting food waste with food insecurity",
                    "Solar-powered device for clean cooking",
                    "Mental health chatbot for teens"
                ]
            },
            
            "video_platforms": [
                "MIT OpenCourseWare",
                "Stanford Online",
                "Khan Academy (SAT/AP prep)",
                "TED / TED-Ed / TED-Med",
                "Crash Course (college-level)",
                "3Blue1Brown (advanced math)",
                "Two Minute Papers (AI research)",
                "Veritasium (physics)",
                "NIH (biomedical research)",
                "Coursera (audit college courses)"
            ],
            
            "assessment_methods": [
                "AP-style exams (40%)",
                "Capstone innovation project (30%)",
                "Research paper or portfolio (20%)",
                "Leadership & collaboration (10%)",
                "Video engagement and comprehension",
                "Standardized test scores (tracking improvement)"
            ]
        }
    
    @staticmethod
    def get_college_syllabus() -> Dict[str, Any]:
        """
        COLLEGE (Ages 18-22) - Professional Development
        
        Session Time: 120 minutes (self-directed)
        Video Learning: 30-40 minutes per session
        Project Work: 60-70 minutes
        Collaboration: 20-30 minutes
        
        Focus: Professional skills, career preparation, entrepreneurship
        """
        return {
            "age_group": "College (Ages 18-22)",
            "session_duration_minutes": 120,
            "video_time_minutes": "30-40",
            "sessions_per_week": "Self-paced (recommended 6-8)",
            "course_duration_weeks": 16,
            
            "learning_objectives": [
                "Master advanced STEAM concepts at professional level",
                "Build career-ready portfolio and professional network",
                "Contribute to open-source or research projects",
                "Develop entrepreneurial mindset and business skills",
                "Publish research or launch startup",
                "Prepare for graduate school or industry career"
            ],
            
            "specialization_tracks": [
                {
                    "track": "Software Engineering & Full-Stack Development",
                    "career_prep": "Tech industry roles (FAANG, startups)",
                    "video_platforms": ["MIT OpenCourseWare", "freeCodeCamp", "Fireship", "Tech with Tim"],
                    "curriculum": [
                        "Advanced algorithms and data structures",
                        "System design and architecture",
                        "Web development (React, Node.js, databases)",
                        "DevOps and cloud computing (AWS, Docker)",
                        "Software engineering best practices"
                    ],
                    "video_integration": [
                        "MIT: Advanced algorithms (40min/week)",
                        "freeCodeCamp: Full-stack tutorials (60min/week)",
                        "System design interviews (30min/week)",
                        "Tech conference talks (20min/week)"
                    ],
                    "projects": [
                        "Build full-stack web application",
                        "Contribute to open-source project (GitHub)",
                        "Create portfolio website with blog",
                        "Develop mobile app (React Native or Flutter)"
                    ],
                    "career_activities": [
                        "LeetCode/HackerRank practice (daily)",
                        "Mock technical interviews",
                        "Attend hackathons",
                        "Network on LinkedIn",
                        "Apply for internships at tech companies"
                    ]
                },
                {
                    "track": "Data Science & Machine Learning",
                    "career_prep": "Data scientist, ML engineer, AI researcher",
                    "video_platforms": ["Stanford Online", "DeepLearning.AI", "Kaggle", "StatQuest"],
                    "curriculum": [
                        "Statistics and probability for ML",
                        "Machine learning algorithms",
                        "Deep learning and neural networks",
                        "Natural language processing",
                        "Computer vision"
                    ],
                    "video_integration": [
                        "Stanford: Machine Learning (40min/week)",
                        "DeepLearning.AI: Deep learning specialization (60min/week)",
                        "Kaggle: Competition walkthroughs (30min/week)",
                        "Research paper reviews (20min/week)"
                    ],
                    "projects": [
                        "Kaggle competition entry",
                        "Build recommendation system",
                        "NLP chatbot or sentiment analysis",
                        "Computer vision project (object detection)",
                        "Publish research paper or blog post"
                    ],
                    "career_activities": [
                        "Complete Kaggle competitions",
                        "Contribute to ML open-source libraries",
                        "Attend AI conferences (virtual)",
                        "Join data science communities",
                        "Internship at AI lab or company"
                    ]
                },
                {
                    "track": "Entrepreneurship & Startup Founder",
                    "career_prep": "Launch own company or join early-stage startup",
                    "video_platforms": ["Y Combinator", "TED", "Harvard Business School Online", "a16z"],
                    "curriculum": [
                        "Lean startup methodology",
                        "Product-market fit and customer discovery",
                        "Fundraising and pitch deck creation",
                        "Growth hacking and marketing",
                        "Team building and leadership"
                    ],
                    "video_integration": [
                        "Y Combinator: Startup School (40min/week)",
                        "TED: Entrepreneurship stories (20min/week)",
                        "a16z podcast episodes (30min/week)",
                        "Founder interviews (20min/week)"
                    ],
                    "projects": [
                        "Identify problem worth solving",
                        "Conduct customer interviews (100+)",
                        "Build MVP (minimum viable product)",
                        "Launch beta and get users",
                        "Pitch to accelerators or investors"
                    ],
                    "career_activities": [
                        "Apply to Y Combinator, Techstars, etc.",
                        "Network with founders and investors",
                        "Attend startup events and pitch competitions",
                        "Build product and iterate based on feedback",
                        "Consider crowdfunding or grants"
                    ]
                }
            ],
            
            "professional_skills": {
                "technical_interview_prep": [
                    "Data structures and algorithms practice (LeetCode)",
                    "System design case studies",
                    "Behavioral interview frameworks (STAR method)",
                    "Salary negotiation strategies"
                ],
                "networking": [
                    "LinkedIn optimization",
                    "Attend virtual conferences",
                    "Informational interviews with professionals",
                    "Join Slack communities in your field",
                    "Contribute to online forums (Stack Overflow, Reddit)"
                ],
                "portfolio_building": [
                    "GitHub profile showcase",
                    "Personal website/blog",
                    "Case studies of major projects",
                    "Video demos and presentations",
                    "Testimonials and recommendations"
                ],
                "soft_skills": [
                    "Communication and presentation",
                    "Teamwork and collaboration",
                    "Project management (Agile/Scrum)",
                    "Leadership and mentorship",
                    "Time management and productivity"
                ]
            },
            
            "video_platforms": [
                "MIT OpenCourseWare",
                "Stanford Online",
                "Harvard Business School Online",
                "Y Combinator Startup School",
                "DeepLearning.AI",
                "freeCodeCamp",
                "Coursera (full courses)",
                "edX",
                "Udacity",
                "Kaggle Learn",
                "TED Talks",
                "Tech conference recordings (Strange Loop, PyCon, etc.)",
                "Company engineering blogs (Google, Netflix, Airbnb)"
            ],
            
            "assessment_methods": [
                "Portfolio quality and completeness (40%)",
                "Technical project complexity (30%)",
                "Professional network growth (15%)",
                "Career readiness (interviews, offers) (15%)",
                "Video learning engagement metrics",
                "Peer code reviews and feedback"
            ],
            
            "graduate_school_prep": {
                "for_phd_track": [
                    "Undergraduate research opportunities",
                    "Publish papers or present at conferences",
                    "GRE preparation",
                    "Statement of purpose writing",
                    "Professor recommendations",
                    "Research fit with potential advisors"
                ],
                "for_masters": [
                    "GRE preparation",
                    "Strong GPA and relevant coursework",
                    "Industry experience or internships",
                    "Clear career goals in statement"
                ]
            }
        }
    
    @staticmethod
    def get_adult_syllabus() -> Dict[str, Any]:
        """
        ADULT (Ages 23+) - Lifelong Learning & Career Advancement
        
        Session Time: Flexible (self-directed)
        Video Learning: 30-45 minutes per session
        Project Work: 60-90 minutes
        
        Focus: Career transitions, upskilling, entrepreneurship, passion projects
        """
        return {
            "age_group": "Adult (Ages 23+)",
            "session_duration_minutes": "Flexible (60-180min)",
            "video_time_minutes": "30-45",
            "sessions_per_week": "Self-paced (3-10 based on goals)",
            "course_duration_weeks": "Varies by goal (4-24 weeks)",
            
            "learning_objectives": [
                "Career transition or advancement in STEAM",
                "Launch side business or startup",
                "Complete passion project or creative work",
                "Stay current with industry trends",
                "Contribute to community through STEAM skills",
                "Achieve work-life balance through lifelong learning"
            ],
            
            "learning_paths": [
                {
                    "path": "Career Changer - Breaking into Tech",
                    "duration_weeks": 24,
                    "video_platforms": ["freeCodeCamp", "Scrimba", "Fireship", "CS Dojo"],
                    "curriculum": [
                        "Phase 1 (Weeks 1-8): Fundamentals",
                        "  - HTML/CSS/JavaScript basics",
                        "  - Git and version control",
                        "  - Command line proficiency",
                        "  - Basic algorithms and problem-solving",
                        "Phase 2 (Weeks 9-16): Specialization",
                        "  - Frontend (React) OR Backend (Node.js/Python)",
                        "  - Databases (SQL and NoSQL)",
                        "  - API development",
                        "  - Testing and debugging",
                        "Phase 3 (Weeks 17-24): Job Ready",
                        "  - Build 3-5 portfolio projects",
                        "  - LeetCode interview practice",
                        "  - Resume and LinkedIn optimization",
                        "  - Networking and job applications"
                    ],
                    "video_integration": [
                        "freeCodeCamp: Full courses (2-3 hours/week)",
                        "Scrimba: Interactive tutorials (1 hour/week)",
                        "Fireship: Quick tech overviews (30min/week)",
                        "Tech interview prep videos (1 hour/week)"
                    ],
                    "projects": [
                        "Personal portfolio website",
                        "E-commerce site or web app",
                        "API-based project (weather app, etc.)",
                        "Full-stack CRUD application",
                        "Capstone project of your choice"
                    ],
                    "success_metrics": [
                        "Complete 100+ LeetCode problems",
                        "Build 5 portfolio-quality projects",
                        "Network with 50+ people in tech",
                        "Apply to 100+ jobs",
                        "Land first tech role within 6 months"
                    ]
                },
                {
                    "path": "Entrepreneur - Launch Your Startup",
                    "duration_weeks": 16,
                    "video_platforms": ["Y Combinator", "Indie Hackers", "TED", "MicroConf"],
                    "curriculum": [
                        "Weeks 1-4: Idea Validation",
                        "  - Problem identification",
                        "  - Customer interviews (50-100)",
                        "  - Competitive analysis",
                        "  - Lean canvas creation",
                        "Weeks 5-8: MVP Development",
                        "  - No-code tools (Bubble, Webflow) OR Code",
                        "  - Landing page creation",
                        "  - Early user acquisition",
                        "  - Feedback loops",
                        "Weeks 9-12: Growth & Iteration",
                        "  - Product-market fit testing",
                        "  - Growth experiments",
                        "  - Pricing strategy",
                        "  - Marketing channels",
                        "Weeks 13-16: Scale or Pivot",
                        "  - Fundraising prep (if applicable)",
                        "  - Team building",
                        "  - Unit economics",
                        "  - Pitch deck creation"
                    ],
                    "video_integration": [
                        "Y Combinator: Startup advice (1 hour/week)",
                        "Indie Hackers: Founder stories (30min/week)",
                        "MicroConf: Bootstrap strategies (45min/week)",
                        "TED: Entrepreneurship inspiration (20min/week)"
                    ],
                    "milestones": [
                        "Week 4: Validated problem with customer interviews",
                        "Week 8: MVP launched with 10 users",
                        "Week 12: 100+ users and product-market fit signals",
                        "Week 16: $1K MRR or fundraising traction"
                    ]
                },
                {
                    "path": "Professional Upskilling - AI & Machine Learning",
                    "duration_weeks": 20,
                    "video_platforms": ["DeepLearning.AI", "fast.ai", "Lex Fridman Podcast", "Two Minute Papers"],
                    "curriculum": [
                        "Weeks 1-5: Foundations",
                        "  - Python for data science",
                        "  - Statistics and linear algebra review",
                        "  - Pandas and NumPy",
                        "  - Data visualization",
                        "Weeks 6-10: Classical ML",
                        "  - Supervised learning algorithms",
                        "  - Unsupervised learning",
                        "  - Model evaluation and tuning",
                        "  - Kaggle competitions",
                        "Weeks 11-15: Deep Learning",
                        "  - Neural networks fundamentals",
                        "  - CNNs for computer vision",
                        "  - RNNs and NLP",
                        "  - Transfer learning",
                        "Weeks 16-20: Specialization",
                        "  - Choose: NLP, Computer Vision, or Reinforcement Learning",
                        "  - Capstone project",
                        "  - Deploy model to production"
                    ],
                    "video_integration": [
                        "DeepLearning.AI: Courses (2-3 hours/week)",
                        "fast.ai: Practical deep learning (1.5 hours/week)",
                        "Lex Fridman: AI researcher interviews (1 hour/week)",
                        "Two Minute Papers: Latest research (30min/week)"
                    ],
                    "projects": [
                        "Kaggle competition top 25% finish",
                        "Image classification model",
                        "NLP sentiment analysis or chatbot",
                        "Recommendation system",
                        "Deploy ML model as web service"
                    ]
                },
                {
                    "path": "Creative Innovator - Art + Technology",
                    "duration_weeks": 12,
                    "video_platforms": ["Domestika", "Skillshare", "Processing Foundation", "Creative Coding"],
                    "curriculum": [
                        "Weeks 1-4: Digital Art Tools",
                        "  - Adobe Creative Suite OR Open source alternatives",
                        "  - Digital illustration",
                        "  - Photo manipulation",
                        "  - Video editing basics",
                        "Weeks 5-8: Creative Coding",
                        "  - Processing or p5.js",
                        "  - Generative art",
                        "  - Data visualization as art",
                        "  - Interactive installations",
                        "Weeks 9-12: Capstone Exhibition",
                        "  - Develop unique art-tech project",
                        "  - Document process",
                        "  - Create online exhibition",
                        "  - Share on social media and art platforms"
                    ],
                    "video_integration": [
                        "Domestika: Design courses (2 hours/week)",
                        "Skillshare: Creative tutorials (1 hour/week)",
                        "Creative coding channels (1 hour/week)",
                        "Artist talks and interviews (30min/week)"
                    ],
                    "projects": [
                        "Design personal brand identity",
                        "Create generative art series",
                        "Build interactive data visualization",
                        "Produce short film or animation",
                        "Host online art exhibition"
                    ]
                }
            ],
            
            "video_platforms": [
                "YouTube (all topics, free)",
                "Coursera (professional certificates)",
                "Udemy (affordable courses on sale)",
                "LinkedIn Learning",
                "Skillshare (creative skills)",
                "Domestika (art & design)",
                "freeCodeCamp (coding)",
                "Khan Academy (fundamentals)",
                "TED / TED-Ed (inspiration)",
                "Company blogs & conference talks",
                "Podcasts (Lex Fridman, Indie Hackers, etc.)"
            ],
            
            "success_factors": [
                "Clear goal setting (SMART goals)",
                "Consistent learning schedule (even 30min/day)",
                "Accountability (learning buddy or community)",
                "Building in public (share progress)",
                "Networking (LinkedIn, Twitter, communities)",
                "Balance (avoid burnout, enjoy process)"
            ],
            
            "assessment_methods": [
                "Achievement of stated career or project goal",
                "Portfolio quality and completeness",
                "Professional network growth",
                "Income or career advancement",
                "Personal satisfaction and fulfillment",
                "Community contributions (teaching, mentoring, open source)"
            ],
            
            "work_life_balance": [
                "Flexible scheduling around work/family",
                "Micro-learning (15-30 min sessions)",
                "Weekend deep dives (2-4 hours)",
                "Pomodoro technique for focus",
                "Family-friendly projects (involve kids)",
                "Self-care and mental health breaks"
            ]
        }
    
    @staticmethod
    def get_all_syllabi() -> Dict[str, Dict[str, Any]]:
        """Get complete syllabus collection for all age groups"""
        return {
            "elementary": MytharaSyllabus.get_elementary_syllabus(),
            "middle_school": MytharaSyllabus.get_middle_school_syllabus(),
            "high_school": MytharaSyllabus.get_high_school_syllabus(),
            "college": MytharaSyllabus.get_college_syllabus(),
            "adult": MytharaSyllabus.get_adult_syllabus()
        }


def main():
    """Demo: Display sample syllabus information"""
    print("\n" + "="*80)
    print("    MYTHARA TUTOR - AGE-APPROPRIATE STEAM SYLLABI")
    print("    Complete Curriculum with Video Learning Integration")
    print("="*80 + "\n")
    
    syllabi = MytharaSyllabus.get_all_syllabi()
    
    for age_group, syllabus in syllabi.items():
        print(f"\n{'='*80}")
        print(f"  {syllabus['age_group'].upper()}")
        print(f"{'='*80}")
        print(f"\n📚 Session Duration: {syllabus['session_duration_minutes']} minutes")
        print(f"🎥 Video Learning Time: {syllabus['video_time_minutes']} minutes")
        print(f"📅 Sessions per Week: {syllabus['sessions_per_week']}")
        
        if 'learning_objectives' in syllabus:
            print(f"\n🎯 Learning Objectives:")
            for obj in syllabus['learning_objectives'][:3]:
                print(f"   • {obj}")
        
        if 'video_platforms' in syllabus:
            print(f"\n🎥 Video Platforms:")
            platforms = syllabus['video_platforms'][:5]
            print(f"   {', '.join(platforms)}")
            if len(syllabus['video_platforms']) > 5:
                print(f"   ... and {len(syllabus['video_platforms']) - 5} more")
    
    print(f"\n\n{'='*80}")
    print("  MYTHARA TUTOR SYLLABI - COMPLETE")
    print(f"{'='*80}")
    print("\n✅ All age groups covered with:")
    print("   ✓ Age-appropriate session times (medical guidelines)")
    print("   ✓ Integrated video learning (YouTube Kids, PBS, Khan Academy, MIT, etc.)")
    print("   ✓ Leadership development activities")
    print("   ✓ Innovation projects for world impact")
    print("   ✓ College prep for high school students")
    print("   ✓ Career advancement for adults")
    print("\n🌟 Focus: Developing tomorrow's leaders and creative innovators")
    print("🌍 Mission: Keep the world alive through STEAM education\n")


if __name__ == "__main__":
    main()
